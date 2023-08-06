import os
import sys
import time
import logging
from .. import commons
import subprocess as sp

logger = logging.getLogger(__name__)
this = sys.modules[__name__]

def get(version):
    return commons.get(this, 'mris_anatomical_stats', version)

def mris_anatomical_stats_362e302e30(input, output, log,  **kwargs):
    '''
    FreeSurfer 6.0.0 mris_anatomical_stats
    '''
    mris_anatomical_stats = commons.which('mris_anatomical_stats')
    if not mris_anatomical_stats:
        raise commons.CommandNotFoundError('could not find mris_anatomical_stats')
    hemi = kwargs['hemi']
    os.environ['SUBJECTS_DIR'] = os.path.dirname(input)
    subject_name = os.path.basename(input)
    cmd = [
        mris_anatomical_stats,
        '-l', '{0}.cortex.label'.format(hemi),
        subject_name,
        hemi
    ]
    cwd = os.getcwd()
    tic = time.time()
    try:
        logger.debug('running %s', sp.list2cmdline(cmd))
        stdout = sp.check_output(cmd, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        logger.critical(os.linesep + e.output.decode('utf-8'))
        provenance = commons.provenance(mris_anatomical_stats, cmd, cwd, tic, time.time())
        commons.log(provenance, e.output, log)
        raise e
    provenance = commons.provenance(mris_anatomical_stats, cmd, cwd, tic, time.time())
    commons.log(provenance, stdout, log)
    return stdout,provenance
