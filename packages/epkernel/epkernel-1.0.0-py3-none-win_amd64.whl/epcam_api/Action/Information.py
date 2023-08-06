import os, sys, json
from epcam_api import epcam, BASE

def is_selected(job,step,layer):
    ret = BASE.is_selected(job,step,layer)
    ret = json.loads(ret)
    if 'result' in ret:
        return ret['result']
    return False

def get_drill_layer_name(job):
    """
    #获取孔层layer名
    :param     job:
    :param     step:
    :return    drill_list:孔层名列表
    :raises    error:
    """
    try:
        ret = BASE.get_graphic(job)
        data = json.loads(ret)
        drill_list = []
        layer_info = data['paras']['info']
        for i in range(0, len(layer_info)):
            if layer_info[i]['type'] == 'drill' and layer_info[i]['context'] == 'board':
                drill_list.append(layer_info[i]['name'])
        return drill_list
    except Exception as e:
        print(e)
        #sys.exit(0)
    return ''


def get_inner_layers(job):
    """
    #获取内层layer_list
    :param     job:
    :returns   inner_layer_list:内层layername列表
    :raises    error:
    """
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        layer_info = data['paras']['info']
        board_layer_list=[]
        index_list = []
        for i in range(0, len(layer_info)):
            if layer_info[i]['context'] == 'board' and layer_info[i]['type'] == 'signal':
                index_list.append(i)
        for j in range(min(index_list),max(index_list)+1):
            board_layer_list.append(layer_info[j]['name'])
        
        if len(board_layer_list) <= 2:
            print('no inner layer!')
            return []
        else:
            board_layer_list.pop(-1)
            board_layer_list.pop(0)
            inner_layer_list = board_layer_list
        return inner_layer_list
    except Exception as e:
        print(e)
    return ''

def get_layers(job):
    try:
        ret = BASE.get_graphic(job)
        data = json.loads(ret)
        layer_list = []
        layer_info = data['paras']['info']
        if len(layer_info):
            for i in range(0, len(layer_info)):
                layer_list.append(layer_info[i]['name'])
        return layer_list
    except Exception as e:
        print(e)
        #sys.exit(0)
    return ''

def get_board_layers(job):
    try:
        ret = BASE.get_graphic(job)
        data = json.loads(ret)
        layer_list = []
        layer_info = data['paras']['info']
        if len(layer_info):
            for i in range(0, len(layer_info)):
                if layer_info[i]['context'] == 'board':
                    layer_list.append(layer_info[i]['name'])
        return layer_list
    except Exception as e:
        print(e)
        #sys.exit(0)
    return ''

def get_soldermask_layers(job):
    """
    #获取防焊层list
    :param     job:
    :param     step:
    :returns   solder_mask_list:
    :raises    error:
    """
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        layer_info = data['paras']['info']
        solder_mask_list=[]
        for i in range(0, len(layer_info)):
            if layer_info[i]['context'] == 'board' and layer_info[i]['type'] == 'solder_mask':
                solder_mask_list.append(layer_info[i]['name'])      
        return solder_mask_list
    except Exception as e:
        print(e)
    return ''

def get_signal_layers(job):
    """
    #获取内外层layer 名
    :param     job:
    :returns   inner_layer_list:内层layername列表
    :raises    error:
    """
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        layer_info = data['paras']['info']
        board_layer_list=[]
        index_list = []
        for i in range(0, len(layer_info)):
            if layer_info[i]['context'] == 'board' and layer_info[i]['type'] == 'signal':
                index_list.append(i)
        for j in range(min(index_list),max(index_list)+1):
            board_layer_list.append(layer_info[j]['name'])

        inner_layer_list = board_layer_list
        return inner_layer_list
    except Exception as e:
        print(e)
    return ''

def get_outer_layers(job):
    """
    #获取外层list
    :param     job:
    :returns   outter_layer_list:外层layername列表
    :raises    error:
    """
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        layer_info = data['paras']['info']
        board_layer_list=[]
        index_list = []
        for i in range(0, len(layer_info)):
            if layer_info[i]['context'] == 'board' and layer_info[i]['type'] == 'signal':
                index_list.append(i)
        if index_list == []:
            print("no signal layer")
            return []
        for j in range(min(index_list),max(index_list)+1):
            board_layer_list.append(layer_info[j]['name'])
        outter_layer_list = []
        outter_layer_list.append(board_layer_list[0])
        if len(board_layer_list) == 1:
            return outter_layer_list
        else: 
            outter_layer_list.append(board_layer_list[-1])
        return outter_layer_list
    except Exception as e:
        print(e)
    return ''


def get_silkscreen_layers(job):
    """
    #获取丝印层layer_list        
    :param     job:     
    :returns   layer_list:丝印层layername列表     
    :raises    error:    
    """
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        layer_info = data['paras']['info']
        layer_list = []
        for i in range(0, len(layer_info)):
            if layer_info[i]['context'] == 'board' and layer_info[i]['type'] == 'silk_screen':
                layer_list.append(layer_info[i]['name'])
        
        if len(layer_list) < 1:
            print("can't find silk_screen-layer!")

        return layer_list
    except Exception as e:
        print(e)
    return ''

def get_soldermask_layers(job):
    """
    #获取防焊层list
    :param     job:
    :param     step:
    :returns   solder_mask_list:
    :raises    error:
    """
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        layer_info = data['paras']['info']
        solder_mask_list=[]
        for i in range(0, len(layer_info)):
            if layer_info[i]['context'] == 'board' and layer_info[i]['type'] == 'solder_mask':
                solder_mask_list.append(layer_info[i]['name'])      
        return solder_mask_list
    except Exception as e:
        print(e)
    return ''

#获取layer profile polygon
def get_profile(job, step):
    try:
        return BASE.get_profile(job, step)
    except Exception as e:
        print(e)
    return 0

def get_layer_feature_count(jobName, stepName, layerName):
    ret = BASE.get_layer_feature_count(jobName, stepName, layerName)
    ret = json.loads(ret)
    if 'featureNum' in ret:
        return int(ret['featureNum'])
    return -1

def get_steps(job):
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        steps = data['paras']['steps']
        return steps
    except Exception as e:
        print(e)
    return []