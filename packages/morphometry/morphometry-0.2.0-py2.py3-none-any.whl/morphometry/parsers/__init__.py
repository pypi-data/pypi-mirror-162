import os
import re
import collections as col

def parse_mri_cnr(s):
    s = s.decode('utf-8')
    lh_cnr = re.search('lh CNR = (.*)', s).group(1)
    rh_cnr = re.search('rh CNR = (.*)', s).group(1)
    tot_cnr = re.search('total CNR = (.*)', s).group(1)
    s = s.split('\n')
    lh_gm_wm_cnr = re.search('gray/white CNR = (.*),', s[3]).group(1)
    lh_gm_csf_cnr = re.search('gray/csf CNR = (.*)', s[3]).group(1)
    rh_gm_wm_cnr = re.search('gray/white CNR = (.*),', s[6]).group(1)
    rh_gm_csf_cnr = re.search('gray/csf CNR = (.*)', s[6]).group(1)
    return {
        'lh_cnr': float(lh_cnr),
        'lh_gm_wm_cnr': float(lh_gm_wm_cnr),
        'lh_gm_csf_cnr': float(lh_gm_csf_cnr),
        'rh_cnr': float(rh_cnr),
        'rh_gm_wm_cnr': float(rh_gm_wm_cnr),
        'rh_gm_csf_cnr': float(rh_gm_csf_cnr),
        'tot_cnr': float(tot_cnr)
    }

def parse_wm_anat_snr(s):
    s = s.decode('utf-8')
    s = s.split()
    return {
        'subject': s[0],
        'snr': float(s[1]),
        'mean_intensity': float(s[2]),
        'stdev_intensity': float(s[3]),
        'mask_vox_after_erosion': int(s[4]),
        'num_erodes': int(s[5])
    }

def parse_mris_euler_number(s):
    s = s.decode('utf-8')
    num_holes = re.search('--> (\d+) holes', s).group(1)
    return {
        'holes': int(num_holes)
    }

def parse_tal_qc(s):
    s = s.decode('utf-8')
    result = re.search('eta = ([-+]?[0-9]*\.?[0-9]+)  atlas_transform_error = ([-+]?[0-9]*\.?[0-9]+)', s)
    return {
        'eta': float(result.group(1)),
        'atlas_txfm_error': float(result.group(2))
    }

def parse_mris_anatomical_stats(s):
    s = s.decode('utf-8')
    num_vert = re.search('number of vertices\s+= ([0-9]+)', s).group(1)
    tot_surf_area = re.search('total surface area\s+= ([0-9]+) mm\^2', s).group(1)
    tot_gm_vol = re.search('total gray matter volume\s+= ([0-9]+) mm\^3', s).group(1)
    avg_cort_thick = re.search('average cortical thickness\s+= ([-+]?[0-9]*\.?[0-9]+) mm \+\- [-+]?[0-9]*\.?[0-9]+ mm', s).group(1)
    avg_cort_thick_err = re.search('average cortical thickness\s+= [-+]?[0-9]*\.?[0-9]+ mm \+\- ([-+]?[0-9]*\.?[0-9]+) mm', s).group(1)
    avg_int_rect_mean_curv = re.search('average integrated rectified mean curvature\s+= ([-+]?[0-9]*\.?[0-9]+)', s).group(1)
    avg_int_rect_gauss_curv = re.search('average integrated rectified Gaussian curvature\s+= ([-+]?[0-9]*\.?[0-9]+)', s).group(1)
    fold_index = re.search('folding index\s+= ([0-9]+)', s).group(1)
    intr_curv_index = re.search('intrinsic curvature index\s+= ([-+]?[0-9]*\.?[0-9]+)', s).group(1)
    return {
        'num_vert': int(num_vert),
        'tot_surf_area': int(tot_surf_area),
        'tot_gm_vol': int(tot_gm_vol),
        'avg_cort_thick': float(avg_cort_thick),
        'avg_cort_thick_err': float(avg_cort_thick_err),
        'avg_integrated_rect_mean_curv': float(avg_int_rect_mean_curv),
        'avg_integrated_rect_gauss_curv': float(avg_int_rect_gauss_curv),
        'fold_index': int(fold_index),
        'intrinsic_curv_index': float(intr_curv_index)
    }

def parse_stats_file(f):
    data = col.defaultdict(col.OrderedDict)
    # read contents of *.stats file
    with open(f, 'rU') as fo:
        content = fo.read().split(os.linesep)
    # separate headers and payload
    headers,payload = list(),list()
    for row in content:
        if not row.strip():
            continue
        if row.startswith('#'):
            headers.append(row)
        else:
            payload.append(row)
    # parse all Measure metrics from the header blob and also get payload ColHeaders
    measure_re = re.compile('# Measure .*?, (?P<name>[\w-]+),? .*, (?P<value>.*), (?P<units>.*)')
    colheaders_re = re.compile('# ColHeaders (?P<headers>.*)')
    for header in headers:
        measure = measure_re.match(header)
        colheaders = colheaders_re.match(header)
        if measure:
            name = measure.group('name')
            value = measure.group('value')
            units = measure.group('units')
            data['headers'][name] = {
                'value': value,
                'units': units
            }
        elif colheaders:
            colheaders = colheaders.group('headers').strip().split(' ')
    # parse the payload
    for row in payload:
        values = row.strip().split()
        row = col.OrderedDict(zip(colheaders, values))
        data['data'][row['StructName']] = row
    return data

