import os
import json
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

DIR = os.path.dirname(__file__)

class Laterality(object):
    APARC_REGIONS = [
        'bankssts',
        'caudalanteriorcingulate',
        'caudalmiddlefrontal',
        'cuneus',
        'entorhinal',
        'fusiform',
        'inferiorparietal',
        'inferiortemporal',
        'isthmuscingulate',
        'lateraloccipital',
        'lateralorbitofrontal',
        'lingual',
        'medialorbitofrontal',
        'middletemporal',
        'parahippocampal',
        'paracentral',
        'parsopercularis',
        'parsorbitalis',
        'parstriangularis',
        'pericalcarine',
        'postcentral',
        'posteriorcingulate',
        'precentral',
        'precuneus',
        'rostralanteriorcingulate',
        'rostralmiddlefrontal',
        'superiorfrontal',
        'superiorparietal',
        'superiortemporal',
        'supramarginal',
        'frontalpole',
        'temporalpole',
        'transversetemporal',
        'insula'
    ]

    ASEG_REGIONS = [
        'Thalamus-Proper',
        'Caudate',
        'Putamen',
        'Pallidum',
        'Hippocampus',
        'Amygdala'
    ]

    def __init__(self, d):
        '''
        :param d: FreeSurfer output directory
        :type d: str
        '''
        self.d = d
        self._output_dir = os.path.join(self.d, 'plots')

    def output_dir(self):
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)
        return self._output_dir

    def aparc(self, output=None):
        lh_aparc = os.path.join(self.d, 'stats', 'lh.aparc.stats.json')
        rh_aparc = os.path.join(self.d, 'stats', 'rh.aparc.stats.json')
        if not output:
            output = os.path.join(self.output_dir(), 'aparc-laterality.png')
        with open(lh_aparc) as fo:
            lh_aparc = json.load(fo)
        with open(rh_aparc) as fo:
            rh_aparc = json.load(fo)
        x,y = [],[]
        for region in Laterality.APARC_REGIONS:
            x.append(float(lh_aparc['data'][region]['ThickAvg']))
            y.append(float(rh_aparc['data'][region]['ThickAvg']))
        plt.plot(x, y, '.')
        ax = plt.gca()
        ax.plot([0, 1], [0, 1], transform=ax.transAxes, linewidth=1, color='grey', linestyle='dashed')
        plt.title('Cortical Laterality')
        plt.xlabel('Left ROI Thickness ($mm$)')
        plt.ylabel('Right ROI Thickness ($mm$)')
        logger.debug('saving %s', output)
        plt.savefig(output)
        plt.close()

    def aseg(self, output=None):
        aseg = os.path.join(self.d, 'stats', 'aseg.stats.json')
        if not output:
            output = os.path.join(self.output_dir(), 'aseg-laterality.png')
        with open(aseg) as fo:
            aseg = json.load(fo)
        x,y = [],[]
        for region in Laterality.ASEG_REGIONS:
            x.append(float(aseg['data']['Left-' + region]['Volume_mm3']))
            y.append(float(aseg['data']['Right-' + region]['Volume_mm3']))
        plt.plot(x, y, '.')
        ax = plt.gca()
        ax.plot([0, 1], [0, 1], transform=ax.transAxes, linewidth=1, color='gray', linestyle='dashed')
        plt.title('Subcortical Laterality')
        plt.xlabel('Left ROI Volume ($mm^3$)')
        plt.ylabel('Right ROI Volume ($mm^3$)')
        logger.debug('saving %s', output)
        plt.savefig(output)
        plt.close()

