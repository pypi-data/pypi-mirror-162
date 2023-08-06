import os
import sys
import time
import logging
from .. import commons
import subprocess as sp

logger = logging.getLogger(__name__)
this = sys.modules[__name__]

def get(version):
    return commons.get(this, 'tal_qc_azs', version)

def tal_qc_azs_362e302e30(input, output, log,  **kwargs):
    '''
    FreeSurfer 6.0.0 tal_QC_AZS
    '''
    tal_qc_azs = commons.which('tal_QC_AZS')
    if not tal_qc_azs:
        raise commons.CommandNotFoundError('could not find tal_QC_AZS')
    cmd = [
        tal_qc_azs,
        str(input)
    ]
    cwd = os.getcwd()
    tic = time.time()
    try:
        logger.debug('running %s', sp.list2cmdline(cmd))
        stdout = sp.check_output(cmd, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        logger.critical(os.linesep + e.output.decode('utf-8'))
        provenance = commons.provenance(tal_qc_azs, cmd, cwd, tic, time.time())
        commons.log(provenance, e.output, log)
        raise e
    provenance = commons.provenance(tal_qc_azs, cmd, cwd, tic, time.time())
    commons.log(provenance, stdout, log)
    return stdout,provenance
