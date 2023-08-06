import os, sys, json
from epcam_api import epcam, BASE
from epcam_api.Edition import Layers
from epcam_api.Action import Selection, Information

# jobname, org_layer_index, dst_layer, poi_layer_index
def copy_layer(jobname, old_layer_name):
    try:
        ret = BASE.get_matrix(jobname)
        data = json.loads(ret)
        layer_infos = data['paras']['info']
        for i in range(0, len(layer_infos)):
            if layer_infos[i]['name'] == old_layer_name:
                old_layer_index = i + 1
        dst_layer = ''
        # 新建空layer
        create_layer(jobname, 'jbz')
        ret2 = BASE.copy_layer(jobname, old_layer_index,
                               dst_layer, len(layer_infos) + 1)
        data2 = json.loads(ret2)
        new_layer = data2['paras']['newname']
        # 删除新层
        delete_layer(jobname, 'jbz')
        return new_layer
    except Exception as e:
        print(e)
    return ''

# 创建layer


def create_layer(job, layer):
    try:
        index = -1  # 默认创建在末尾
        step = ''  # 在所有层创建
        BASE.create_new_layer(job, step, layer, index)
    except Exception as e:
        print(e)

# 删除layer


def delete_layer(job, layername):
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        layer_infos = data['paras']['info']
        for i in range(0, len(layer_infos)):
            if layer_infos[i]['name'] == layername:
                layer_index = i + 1
                BASE.delete_layer(job, layer_index)
                break
    except Exception as e:
        print(e)
    return 0


def insert_row(job, row_index):
    try:
        BASE.insert_layer(job, row_index)
    except Exception as e:
        print(e)
    return 0


def insert_column(job, col_index):
    try:
        BASE.insert_step(job, col_index)
    except Exception as e:
        print(e)
    return 0

# 依据polygon 建profile


def create_profile_by_polygon(job, step, layer, poly):
    """
    #依据polygon 建profile
    :param     poly:
    :returns   
    :raises    error:
    """
    try:
        for i in range(len(poly)-1):
            BASE.add_line(job, step, [], layer, 'r1', poly[i][0],
                          poly[i][1], poly[i+1][0], poly[i+1][1], 1, 0, [])
        Selection.select_features_by_filter(job, step, [layer])
        Layers.create_profile(job, step, layer)
        Selection.select_features_by_filter(job, step, [layer])
        Layers.delete_feature(job, step, [layer])
    except Exception as e:
        print(e)
    return ''

# 创建step


def create_step(job, step):
    try:
        index = -1  # 默认创建在末尾
        BASE.create_step(job, step, index)
    except Exception as e:
        print(e)


# 创建阴阳step：
def create_flip(job, step):
    try:
        siglayer = Information.get_signal_layers(job)
        smlayer = Information.get_soldermask_layers(job)
        drllayer = Information.get_drill_layer_name(job)
        screenlayer = Information.get_silkscreen_layers(job)
        splayer = []
        allboard = Information.get_board_layers(job)
        for layer in allboard:
            if (layer not in siglayer) and (layer not in smlayer) and (layer not in drllayer) and (layer not in screenlayer):
                splayer.append(layer)
        stepname = step+'_flip'
        create_step(job, stepname)
        poly = Information.get_profile(job, step)
        poly = json.loads(poly)
        poly = poly["points"]
        orig_poly = []  # 左下角pcs profile polygon
        for i in range(len(poly)):
            per_point = []
            per_point.append(-poly[i]["ix"])
            per_point.append(poly[i]["iy"])
            orig_poly.append(per_point)
        create_profile_by_polygon(job, stepname, siglayer[0], orig_poly)

        for i in range(len(siglayer)):
            BASE.copy_layer_features(job, step, [siglayer[i]], job, stepname, [
                                     siglayer[len(siglayer)-1-i]], False, False)
        for i in range(len(smlayer)):
            BASE.copy_layer_features(job, step, [smlayer[i]], job, stepname, [
                                     smlayer[len(smlayer)-1-i]], False, False)
        for i in range(len(screenlayer)):
            BASE.copy_layer_features(job, step, [screenlayer[i]], job, stepname, [
                                     screenlayer[len(screenlayer)-1-i]], False, False)
        for i in range(len(splayer)):
            BASE.copy_layer_features(job, step, [splayer[i]], job, stepname, [
                                     splayer[len(splayer)-1-i]], False, False)
        for drl in drllayer:
            num1 = drl[3:]
            g = num1.find('-')
            first = int(num1[0:g])
            second = int(num1[g+1:])
            if first == 1 and second == len(siglayer):
                BASE.copy_layer_features(
                    job, step, [drl], job, stepname, [drl], False, False)
            else:
                newdrl = 'drl'+str(len(siglayer)-second+1) + \
                    '-'+str(len(siglayer)-first+1)
                if newdrl not in drllayer:
                    create_layer(job, newdrl)
                    allboard.append(newdrl)
                    BASE.copy_layer_features(job, step, [drl], job, stepname, [
                                             newdrl], False, False)
                else:
                    BASE.copy_layer_features(job, step, [drl], job, stepname, [
                                             newdrl], False, False)

        for layer in allboard:
            BASE.transform(job, stepname, layer, 0, False, False,
                           True, False, False, {'ix': 0, 'iy': 0}, 0, 1, 1, 0, 0)
    except Exception as e:
        print(e)
    return ''


def change_matrix_row(job, layer, context, type, layername):
    """
    #修改指定层别信息,若修改后信息与原层别一致，则此函数不执行
    :param     jobname:
    :param     layer:
    :param     context:
    :returns   :
    :raises    error:
    """
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        layer_infos = data['paras']['info']
        for i in range(0, len(layer_infos)):
            if layer_infos[i]['name'] == layer:
                layer_index = i + 1
                layer_infos[i]['context'] = context
                layer_infos[i]['type'] = type
                layer_infos[i]['name'] = layername
        BASE.change_matrix(job, -1, layer_index, '',
                           layer_infos[layer_index-1])
    except Exception as e:
        print(e)
    return 0


def change_matrix_column(job, src_name, dst_name):
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        step_infos = data['paras']['steps']
        old_step_index = step_infos.index(src_name) + 1
        old_layer_index = -1
        new_layer_info = ''
        BASE.change_matrix(job, old_step_index,
                           old_layer_index, dst_name, new_layer_info)
    except Exception as e:
        print(e)


def create_step(job, step):
    try:
        index = -1  # 默认创建在末尾
        BASE.create_step(job, step, index)
    except Exception as e:
        print(e)


def delete_step(job, step):
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        step_infos = data['paras']['steps']
        for i in range(0, len(step_infos)):
            if step_infos[i] == step:
                step_index = i + 1
        BASE.delete_step(job, step_index)
    except Exception as e:
        print(e)
    return 0


def copy_step(job, src_step_name):
    try:
        ret = BASE.get_matrix(job)
        data = json.loads(ret)
        step_infos = data['paras']['steps']

        for i in range(0, len(step_infos)):
            if step_infos[i] == src_step_name:
                old_step_index = i + 1
        BASE.insert_step(job, old_step_index+1)
        dst_step = ''
        # 新建空
        create_step(job, 'jbz')
        ret2 = BASE.copy_step(job, old_step_index,
                              dst_step, len(step_infos) + 1)
        data2 = json.loads(ret2)
        new_step = data2['paras']['newname']
        # 删除新层
        delete_step(job, 'jbz')
        return new_step
    except Exception as e:
        print(e)
    return ''


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
