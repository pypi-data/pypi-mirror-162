import os
import sys
import time
import logging
from .. import commons
import subprocess as sp

logger = logging.getLogger(__name__)
this = sys.modules[__name__]

def get(version):
    return commons.get(this, 'mris_euler_number', version)

def mris_euler_number_362e302e30(input, output, log,  **kwargs):
    '''
    FreeSurfer 6.0.0 mris_euler_number
    '''
    mris_euler_number = commons.which('mris_euler_number')
    if not mris_euler_number:
        raise commons.CommandNotFoundError('could not find mris_euler_number')
    cmd = [
        mris_euler_number,
        input, 
    ]
    cwd = os.getcwd()
    tic = time.time()
    try:
        logger.debug('running %s', sp.list2cmdline(cmd))
        stdout = sp.check_output(cmd, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        logger.critical(os.linesep + e.output.decode('utf-8'))
        provenance = commons.provenance(mris_euler_number, cmd, cwd, tic, time.time())
        commons.log(provenance, e.output, log)
        raise e
    provenance = commons.provenance(mris_euler_number, cmd, cwd, tic, time.time())
    commons.log(provenance, stdout, log)
    return stdout,provenance
