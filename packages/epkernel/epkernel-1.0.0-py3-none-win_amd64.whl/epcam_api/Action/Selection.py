import os, sys, json
from epcam_api import epcam, BASE

def set_attribute_filter(logic, attribute_list):
    """
    #设置属性筛选
    :param     logic:0 ：全部满足  1:有其一
    :param     attribute_list:要设置的属性列表
    :returns   :
    :raise    error:
    """
    try:
        BASE.filter_set_attribute(logic, attribute_list)
    except Exception as e:
        print(e)
    return 0

def select_features_by_filter(job, step, layers):
    """
    #根据筛选条件选择
    :param     job:
    :param     step:
    :param     layers:layer列表
    :returns   :
    :raises    error:
    """
    try:
        BASE.select_features_by_filter(job, step, layers)
    except Exception as e:
        print(e)
    return 0

def reset_select_filter():
    try:
        BASE.set_select_param(0x7F, False, [], 0, 0, -1, -1, [], 0, True)
    except Exception as e:
        print(e)
    return 0

def clear_select(job, step, layer):
    try:
        BASE.clear_selected_features(job, step, layer)
    except Exception as e:
        print(e)
    return 0
    
def set_featuretype_filter(featuretype):
    """
    #设置feature type筛选
    :param     featuretype:代表筛选features的类型
    :returns   :
    :raises    error:
    """
    try:
        ret = BASE.get_select_param()
        data = json.loads(ret)
        select_param = data['paras']['param']
        #print(data)  
        flag = select_param['attributes_flag']
        value = select_param['attributes_value']   
        symbols = select_param['symbols']
        pr_value = select_param['profile_value']
        sele = select_param['use_selection']
        minline = select_param['minline']
        maxline = select_param['maxline']
        dcode = select_param['dcode']
        has_symbol = select_param['has_symbols']
        BASE.set_select_param(featuretype, has_symbol, symbols,minline, maxline,dcode, flag,value, pr_value,sele)
    except Exception as e:
        print(e)
    return 0

def set_include_symbol_filter(symbol_list):
    """
    #设置include symbol筛选
    :param     symbol_list:设置筛选include_symbol的list
    :returns   :
    :raises    error:
    """
    try:
        ret = BASE.get_select_param()
        data = json.loads(ret)
        select_param = data['paras']['param']
        featuretype = select_param['featuretypes']
        flag = select_param['attributes_flag']
        value = select_param['attributes_value']   
        pr_value = select_param['profile_value']
        sele = select_param['use_selection']
        minline = select_param['minline']
        maxline = select_param['maxline']
        dcode = select_param['dcode']
        if symbol_list == '':
            BASE.set_select_param(featuretype, False, symbol_list,minline, maxline,dcode, flag,value, pr_value,sele)
        else :
            BASE.set_select_param(featuretype, True, symbol_list,minline, maxline,dcode, flag,value, pr_value,sele)

    except Exception as e:
        print(e)
    return 0

def reverse_select(job, step, layer):
    """
    #反选
    :param     job:
    :param     step:
    :param     layer:
    :returns   :
    :raises    error:
    """
    try:
        BASE.counter_election(job, step, layer)
    except Exception as e:
        print(e)
    return 0

def set_selection(is_standard, is_clear, all_layers, is_select, inside, exclude):
    try:
        BASE.set_selection(is_standard, is_clear, all_layers, is_select, inside, exclude)
    except Exception as e:
        print(e)
    return 0

#重置设置模式
def reset_selection():
    try:
        BASE.set_selection(True, True, True, True, True, True)
    except Exception as e:
        print(e)
    return 0

#取消选中
def unselect_features(job, step, layer):
    try:
        BASE.unselect_features(job, step, layer)
    except Exception as e:
        print(e)
    return 0

def select_feature_by_polygon(job, step, layer, selectpolygon):
    try:
        BASE.select_polyline(job, step, layer, selectpolygon)
    except Exception as e:
        print(e)
    return 0

def select_feature_by_point(job, step, layer, location_x,location_y):
    pass