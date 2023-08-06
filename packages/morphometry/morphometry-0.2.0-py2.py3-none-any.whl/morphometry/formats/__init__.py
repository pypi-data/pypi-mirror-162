import os
import pydicom
import logging

logger = logging.getLogger(__name__)

class Format:
    ANALYZE = ".analyze"
    NIFTI = ".nii"
    NIFTI_GZ = ".nii.gz"
    DICOM = ""
    MATRIX = ".mat"

class File(object):
    def __init__(self, dirname, basename, format):
        self.dirname = dirname
        if basename.endswith(format):
            basename = basename.rstrip(format)
        self.basename = basename
        self.format = format
        self.fullfile = os.path.join(dirname, basename + format)
        self.multipart = False

    def index(self):
        return None

    def exists(self):
        return os.path.exists(self.fullfile)

    def __str__(self):
        return self.fullfile

class Multipart(File):
    def __init__(self, dirname, basename, format):
        super(Multipart, self).__init__(dirname, basename, format)
        self.multipart = True

    def index(self):
        files = os.listdir(self.fullfile)
        return [os.path.join(self.fullfile, x) for x in files]

class Matrix(File):
    def __init__(self, dirname, basename):
        super(Matrix, self).__init__(dirname, basename, Format.MATRIX)
        self.type = 'matlab'
        self.mime = 'application/x-matlab'
    
class Analyze(Multipart):
    def __init__(self, dirname, basename):
        super(Analyze, self).__init__(dirname, basename, Format.ANALYZE)
        self.type = 'analyze'
        self.mime = 'application/x-analyze'
   
class Dicom(Multipart):
    def __init__(self, dirname, basename):
        super(Dicom, self).__init__(dirname, basename, Format.DICOM)
        self.type = 'dicom'
        self.mime = 'application/dicom'

    def index(self):
        files = list()
        for f in os.listdir(self.fullfile):
            fullfile = os.path.join(self.fullfile, f)
            try:
                pydicom.read_file(fullfile)
                files.append(fullfile)
            except pydicom.errors.InvalidDicomError as e:
                logger.warn('not a dicom file %s', fullfile)
                continue
        return files

class Nifti(File):
    def __init__(self, dirname, basename):
        super(Nifti, self).__init__(dirname, basename, Format.NIFTI)
        self.type = 'nifti'
        self.mime = 'application/x-nifti'

class NiftiGz(File):
    def __init__(self, dirname, basename):
        super(NiftiGz, self).__init__(dirname, basename, Format.NIFTI_GZ)
        self.mime = 'application/x-nifti'
