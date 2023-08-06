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


def get_layers(job):
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        layer_infos = data['paras']['info']
        layer_list = []
        for i in range(0, len(layer_infos)):
            layer_list.append(layer_infos[i]['name'])
        return layer_list
    except Exception as e:
        print(e)
    return []

def get_selected_features_infos(job, step, layer):
    """
    #获取选中feature的所有信息
    :param     job:
    :param     step:
    :param     layer:
    :param     
    :returns   featureinfo: feature信息
    :raises    error:
    """ 
    try:
        ret = BASE.get_selected_feature_infos(job, step, layer)
        data = json.loads(ret)
        featureinfos = []
        if data['paras'] != False:
            return data['paras']
    except Exception as e:
        print(e)
    return []

def get_usersymbol_list(job):
    try:
        ret = BASE.get_special_symbol_names(job)
        data = json.loads(ret)
        user_list = data['paras']
        return user_list
    except Exception as e:
        print(e)
    return []

def get_smd_or_bga_symbolname(job, step, layer):
    """
    #拿到选中的smd/bga pad的symbol信息
    :param     job:
    :param     step:
    :returns   solder_mask_list:
    :raises    error:
    """
    try:
        #获取选中PAD的symbol信息
        global _size
        ret = BASE.get_selected_features_report(job, step, layer)
        data = json.loads(ret)
        pad_list = data['paras']['pad_list']
        symbol_list = []
        if pad_list == None:
            return symbol_list
        else:
            for i in range(0, len(pad_list)):
                if pad_list[i]['symbolname'] not in symbol_list:
                    try:
                        _size = 0
                        if pad_list[i]['symbol_width'] <= pad_list[i]['symbol_height']:
                            _size = pad_list[i]['symbol_width']
                        else:
                            _size = pad_list[i]['symbol_height']                            
                        symbol_list.append([pad_list[i]['symbolname'], _size])
                    except:
                        continue
        return symbol_list
    except Exception as e:
        print(e)
    return []

def get_profile_box(job, step):   
    try:
        ret = BASE.get_profile_box(job, step)
        data = json.loads(ret)
        profile_box = data['paras']
        return profile_box
    except Exception as e:
        print(e)
    return 0

def get_all_features_num(job, step, layer):
    try:
        num = 0
        BASE.load_layer(job, step, layer)
        ret = BASE.get_all_features_report(job, step, layer)
        data = json.loads(ret)
        if data['paras']['lines_list'] != None:
            if len(data['paras']['lines_list']):
                for i in range(len(data['paras']['lines_list'])):
                    num += data['paras']['lines_list'][i]['count']
        if data['paras']['pad_list'] != None:
            if len(data['paras']['pad_list']):
                for j in range(len(data['paras']['pad_list'])):
                    num += data['paras']['pad_list'][j]['count']
        if data['paras']['surface_list'] != None:
            if len(data['paras']['surface_list']):
                for k in range(len(data['paras']['surface_list'])):
                    num += data['paras']['surface_list'][k]['count']
        if data['paras']['arc_list'] != None:
            if len(data['paras']['arc_list']):
                for v in range(len(data['paras']['arc_list'])):
                    num += data['paras']['arc_list'][v]['count']
        if data['paras']['text_list'] != None:
            if len(data['paras']['text_list']):
                for t in range(len(data['paras']['text_list'])):
                    num += data['paras']['text_list'][t]['count']
        return num
    except Exception as e:
        print(e)
    return 0

def get_sr_limit(job,step): #获取拼版中最小和最大坐标
    repeat_infos=BASE.get_step_repeat(job,step)    #获取拼板信息
    repeat_infos=json.loads(repeat_infos)
    repeat_infos=repeat_infos['result']
    xminlist=[]
    yminlist=[]
    xmaxlist=[]
    ymaxlist=[]
    for repeat_info in repeat_infos:
        repeat_infox=repeat_info['X']
        repeat_infoy=repeat_info['Y']
        set_box=BASE.get_profile_box(job, repeat_info['NAME'])
        set_box=json.loads(set_box)['paras']
        datum_x=json.loads(BASE.get_step_header_infos(job, repeat_info['NAME']))['x_datum']
        datum_y=json.loads(BASE.get_step_header_infos(job, repeat_info['NAME']))['y_datum']
        x_offset = repeat_infox - datum_x
        y_offset = repeat_infoy - datum_y
        pts=[]
        pts.append([set_box['Xmin']+x_offset,set_box['Ymin']+y_offset])
        pts.append([set_box['Xmin']+x_offset,set_box['Ymax']+y_offset])
        pts.append([set_box['Xmax']+x_offset,set_box['Ymax']+y_offset])
        pts.append([set_box['Xmax']+x_offset,set_box['Ymin']+y_offset])
        width=set_box['Xmax']-set_box['Xmin']
        height=set_box['Ymax']-set_box['Ymin']
        if repeat_info['MIRROR']:
            pts.clear()
            pts.append([set_box['Xmin']+x_offset-width,set_box['Ymin']+y_offset])
            pts.append([set_box['Xmin']+x_offset-width,set_box['Ymax']+y_offset])
            pts.append([set_box['Xmin']+x_offset,set_box['Ymax']+y_offset])
            pts.append([set_box['Xmin']+x_offset,set_box['Ymin']+y_offset])

        if repeat_info['ANGLE']!=0:
            value = math.acos(-1) / 180
            ratio = -1 * repeat_info['ANGLE'] * value
            if repeat_info['MIRROR']:
                ratio = -1 * (360-repeat_info['ANGLE']) * value
            for pt in pts:
                a = pt[0]
                b = pt[1]
                pt[0]=(a - repeat_infox)*math.cos(ratio) - (b - repeat_infoy)*math.sin(ratio) + repeat_infox
                pt[1]=(a - repeat_infox)*math.sin(ratio) + (b - repeat_infoy)*math.cos(ratio) + repeat_infoy
        allx=[]
        ally=[]
        for pt in pts:
            allx.append(pt[0])
            ally.append(pt[1])
        allx.sort()
        ally.sort()
        xmin=allx[0]
        ymin=ally[0]
        set_length=allx[-1]-allx[0]
        set_width=ally[-1]-ally[0]    
        length= (repeat_info['NX']-1)*repeat_info['DX']+set_length
        width = (repeat_info['NY']-1)*repeat_info['DY']+set_width
        xmax=xmin+length
        ymax=ymin+width
        xminlist.append(xmin)
        yminlist.append(ymin)
        xmaxlist.append(xmax)
        ymaxlist.append(ymax)
    xminlist.sort()
    yminlist.sort()
    xmaxlist.sort(reverse=True)
    ymaxlist.sort(reverse=True)
    gSRxmin=xminlist[0]/1000000
    gSRymin=yminlist[0]/1000000
    gSRxmax=xmaxlist[0]/1000000
    gSRymax=ymaxlist[0]/1000000
    infos={}
    infos['gSRxmin']=gSRxmin
    infos['gSRymin']=gSRymin
    infos['gSRxmax']=gSRxmax
    infos['gSRymax']=gSRymax
    return infos
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        steps = data['paras']['steps']
        return steps
    except Exception as e:
        print(e)
    return []