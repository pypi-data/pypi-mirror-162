#!python

import os
import re
import sys
import json
import yaml
import time
import yaxil
import fcntl
import errno
import arrow
import atexit
import socket
import shutil
import signal
import logging
import nibabel as nib
import datetime as dt
import tempfile as tf
import argparse as ap
import subprocess as sp
import collections as col
import morphometry.xnat as xnat
import morphometry.greve as greve
import morphometry.freesurfer as fs
import morphometry.formats as formats
import morphometry.commons as commons
import morphometry.parsers as parsers
from morphometry.plots import Laterality
from morphometry.snapshots import Snapshotter
from morphometry.xnat.morph3 import Report

logger = logging.getLogger(__name__)

Version = ap.Namespace(
    FreeSurfer='6.0.0'
)

STEPS = [
    'sourcedata',
    'convert',
    'recon',
    'tal_qc',
    'stats',
    'euler',
    'wm-anat-snr',
    'cnr',
    'pctsurfcon',
    'parse',
    'snapshots',
    'plots',
    'reports',
    'xar'
]

yaml.SafeDumper.add_representer(col.defaultdict, yaml.representer.SafeRepresenter.represent_dict)

def main():
    parser = ap.ArgumentParser(description='FreeSurfer end-to-end pipeline')
    parser.add_argument('--input', nargs='+', default=[], 
        help='Input anatomical images')
    parser.add_argument('--xnat',
        help='XNAT download string ALIAS:PROJECT:STUDY:SESSION:SCAN')
    parser.add_argument('--output-dir', default='output', 
        help='Ouptut directory')
    parser.add_argument('--scratch-dir', 
        help='Scratch directory')
    parser.add_argument('--custom-tal-atlas',
        help='Custom normalization atlas for FreeSurfer')
    parser.add_argument('--steps', nargs='+', default=STEPS,
        help='Steps to execute')
    parser.add_argument('--no-snapshots', action='store_true',
        help='Disable snapshot generation')
    parser.add_argument('--no-hires', action='store_true',
        help='Disable FreeSurfer native high resolution support')
    parser.add_argument('--no-lock', action='store_true',
        help='Do not attempt to do any mutual exclusion')
    parser.add_argument('--force', action='store_true',
        help='Force reuse of existing output directory')
    parser.add_argument('--upload', action='store_true',
        help='Upload XAR file to XNAT')
    parser.add_argument('--debug', action='store_true',
        help='Print debugging information')
    args = parser.parse_args()

    # get start time, current working directory, and utility being called
    start = arrow.now()
    tic = time.time()
    cwd = os.getcwd()
    self_ = os.path.abspath(sys.argv[0])

    # enable debug messages and print the command currently being executed
    level = logging.DEBUG if args.debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=level, format=log_format)
    logger.info(sp.list2cmdline(sys.argv))
    logger.info('running on machine {0}'.format(socket.getfqdn()))

    # define output directories
    args.output_dir = os.path.expanduser(args.output_dir)
    morph_output_dir = os.path.join(args.output_dir, 'morphometrics')

    # create base output directory (if not present)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    else:
        # attempt mutual exclusion
        if not args.no_lock:
            mutex = os.path.join(args.output_dir, '.mutex')
            fd = os.open(mutex, os.O_RDWR|os.O_CREAT)
            try:
                fcntl.lockf(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
                logger.info('locked the mutex {0}'.format(mutex))
            except IOError as e:
                if e.errno == errno.EWOULDBLOCK:
                    logger.critical('another process has locked {0}'.format(mutex))
                    sys.exit(2)
                raise e
        # delete morph_output_dir if the user passed in --force argument
        if args.force:
            if 'recon' in args.steps and os.path.exists(morph_output_dir):
                logger.warn('about to delete {0} in 10s, press enter to continue or Ctrl+C to exit'.format(morph_output_dir))
                commons.wait_for_keypress(10)
                shutil.rmtree(morph_output_dir)
 
    # directory for saving logs
    logs_dir = os.path.join(args.output_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    if 'sourcedata' in args.steps:  
        # download files from xnat
        sourcedata = col.defaultdict(dict)
        if args.xnat:
            download_dir = os.path.abspath(os.path.join(args.output_dir, 'xnat'))
            match = parse_xnat_string(args.xnat)
            auth = yaxil.auth(match['alias'])
            with yaxil.session(auth) as ses:
                accession = ses.accession(match['session'], match['project'])
                ses.download(
                    match['session'],
                    [match['scan']],
                    project=match['project'],
                    out_dir=download_dir,
                    attempts=3
                )
            sourcedata['application/x-xnat'] = {
                'url': auth.url,
                'accession': accession,
                'project': match['project'],
                'session': match['session'],
                'scan': match['scan'],
                'output': download_dir
            }
            args.input = [download_dir]

        # take all inputs and create nifti-1 files (if necessary)
        anats = list()
        sourcedata = list()
        for input in cast_inputs(args.input):
            source = {
                'origin': os.path.abspath(str(input)),
                'converted': None
            }
            if input.mime == 'application/dicom':
                dcm_file = input.index()[0]
                base,_ = os.path.splitext(os.path.basename(dcm_file))
                dirname = os.path.join(args.output_dir, 'nifti')
                basename = '{0}.nii.gz'.format(base) # must be unique
                nifti_file = formats.NiftiGz(dirname, basename)
                id_ = 'mri_convert_{0}'.format(base)
                log_prefix = os.path.join(logs_dir, id_)
                if 'convert' in args.steps:
                    logger.info('creating %s', nifti_file)
                    mri_convert = fs.mri_convert.get(Version.FreeSurfer)
                    mri_convert(dcm_file, nifti_file, log_prefix)
                source['converted'] = str(nifti_file)
            elif input.mime == 'application/x-nifti':
                nifti_file = os.path.abspath(str(input))
            anats.append(nifti_file)
            # cache some often used information to sourcedata
            nii = nib.load(str(nifti_file))
            source['dim'] = nii.shape
            source['orientation'] = ''.join(nib.aff2axcodes(nii.affine))
            sourcedata.append(source)
            
        # save sourcedata provenance
        logfile = os.path.join(logs_dir, 'sourcedata.yml')
        with open(logfile, 'w') as fo:
            fo.write(yaml.safe_dump(sourcedata, default_flow_style=False))

    # switch output directory to (faster) scratch directory
    if args.scratch_dir:
        if not os.path.exists(args.scratch_dir):
            os.makedirs(args.scratch_dir)
        tmp_dir = tf.mkdtemp(dir=args.scratch_dir)
        morph_scratch_dir = os.path.join(tmp_dir, 'morphometrics')
        # register an atexit function to move output dir to output dir
        move_on_exit(morph_scratch_dir, morph_output_dir)
        morph_output_dir = morph_scratch_dir
    
    # run recon-all
    if 'recon' in args.steps:
        logger.info('running recon-all')
        log_prefix = os.path.join(logs_dir, 'recon_all')
        recon_all = fs.recon_all.get(Version.FreeSurfer)
        cw256 = commons.check_fov(anats)
        # motioncor = True if len(anats) > 1 else False
        motioncor = False
        submillimeter = False
        if not args.no_hires:
            submillimeter = commons.check_submillimeter(anats)
        logger.info('crop width to 256 flag is %s', cw256)
        logger.info('motion correction flag is %s', motioncor)
        logger.info('submillimeter flag is %s', submillimeter)
        recon_all(
            anats,
            morph_output_dir,
            log_prefix,
            motioncor=motioncor,
            hires=submillimeter,
            cw256=cw256,
            custom_tal_atlas=args.custom_tal_atlas
        )
    
    # run tal_QC_AZS
    if 'tal_qc' in args.steps:
        logger.info('running tal_qc_azs')
        tal_avi_log = os.path.join(morph_output_dir, 'mri', 'transforms', 'talairach_avi.log')
        log_prefix = os.path.join(logs_dir, 'tal_qc_azs')
        tal_qc_azs = fs.tal_qc_azs.get(Version.FreeSurfer)
        stdout,_ = tal_qc_azs(tal_avi_log, None, log_prefix)
        tal_qc = parsers.parse_tal_qc(stdout)
        tal_qc_json = os.path.join(morph_output_dir, 'stats', 'tal_qc_azs.json')
        logger.info('saving %s', tal_qc_json)
        with open(tal_qc_json, 'w') as fo:
            fo.write(json.dumps(tal_qc, indent=2))
   
    # run mris_anatomoical_stats on left and right hemispheres
    if 'stats' in args.steps:
        mris_anatomical_stats = fs.mris_anatomical_stats.get(Version.FreeSurfer)
        # right hemisphere
        logger.info('running mris_anatomical_stats on right hemi')
        log_prefix = os.path.join(logs_dir, 'rh.mris_anatomical_stats')
        stdout,_ = mris_anatomical_stats(morph_output_dir, None, log_prefix, hemi='rh')
        rh_stats = parsers.parse_mris_anatomical_stats(stdout)
        rh_stats_json = os.path.join(morph_output_dir, 'stats', 'rh.mris_anatomical_stats.json')
        logger.info('saving %s', rh_stats_json)
        with open(rh_stats_json, 'w') as fo:
            fo.write(json.dumps(rh_stats, indent=2))
        # left hemisphere
        logger.info('running mris_anatomical_stats on left hemi')
        log_prefix = os.path.join(logs_dir, 'lh.mris_anatomical_stats.log')
        stdout,_ = mris_anatomical_stats(morph_output_dir, None, log_prefix, hemi='lh')
        lh_stats = parsers.parse_mris_anatomical_stats(stdout)
        lh_stats_json = os.path.join(morph_output_dir, 'stats', 'lh.mris_anatomical_stats.json')
        logger.info('saving %s', lh_stats_json)
        with open(lh_stats_json, 'w') as fo:
            fo.write(json.dumps(lh_stats, indent=2))

    # run mris_anatomoical_stats on left and right hemispheres
    if 'euler' in args.steps:
        mris_euler_number = fs.mris_euler_number.get(Version.FreeSurfer)
        # right hemisphere
        logger.info('running mris_euler_number on right hemi')
        log_prefix = os.path.join(logs_dir, 'rh.mris_euler_number')
        input_file = os.path.join(morph_output_dir, 'surf', 'rh.orig.nofix')
        stdout,_ = mris_euler_number(input_file, None, log_prefix)
        rh_euler_parsed = parsers.parse_mris_euler_number(stdout)
        rh_euler_json = os.path.join(morph_output_dir, 'stats', 'rh.mris_euler_number.json')
        logger.info('saving %s', rh_euler_json)
        with open(rh_euler_json, 'w') as fo:
            fo.write(json.dumps(rh_euler_parsed, indent=2))
        # left hemisphere
        logger.info('running mris_euler_number on left hemi')
        log_prefix = os.path.join(logs_dir, 'lh.mris_euler_number')
        input_file = os.path.join(morph_output_dir, 'surf', 'lh.orig.nofix')
        stdout,_ = mris_euler_number(input_file, None, log_prefix)
        lh_euler_parsed = parsers.parse_mris_euler_number(stdout)
        lh_euler_json = os.path.join(morph_output_dir, 'stats', 'lh.mris_euler_number.json')
        logger.info('saving %s', lh_euler_json)
        with open(lh_euler_json, 'w') as fo:
            fo.write(json.dumps(lh_euler_parsed, indent=2))

    # run wm-anat-snr
    if 'wm-anat-snr' in args.steps:
        wm_anat_snr = fs.wm_anat_snr.get(Version.FreeSurfer)
        logger.info('running wm_anat_snr')
        log_prefix = os.path.join(logs_dir, 'wm_anat_snr')
        wm_anat_snr(morph_output_dir, None, log_prefix)
        output_file = os.path.join(morph_output_dir, 'stats', 'wmsnr.e3.dat')
        with open(output_file, 'rb') as fo:
            wm_anat_snr_parsed = parsers.parse_wm_anat_snr(fo.read())
        wm_anat_snr_json = os.path.join(morph_output_dir, 'stats', 'wm_anat_snr.json')
        logger.info('saving %s', wm_anat_snr_json)
        with open(wm_anat_snr_json, 'w') as fo:
            fo.write(json.dumps(wm_anat_snr_parsed, indent=2))

    # run wm-anat-snr
    if 'cnr' in args.steps:
        mri_cnr = fs.mri_cnr.get(Version.FreeSurfer)
        logger.info('running mri_cnr')
        log_prefix = os.path.join(logs_dir, 'mri_cnr')
        surf_dir = os.path.join(morph_output_dir, 'surf')
        input_file = os.path.join(morph_output_dir, 'mri', 'orig.mgz')
        stdout,_ = mri_cnr(input_file, None, log_prefix, surf_dir=surf_dir)
        mri_cnr_parsed = parsers.parse_mri_cnr(stdout)
        mri_cnr_json = os.path.join(morph_output_dir, 'stats', 'mri_cnr.json')
        logger.info('saving %s', mri_cnr_json)
        with open(mri_cnr_json, 'w') as fo:
            fo.write(json.dumps(mri_cnr_parsed, indent=2))

    # parse aseg.stats, lh.aparc.stats, and rh.aparc.stats and save in JSON format
    if 'parse' in args.steps:
        aseg_stats_file = os.path.join(morph_output_dir, 'stats', 'aseg.stats')
        aseg_stats = parsers.parse_stats_file(aseg_stats_file)
        aseg_json = os.path.join(morph_output_dir, 'stats', 'aseg.stats.json')
        with open(aseg_json, 'w') as fo:
            fo.write(json.dumps(aseg_stats, indent=2))
        lh_aparc_stats_file = os.path.join(morph_output_dir, 'stats', 'lh.aparc.stats')
        lh_aparc_stats = parsers.parse_stats_file(lh_aparc_stats_file)
        lh_aparc_json = os.path.join(morph_output_dir, 'stats', 'lh.aparc.stats.json')
        with open(lh_aparc_json, 'w') as fo:
            fo.write(json.dumps(lh_aparc_stats, indent=2))
        rh_aparc_stats_file = os.path.join(morph_output_dir, 'stats', 'rh.aparc.stats')
        rh_aparc_stats = parsers.parse_stats_file(rh_aparc_stats_file)
        rh_aparc_json = os.path.join(morph_output_dir, 'stats', 'rh.aparc.stats.json')
        with open(rh_aparc_json, 'w') as fo:
            fo.write(json.dumps(rh_aparc_stats, indent=2))

    # generate plots
    if 'plots' in args.steps:
        laterality = Laterality(
            morph_output_dir
        )
        laterality.aparc()
        laterality.aseg()

    # generate snapshots (this part can be brittle)
    if not args.no_snapshots and 'snapshots' in args.steps:
        headless = not os.environ.get('DISPLAY', False)
        snapshotter = Snapshotter(
            morph_output_dir,
            headless=headless
        )
        snapshotter.orig()
        snapshotter.brainmask()
        snapshotter.aseg()
        snapshotter.surfaces()

    # record provenance for the the current executing command
    p = commons.provenance(self_, sys.argv, cwd, tic, time.time())
    logfile = os.path.join(logs_dir, '__main__.yml')
    logger.info('saving provenance record {0}'.format(logfile))
    commons.log_provenance(p, logfile)

    # create XNAT archive (XAR)
    if 'xar' in args.steps:
        # create consolidated report file
        report = Report(morph_output_dir, logs_dir)
        r = report.build_report()
        report_file = os.path.join(morph_output_dir, 'report.yml')
        logger.info('writing report file %s', report_file)
        with open(report_file, 'w') as fo:
            fo.write(yaml.safe_dump(r, default_flow_style=False))
        # create the xnat archive
        output_file = os.path.join(args.output_dir, 'xnat.zip')
        logger.info('saving xar file %s', output_file)
        report = Report(morph_output_dir, logs_dir)
        report.build_assessment(output=output_file)
        # upload the archive to xnat
        if args.upload:
            match = parse_xnat_string(args.xnat)
            auth = yaxil.auth(match['alias'])
            with yaxil.session(auth) as ses:
                ses.storexar(output_file)

    logger.info('started %s', start.humanize())

def cast_inputs(inputs):
    ''' detect file types and wrap with a format '''
    for input in inputs:
        dirname = os.path.dirname(input)
        basename = os.path.basename(input)
        if os.path.isdir(input):
            yield formats.Dicom(dirname, basename)
        if re.match('.*\.nii\.gz', input):
            basename = os.path.basename(input)
            yield formats.NiftiGz(dirname, basename)

def move_on_exit(output_dir, move_to):
    # a closure to copy and remove output directory on atexit
    def _move_on_exit(*args):
        if (output_dir and move_to) and os.path.exists(output_dir) and (output_dir != move_to):
            logger.info('moving output directory from %s to %s', output_dir, move_to)
            shutil.copytree(output_dir, move_to)
            shutil.rmtree(output_dir)
    # closure to remove output directory on SIGTERM
    def sigterm_handler(*args):
        if os.path.exists(output_dir):
            logger.info('purging terminated job data in %s', output_dir)
            shutil.rmtree(output_dir)
    # register handlers (note that signal.signal will trigger an atexit)
    atexit.register(_move_on_exit)
    signal.signal(signal.SIGINT, sigterm_handler)

def parse_xnat_string(s):
    match = re.match('(?P<alias>.*):(?P<project>.*):(?P<session>.*):(?P<scan>.*)', s)
    return match.groupdict()

if __name__ == '__main__':
    main()

