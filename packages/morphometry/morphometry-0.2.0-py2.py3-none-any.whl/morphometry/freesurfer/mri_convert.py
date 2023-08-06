import os
import sys
import time
import logging
from .. import commons
import subprocess as sp

logger = logging.getLogger(__name__)
this = sys.modules[__name__]

def get(version):
    return commons.get(this, 'mri_convert', version)

def mri_convert_362e302e30(input, output, log, **kwargs):
    '''
    FreeSurfer 6.0.0 mri_convert
    '''
    mri_convert = commons.which('mri_convert')
    if not mri_convert:
        raise commons.CommandNotFoundError('could not find mri_convert')
    infile, outfile = str(input), str(output)
    d = os.path.dirname(outfile)
    if not os.path.exists(d):
        os.makedirs(d)
    cmd = [
        mri_convert, 
        infile
    ]
    if 'outtype' in kwargs:
        cmd.extend([
            '-ot', kwargs['outtype']
        ])
    cmd.append(outfile)
    cwd = os.getcwd()
    tic = time.time()
    try:
        logger.debug('running %s', sp.list2cmdline(cmd))
        stdout = sp.check_output(cmd, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        logger.critical(os.linesep + e.output.decode('utf-8'))
        provenance = commons.provenance(mri_convert, cmd, cwd, tic, time.time())
        commons.log(provenance, e.output, log)
        raise e
    provenance = commons.provenance(mri_convert, cmd, cwd, tic, time.time())
    commons.log(provenance, stdout, log)
    return stdout,provenance
