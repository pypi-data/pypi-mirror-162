import re
import os
import yaml
import lxml
import zipfile
import logging
from lxml import etree

logger = logging.getLogger(__name__)

class Report:
    def __init__(self, output_dir, logs_dir):
        self.output_dir = output_dir
        self.logs_dir = logs_dir
        self.report = None
        self.module = os.path.dirname(__file__)
        
    def build_report(self):
        if self.report:
            return self.report
        # initialize report file
        self.report = {
            'provenance': None,
            'tal_qc_azs': None,
            'aseg': None,
            'aparc': {
                'lh': None,
                'rh': None
            },
            'mris_anatomical_stats': {
                'lh': None,
                'rh': None
            }
        }
        # read in provenance file
        provenance = os.path.join(self.logs_dir, '__main__.yml')
        with open(provenance, 'r') as fo:
            self.report['provenance'] = yaml.load(fo, Loader=yaml.FullLoader)
        # load left hemisphere mris_anatomical_stats
        lh_anat_stats = os.path.join(self.output_dir, 'stats', 'lh.mris_anatomical_stats.json') 
        with open(lh_anat_stats, 'r') as fo:
            self.report['mris_anatomical_stats']['lh'] = yaml.load(fo, Loader=yaml.FullLoader)
        # load right hemisphere mris_anatomical_stats
        rh_anat_stats = os.path.join(self.output_dir, 'stats', 'rh.mris_anatomical_stats.json') 
        with open(rh_anat_stats, 'r') as fo:
            self.report['mris_anatomical_stats']['rh'] = yaml.load(fo, Loader=yaml.FullLoader)
        # load tal_qc_azs
        tal_qc_azs = os.path.join(self.output_dir, 'stats', 'tal_qc_azs.json')
        with open(tal_qc_azs, 'r') as fo:
            self.report['tal_qc_azs'] = yaml.load(fo, Loader=yaml.FullLoader)
        # load aseg.stats
        aseg_stats = os.path.join(self.output_dir, 'stats', 'aseg.stats.json')
        with open(aseg_stats, 'r') as fo:
            self.report['aseg'] = yaml.load(fo, Loader=yaml.FullLoader)
        # load lh.aparc.stats
        lh_aparc_stats = os.path.join(self.output_dir, 'stats', 'lh.aparc.stats.json')
        with open(lh_aparc_stats, 'r') as fo:
            self.report['aparc']['lh'] = yaml.load(fo, Loader=yaml.FullLoader)
        # load rh.aparc.stats
        rh_aparc_stats = os.path.join(self.output_dir, 'stats', 'rh.aparc.stats.json')
        with open(rh_aparc_stats, 'r') as fo:
            self.report['aparc']['rh'] = yaml.load(fo, Loader=yaml.FullLoader)

        return self.report

    def build_assessment(self, output='assessment.zip'):
        # this is as straight forward as I can possibly make it
        self.build_report()
        # initialize namespaces
        ns = {
            None: 'http://www.neuroinfo.org/neuroinfo',
            'xs': 'http://www.w3.org/2001/XMLSchema',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xnat': 'http://nrg.wustl.edu/xnat',
            'neuroinfo': 'http://www.neuroinfo.org/neuroinfo'
        }
        # read sourcedata file
        sourcedata_file = os.path.join(self.logs_dir, 'sourcedata.yml')
        with open(sourcedata_file, 'r') as fo:
            source = yaml.load(fo, Loader=yaml.FullLoader)['application/x-xnat']
        mid = '{0}_ANAT{1}'.format(source['session'], source['scan'])
        # root element
        xnatns = '{%s}' % ns['xnat']
        root = etree.Element('Morphometrics3', nsmap=ns)
        root.attrib['project'] = source['project']
        root.attrib['ID'] = '{0}_Morphometrics3'.format(mid)
        root.attrib['label'] = '{0}_Morphometrics3'.format(mid)
        # compile a list of files to be added to xnat:out section
        files = [
            {
                'filename': os.path.join(self.output_dir, 'report.yml'),
                'URI': '{0}_Morph3.yml'.format(mid),
                'format': 'text/yaml',
                'label': 'Report File',
                'file_list': True
            },
            {
                'filename': os.path.join(self.output_dir, 'tmp', 'coronal.png'),
                'URI': '{0}_Morph3_coronal.png'.format(mid),
                'format': 'image/png',
                'label': 'Screen Coronal',
                'file_list': True
            },
            {
                'filename': os.path.join(self.output_dir, 'tmp', 'axial.png'),
                'URI': '{0}_Morph3_axial.png'.format(mid),
                'format': 'image/png',
                'label': 'Screen Axial',
                'file_list': True
            },
            {
                'filename': os.path.join(self.output_dir, 'tmp', 'sagittal.png'),
                'URI': '{0}_Morph3_sagittal.png'.format(mid),
                'format': 'image/png',
                'label': 'Screen Sagittal',
                'file_list': True
            }
        ]
        for hemi in ['lh', 'rh']:
            files.extend([{
                'filename': os.path.join(self.output_dir, 'tmp', 'infl_{0}_ant.png'.format(hemi)),
                'URI': '{0}_Morph3_infl_{1}_ant.png'.format(mid, hemi),
                'format': 'image/png',
                'label': '{0} Anterior'.format(hemi.upper()),
                'file_list': True
            },
            {
                'filename': os.path.join(self.output_dir, 'tmp', 'infl_{0}_inf.png'.format(hemi)),
                'URI': '{0}_Morph3_infl_{1}_inf.png'.format(mid, hemi),
                'format': 'image/png',
                'label': '{0} Inferior'.format(hemi.upper()),
                'file_list': True
            },
            {
                'filename': os.path.join(self.output_dir, 'tmp', 'infl_{0}_lat.png'.format(hemi)),
                'URI': '{0}_Morph3_infl_{1}_lat.png'.format(mid, hemi),
                'format': 'image/png',
                'label': '{0} Lateral'.format(hemi.upper()),
                'file_list': True
            },
            {
                'filename': os.path.join(self.output_dir, 'tmp', 'infl_{0}_med.png'.format(hemi)),
                'URI': '{0}_Morph3_infl_{1}_med.png'.format(mid, hemi),
                'format': 'image/png',
                'label': '{0} Medial'.format(hemi.upper()),
                'file_list': True
            },
            {
                'filename': os.path.join(self.output_dir, 'tmp', 'infl_{0}_pst.png'.format(hemi)),
                'URI': '{0}_Morph3_infl_{1}_pst.png'.format(mid, hemi),
                'format': 'image/png',
                'label': '{0} Posterior'.format(hemi.upper()),
                'file_list': True
            },
            {
                'filename': os.path.join(self.output_dir, 'tmp', 'infl_{0}_sup.png'.format(hemi)),
                'URI': '{0}_Morph3_infl_{1}_sup.png'.format(mid, hemi),
                'format': 'image/png',
                'label': '{0} Superior'.format(hemi.upper()),
                'file_list': True
            }])

        # add xnat:date and xnat:time
        xnat_date = etree.SubElement(root, xnatns + 'date').text = self.report['provenance'][0]['start_date']
        xnat_date = etree.SubElement(root, xnatns + 'time').text = self.report['provenance'][0]['start_time']
                
        # add xnat:out files
        xnat_out = etree.SubElement(root, xnatns + 'out')
        for item in files:
            e = etree.SubElement(xnat_out, xnatns + 'file')
            e.attrib['format'] = item['format']
            e.attrib['label'] = item['label']
            e.attrib['URI'] = item['URI']
            e.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = 'xnat:resource'
            if item['file_list']:
                tags = etree.SubElement(e, xnatns + 'tags')
                etree.SubElement(tags, xnatns + 'tag').text = 'file_list'

        # add xnat:imageSession_ID
        etree.SubElement(root, xnatns + 'imageSession_ID').text = source['accession']
        etree.SubElement(root, 'scan_id').text = source['scan']
        etree.SubElement(root, 'SessionLabel').text = source['session']

        # read name mapping file
        mapping_file = os.path.join(self.module, 'mapping.yml')
        with open(mapping_file, 'r') as fo:
            mapping = yaml.load(fo, Loader=yaml.FullLoader)

        # do not add 'L_' or 'R_' prefix to certain header metrics
        global_metrics = [
            'CorVol',
            'SupraTentVol',
            'SupraTentVolNotVent',
            'BrainSegVol',
            'BrainSegVolNotVent',
            'BrainSegVolNotVentSurf',
            'ICV'
        ]

        # track total surface area and numbers of vertices        
        total_vertices = 0
        lh_total_surf_area = 0
        rh_total_surf_area = 0

        # add lh_aparc_hdr
        lh_aparc_hdr = etree.SubElement(root, 'lh_aparc_hdr')
        for name,metrics in iter(self.report['aparc']['lh']['headers'].items()):
            name = mapping['aparc']['headers'][name.lower()]
            if name == 'NumVert':
                total_vertices += int(metrics['value'])
            if name in global_metrics:
                etree.SubElement(lh_aparc_hdr, name).text = metrics['value']
            else:
                etree.SubElement(lh_aparc_hdr, 'L_{0}'.format(name)).text = metrics['value']

        # add lh_aparc
        lh_aparc = etree.SubElement(root, 'lh_aparc')
        for structure,metrics in iter(self.report['aparc']['lh']['data'].items()):
            struct_name = mapping['aparc']['structures'][structure.lower()]
            for metric,value in iter(metrics.items()):
                metric_name = mapping['aparc']['metrics'][metric.lower()]
                if metric_name == 'StructName':
                    continue
                elif metric_name == 'SurfArea':
                    lh_total_surf_area += int(value)
                etree.SubElement(lh_aparc, 'L_{0}_{1}'.format(struct_name, metric_name)).text = value
        etree.SubElement(lh_aparc_hdr, 'L_TotSurfArea').text = str(lh_total_surf_area)

        # add rh_aparc_hdr
        rh_aparc_hdr = etree.SubElement(root, 'rh_aparc_hdr')
        for name,metrics in iter(self.report['aparc']['rh']['headers'].items()):
            name = mapping['aparc']['headers'][name.lower()]
            if name == 'NumVert':
                total_vertices += int(metrics['value'])
            if name in global_metrics:
                etree.SubElement(rh_aparc_hdr, name).text = metrics['value']
            else:
                etree.SubElement(rh_aparc_hdr, 'R_{0}'.format(name)).text = metrics['value']

        # add rh_aparc
        rh_aparc = etree.SubElement(root, 'rh_aparc')
        for structure,metrics in iter(self.report['aparc']['rh']['data'].items()):
            struct_name = mapping['aparc']['structures'][structure.lower()]
            for metric,value in iter(metrics.items()):
                metric_name = mapping['aparc']['metrics'][metric.lower()]
                if metric_name == 'StructName':
                    continue
                elif metric_name == 'SurfArea':
                    rh_total_surf_area += int(value)
                etree.SubElement(rh_aparc, 'R_{0}_{1}'.format(struct_name, metric_name)).text = value
        etree.SubElement(rh_aparc_hdr, 'R_TotSurfArea').text = str(rh_total_surf_area)

        # add total metrics to both lh and rh headers
        etree.SubElement(lh_aparc_hdr, 'TotSurfArea').text = str(lh_total_surf_area + rh_total_surf_area)
        etree.SubElement(rh_aparc_hdr, 'TotSurfArea').text = str(lh_total_surf_area + rh_total_surf_area)
        etree.SubElement(lh_aparc_hdr, 'TotNumVert').text = str(total_vertices)
        etree.SubElement(rh_aparc_hdr, 'TotNumVert').text = str(total_vertices)

        # add aseg_hdr
        aseg_hdr = etree.SubElement(root, 'aseg_hdr')
        for name,metrics in iter(self.report['aseg']['headers'].items()):
            name = mapping['aseg']['headers'][name.lower()]
            etree.SubElement(aseg_hdr, name).text = metrics['value']

        # add aseg
        lh_aseg = etree.SubElement(root, 'lh_aseg')
        rh_aseg = etree.SubElement(root, 'rh_aseg')
        etc_aseg = etree.SubElement(root, 'etc_aseg')
        for structure,metrics in iter(self.report['aseg']['data'].items()):
            struct_name = mapping['aseg']['structures'][structure.lower().replace('-', '_')]
            for metric,value in iter(metrics.items()):
                if metric in ['StructName', 'Index']:
                    continue
                metric_name = mapping['aseg']['metrics'][metric.lower()]
                if struct_name.startswith('L_'):
                    etree.SubElement(lh_aseg, '{0}_{1}'.format(struct_name, metric_name)).text = value
                elif struct_name.startswith('R_'):
                    etree.SubElement(rh_aseg, '{0}_{1}'.format(struct_name, metric_name)).text = value
                else:
                    etree.SubElement(etc_aseg, '{0}_{1}'.format(struct_name, metric_name)).text = value
                
        # add tal_qc 
        tal_qc_file = os.path.join(self.output_dir, 'stats', 'tal_qc_azs.json')
        with open(tal_qc_file, 'r') as fo:
            tal_qc = yaml.load(fo, Loader=yaml.FullLoader)
        e = etree.SubElement(root, 'tal_qc')
        for metric,value in iter(tal_qc.items()):
            metric_name = mapping['tal_qc']['metrics'][metric]
            etree.SubElement(e, metric_name).text = str(value)

        # add left mris_anatomical_stats
        lh_mris_anat_file = os.path.join(self.output_dir, 'stats', 'lh.mris_anatomical_stats.json')
        with open(lh_mris_anat_file, 'r') as fo:
            lh_anat_stats = yaml.load(fo, Loader=yaml.FullLoader)
        e = etree.SubElement(root, 'lh_anat')
        for metric,value in iter(lh_anat_stats.items()):
            metric_name = mapping['mris_anat_stats']['metrics'][metric]
            etree.SubElement(e, 'L_' + metric_name).text = str(value)
        
        # add right mris_anatomical_stats
        rh_mris_anat_file = os.path.join(self.output_dir, 'stats', 'rh.mris_anatomical_stats.json')
        with open(rh_mris_anat_file, 'r') as fo:
            rh_anat_stats = yaml.load(fo, Loader=yaml.FullLoader)
        e = etree.SubElement(root, 'rh_anat')
        for metric,value in iter(rh_anat_stats.items()):
            metric_name = mapping['mris_anat_stats']['metrics'][metric]
            etree.SubElement(e, 'R_' + metric_name).text = str(value)

        # build the archive
        with zipfile.ZipFile(output, 'w') as zf:
            for f in files:
                filename = f['filename']
                arcname = os.path.join('ASSESSMENT_FOLDER', f['URI'])
                logger.info('adding %s to %s', filename, arcname)
                zf.write(filename, arcname)
            zf.writestr('ASSESSMENT.XML', etree.tostring(root, pretty_print=True))
