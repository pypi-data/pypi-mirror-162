import os
import re
import sys
import time
import yaml
import select
import socket
import base64
import hashlib
import logging
import getpass as gp
import datetime as dt
import nibabel as nib
import subprocess as sp
import collections as col

logger = logging.getLogger(__name__)

yaml.SafeDumper.add_representer(col.OrderedDict, yaml.representer.SafeRepresenter.represent_dict)

Provenance = col.namedtuple('Provenance', [
    'basename',
    'dirname',
    'checksum',
    'command',
    'start',
    'start_date',
    'start_time',
    'end',
    'username',
    'mtime',
    'cwd',
    'os',
    'cpu',
    'hostname',
    'dist',
    'elapsed',
    'env'
])

def provenance(exe, command, cwd, start, end):
    return Provenance(basename=os.path.basename(exe),
                      dirname=os.path.dirname(exe),
                      checksum=sha256file(exe),
                      mtime=dt.datetime.fromtimestamp(os.path.getmtime(exe)).isoformat(),
                      command=command,
                      start=start,
                      end=end,
                      os=sp.check_output(['uname', '-a']).strip(),
                      dist=sp.check_output(['cat', '/etc/system-release']).strip(),
                      hostname=socket.gethostname(),
                      cwd=cwd,
                      username=gp.getuser(),
                      cpu=getcpu(),
                      start_date=dt.datetime.fromtimestamp(start).strftime('%Y-%m-%d'),
                      start_time=dt.datetime.fromtimestamp(start).strftime('%H:%M:%S'),
                      elapsed=end-start,
                      env=getenv())

def getcpu():
    info = dict()
    output = sp.check_output(['lscpu']).decode('utf-8').strip()
    for line in output.split(os.linesep):
        match = re.match('(.*):\s+(.*)', line)
        if not match:
            raise CPUInfoError('failed to parse line from lscpu output: "{0}"'.format(line))
        k,v = match.groups()
        info[k] = v
    return info

class CPUInfoError(Exception):
    pass

def wait_for_keypress(timeout=10):
    if sys.stdin.isatty():
        select.select([sys.stdin], [],[], timeout)
    else:
        toc = dt.datetime.now() + dt.timedelta(seconds=timeout)
        while dt.datetime.now() <= toc:
            time.sleep(1)

def get(module, name, version):
    hash = base64.b16encode(str.encode(version)).lower()
    fname = '%s_%s' % (name, hash.decode('utf-8'))
    try:
        return getattr(module, fname)
    except ValueError:
        raise VersionError('could not find %s/%s (%s)' % (name, version, fname))

def dimlen(input, dim):
    input = nib.load(input)
    return input.shape[dim]

def check_fov(inputs):
    for f in inputs:
        # load file and get field-of-view along each dimension
        nii = nib.load(str(f))
        fovs = (nii.header['dim'] * nii.header['pixdim'])[1:4]
        logger.info(f'{f} has field-of-view {fovs}')
        # return True if any field of view is > 256
        if any(i > 256.0 for i in fovs):
            logger.info(f'detected a field-of-view > 256.0')
            return True
    return False

def check_submillimeter(inputs):
    for f in inputs:
        # load file and get voxel dimensions
        pixdims = nib.load(str(f)).header['pixdim'][1:4]
        # return True if any pixel dimension is submillimeter
        if any(x < 1.0 for x in pixdims):
            return True
    return False

def sha256file(f):
    f = os.path.expanduser(f)
    with open(f, 'rb') as fo:
        return hashlib.sha256(fo.read()).hexdigest()

def log(provenance, output, logfile_prefix):
    prov_logfile = '{0}.yml'.format(logfile_prefix.rstrip('.'))
    log_provenance(provenance, prov_logfile)
    output_logfile = '{0}.log'.format(logfile_prefix.rstrip('.'))
    log_output(output, output_logfile)

def log_output(output, logfile):
    with open(logfile, 'wb') as fo:
        fo.write(output)

def log_provenance(provenance, logfile):
    content = list()
    if os.path.exists(logfile):
        with open(logfile, 'r') as fo:
            content = yaml.load(fo, Loader=yaml.SafeLoader)
    content.append(provenance._asdict())
    with open(logfile, 'w') as fo:
        yaml.safe_dump(content, fo, default_flow_style=False)

def which(x):
    for p in os.environ.get('PATH').split(os.pathsep):
        p = os.path.join(p, x)
        if os.path.exists(p):
            return os.path.abspath(p)
    return None

def getenv():
    def _split(v):
        if v not in os.environ:
            return None
        return os.environ[v].split(os.pathsep)
    return {
        'PATH': _split('PATH'),
        'LD_LIBRARY_PATH': _split('LD_LIBRARY_PATH'),
        'MATLABPATH': _split('MATLABPATH'),
        'PYTHONPATH': _split('PYTHONPATH'),
        'PERL5LIB': _split('PERL5LIB'),
        'FREESURFER_HOME': os.environ.get('FREESURFER_HOME', None),
        'SUBJECTS_DIR': os.environ.get('SUBJECTS_DIR', None),
        'MNI_DATAPATH': os.environ.get('MNI_DATAPATH', None),
        'MNI_DIR': os.environ.get('MNI_DIR', None),
        'MINC_BIN_DIR': os.environ.get('MINC_BIN_DIR', None),
        'FSF_OUTPUT_FORMAT': os.environ.get('FSF_OUTPUT_FORMAT', None),
        'FMRI_ANALYSIS_DIR': os.environ.get('FMRI_ANALYSIS_DIR', None),
        'MNI_PERL5LIB': _split('MNI_PERL5LIB'),
        'FSFAST_HOME': os.environ.get('FSFAST_HOME', None),
        'LOCAL_DIR': os.environ.get('LOCAL_DIR', None),
        'OS': os.environ.get('OS', None),
        'SHELL': os.environ.get('SHELL', None),
        'LANG': os.environ.get('LANG', None),
        'USER': os.environ.get('USER', None),
        'PWD': os.environ.get('PWD', None),
        'DISPLAY': os.environ.get('DISPLAY', None),
        'http_proxy': os.environ.get('http_proxy', None),
        'https_proxy': os.environ.get('https_proxy', None),
        'no_proxy': os.environ.get('no_proxy', None)
    }
   
class Orient:
    NEUROLOGICAL = 0
    RADIOLOGICAL = 1 

class Order:
    ASCEND = 0
    DESCEND = 1
    INTER_MIDDLE_TOP = 2
    INTER_BOTTOM_UP = 3
    INTER_TOP_DOWN = 4

class Axis:
    X = 0
    Y = 1
    Z = 2
    T = 3

class VersionError(Exception):
    pass

class SubprocessError(Exception):
    pass

class APIError(Exception):
    pass

class CommandNotFoundError(Exception):
    pass
