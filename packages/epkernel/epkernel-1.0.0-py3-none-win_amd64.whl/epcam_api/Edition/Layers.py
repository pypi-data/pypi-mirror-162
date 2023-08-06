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

def break_features(job, step, layers, sel_type):
    try:
        BASE.sel_break(job, step, layers, sel_type)
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