import os, sys, json
from epcam_api import epcam, BASE

from epcam_api.Action import Information, Selection
from epcam_api.Edition import Matrix

def copy_other(src_job, src_step, src_layers, dst_layers, invert, offset_x, offset_y, mirror, resize, rotation, x_anchor, y_anchor):
    try:
        BASE.sel_copy_other(src_job, src_step, src_layers, dst_layers, invert, offset_x, offset_y, 
                    mirror, resize, rotation, x_anchor, y_anchor)
    except Exception as e:
        print(e)
    return ''


def delete_feature(job, step, layers):
    try:
        BASE.sel_delete(job, step, layers)
    except Exception as e:
        print(e)
    return 0

def change_text(job, step, layers, text, font, x_size, y_size, width, polarity, mirror):
    try:
        BASE.change_text(job, step, layers, text, font, x_size, y_size, width, polarity, mirror)
    except Exception as e:
        print(e)
    return 0

def break_features(job, step, layers, type):
    try:
        BASE.sel_break(job, step, layers, type)
    except Exception as e:
            print(e)
    return 0

def add_line(job, step, layers, symbol, start_x, start_y, end_x, end_y, polarity, attributes):
    try:
        layer = ''
        if len(layers) > 0:
            layer = layers[0]
        BASE.add_line(job, step, layers, layer, symbol, start_x, start_y, end_x, end_y, polarity, 0, attributes)
    except Exception as e:
        print(e)
    return 0
    
# 依据polygon 建profile
def create_profile_by_polygon(job, step, layer, poly):
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

def hierarchy_edit(job, step, layers, mode):
    try:
        BASE.sel_index(job, step, layers, mode)
    except Exception as e:
        print(e)
    return 0

def add_surface(job, step, layers, polarity, attributes, points_location):
    try:
        layer = ''
        if len(layers)> 0:
            layer = layers[0]
        BASE.add_surface(job, step, layers, layer, polarity, 0, False, attributes, points_location)
    except Exception as e:
        print(e)
    return ''

def add_round_surface(job, step, layers, polarity, attributes,center_x,center_y,radius):
    try:
        layer = ''
        if len(layers)> 0:
            layer = layers[0]
        point2_x = center_x + radius
        point2_y = center_y
        points_location = [[center_x, center_y], [point2_x, point2_y]]
        BASE.add_surface(job, step, layers, layer, polarity, 0, True, attributes, points_location)
    except Exception as e:
        print(e)
    return '' 

def contour2pad(job, step, layers, tol, minsize, maxsize, suffix):
    try:
        BASE.contour2pad(job, step, layers, tol, minsize, maxsize, suffix)
    except Exception as e:
        print(e)
    return ''

def resize_polyline(job, step, layers, size, sel_type):
    try:
        BASE.resize_polyline(job, step, layers, size, sel_type)
    except Exception as e:
        print(e)
    return ''

def add_line(job, step, layers, symbol, start_x, start_y, end_x, end_y, polarity, attributes):
    try:
        layer=''
        if len(layers)>0:
            layer=layers[0]
        BASE.add_line(job, step, layers, layer, symbol, start_x, start_y, end_x, end_y, polarity, 0, attributes)
    except Exception as e:
        print(e)
    return ''

#跨层移动feature
def move2other_layer(src_job, src_step, src_layers, dst_job, dst_step, dst_layer, invert, offset_x, offset_y, mirror, resize, rotation, x_anchor, y_anchor):
    try:
        BASE.sel_move_other(src_job, src_step, src_layers, dst_job, dst_step, dst_layer, invert, offset_x, offset_y, 
                    mirror, resize, rotation, x_anchor, y_anchor)
    except Exception as e:
        print(e)
    return ''

def contourize(job, step, layers, accuracy, separate_to_islands, size, mode):
    try:
        BASE.contourize(job, step, layers, accuracy, separate_to_islands, size, mode)
    except Exception as e:
        print(e)
    return ''

def add_pad(job, step, layers, symbol, location_x, location_y, polarity, orient, attributes):
    try:
        layer=''
        if len(layers)>0:
            layer=layers[0]
        BASE.add_pad(job, step, layers, layer, symbol, location_x, location_y, polarity, 0, orient, attributes)
    except Exception as e:
        print(e)
    return ''

def change_feature_symbols(job, step, layers, symbol):
    try:
        BASE.change_feature_symbols(job, step, layers, symbol, False)
    except Exception as e:
        print(e)
    return 0

def copy_features2dstjob(src_job, src_step, src_layers, dst_job, dst_step, dst_layers, mode, invert):
    try:
        BASE.copy_layer_features(src_job, src_step, src_layers, dst_job, dst_step, dst_layers, mode, invert)
    except Exception as e:
        print(e)
    return ''
