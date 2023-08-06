import os
import sys
import time
import logging
from .. import commons
import subprocess as sp

logger = logging.getLogger(__name__)
this = sys.modules[__name__]

def get(version):
    return commons.get(this, 'mri_cnr', version)

def mri_cnr_362e302e30(input, output, log,  **kwargs):
    '''
    FreeSurfer 6.0.0
    '''
    mri_cnr = commons.which('mri_cnr')
    if not mri_cnr:
        raise commons.CommandNotFoundError('could not find mri_cnr')
    if 'surf_dir' not in kwargs:
        raise Exception('function requires surf_dir argument')
    cmd = [
        mri_cnr,
        kwargs['surf_dir'],
        input
    ]
    cwd = os.getcwd()
    tic = time.time()
    try:
        logger.debug('running %s', sp.list2cmdline(cmd))
        stdout = sp.check_output(cmd, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        logger.critical(os.linesep + e.output.decode('utf-8'))
        provenance = commons.provenance(mri_cnr, cmd, cwd, tic, time.time())
        commons.log(provenance, e.output, log)
        raise e
    provenance = commons.provenance(mri_cnr, cmd, cwd, tic, time.time())
    commons.log(provenance, stdout, log)
    return stdout,provenance
