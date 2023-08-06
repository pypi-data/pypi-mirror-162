import os
import sys
import time
import logging
from .. import commons
import subprocess as sp

logger = logging.getLogger(__name__)
this = sys.modules[__name__]

def get(version):
    return commons.get(this, 'wm_anat_snr', version)

def wm_anat_snr_362e302e30(input, output, log,  **kwargs):
    '''
    FreeSurfer 6.0.0 wm-anat-snr
    '''
    wm_anat_snr = commons.which('wm-anat-snr')
    if not wm_anat_snr:
        raise commons.CommandNotFoundError('could not find wm-anat-snr')
    os.environ['SUBJECTS_DIR'] = os.path.dirname(input)
    subject_name = os.path.basename(input)
    cmd = [
        wm_anat_snr,
        '--s', subject_name,
        '--force'
    ]
    cwd = os.getcwd()
    tic = time.time()
    try:
        logger.debug('running %s', sp.list2cmdline(cmd))
        stdout = sp.check_output(cmd, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        logger.critical(os.linesep + e.output.decode('utf-8'))
        provenance = commons.provenance(wm_anat_snr, cmd, cwd, tic, time.time())
        commons.log(provenance, e.output, log)
        raise e
    provenance = commons.provenance(wm_anat_snr, cmd, cwd, tic, time.time())
    commons.log(provenance, stdout, log)
    return stdout,provenance
