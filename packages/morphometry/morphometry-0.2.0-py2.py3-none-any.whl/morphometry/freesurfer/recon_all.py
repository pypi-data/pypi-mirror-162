import os
import sys
import time
import logging
from .. import commons
import subprocess as sp

logger = logging.getLogger(__name__)

this = sys.modules[__name__]

def get(version):
    return commons.get(this, 'recon_all', version)

def recon_all_362e302e30(input, output, log,  **kwargs):
    '''
    FreeSurfer 6.0.0 recon-all
    '''
    recon_all = commons.which('recon-all')
    if not recon_all:
        raise commons.CommandNotFoundError('could not find recon-all')
    output_dirname = os.path.dirname(output)
    output_basename = os.path.basename(output)
    if not os.path.exists(output_dirname):
        os.makedirs(output_dirname)
    cmd = [
        recon_all,
        '-sd', output_dirname, 
        '-s', output_basename,
        '-all'
    ]
    if kwargs.get('custom_tal_atlas', None):
        cmd.extend([
            '-custom-tal-atlas', kwargs.get('custom_tal_atlas')
        ])
    if kwargs.get('cw256', False):
        cmd.append('-cw256')
    if kwargs.get('motioncor', False):
        cmd.append('-motioncor')
    if kwargs.get('hires', False):
        if not kwargs.get('cw256', False):
            cmd.append('-cm')
        else:
            logger.warning('recon-all does not support passing -cm and -cw256 together')
    for image in input:
        cmd.extend([
            '-i', str(image)
        ])
    cwd = os.getcwd()
    tic = time.time()
    try:
        logger.debug('running %s', sp.list2cmdline(cmd))
        stdout = sp.check_output(cmd, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        logger.critical(os.linesep + e.output.decode('utf-8'))
        provenance = commons.provenance(recon_all, cmd, cwd, tic, time.time())
        commons.log(provenance, e.output, log)
        raise e
    provenance = commons.provenance(recon_all, cmd, cwd, tic, time.time())
    commons.log(provenance, stdout, log)
    return stdout,provenance

