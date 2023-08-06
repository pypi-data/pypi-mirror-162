import os
import json
import traceback
import numpy as np
import pandas as pd
import meteva
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import xarray as xr

def set_jar_path(path):
    if os.path.exists(path):
        meteva.base.ws_jar_path = path
    else:
        print(path + " not exists")

def java_class_func(jar_path, class_name, func_name, jvm_path=None, *args):
    import jpype
    """
    调用jar包中class下的方法
    :return:
    """
    # jar包路径的配置
    # jarpath = os.path.join(os.path.abspath("."), "D:\\hf-0.1.jar")
    jarpath = os.path.join(os.path.abspath(".."), jar_path)
    # 这里指定了jvm
    if jvm_path:
        jvmpath = jvm_path
    else:
        jvmpath = jpype.getDefaultJVMPath()

    try:
        jpype.startJVM(jvmpath, "-ea", "-Djava.class.path=%s" % jarpath)
    except Exception as e:
        pass

    java_class = jpype.JClass(class_name)
    ru_param = ','.join(list(map(lambda x: json.dumps(x), args)))

    res = str(eval("java_class.%s(%s)" % (func_name, ru_param)))
    #jpype.shutdownJVM()
    return res


def high_low_center(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100,grade_interval = 5):
    grid0 = meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    para = {"type":"high_low_center",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,"grade_interval":grade_interval,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":grid0.slon,"startlat":grid0.slat,"dlon":grid0.dlon,"dlat":grid0.dlat,
            "data":data,"output_dir_root":output_dir_root}
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    graphy = json.loads(str_json)
    return graphy


def vortex(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 = meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    para = {"type":"vortex",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":grid0.slon,"startlat":grid0.slat,"dlon":grid0.dlon,"dlat":grid0.dlat,
            "data":data,"output_dir_root":output_dir_root}
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    graphy = json.loads(str_json)
    return graphy



def trough(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 = meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    para = {"type":"trough",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":grid0.slon,"startlat":grid0.slat,"dlon":grid0.dlon,"dlat":grid0.dlat,
            "data":data,"output_dir_root":output_dir_root}
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    graphy = json.loads(str_json)
    return graphy


def reverse_trough(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 = meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    para = {"type":"reverse_trough",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":grid0.slon,"startlat":grid0.slat,"dlon":grid0.dlon,"dlat":grid0.dlat,
            "data":data,"output_dir_root":output_dir_root}
    para_json = json.dumps(para)
    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    graphy = json.loads(str_json)
    return graphy


def convergence_line(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    para = {"type":"convergence_line",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":grid0.slon,"startlat":grid0.slat,"dlon":grid0.dlon,"dlat":grid0.dlat,
            "data":data,"output_dir_root":output_dir_root}
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    graphy = json.loads(str_json)
    return graphy


def shear(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    para = {"type":"shear",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":grid0.slon,"startlat":grid0.slat,"dlon":grid0.dlon,"dlat":grid0.dlat,
            "data":data,"output_dir_root":output_dir_root}
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    graphy = json.loads(str_json)
    return graphy


def jet(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100,jet_min_speed = 12,only_south_jet =False):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    para = {"type":"jet",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,"jet_min_speed":jet_min_speed,"only_south_jet":str(only_south_jet),
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":grid0.slon,"startlat":grid0.slat,"dlon":grid0.dlon,"dlat":grid0.dlat,
            "data":data,"output_dir_root":output_dir_root}
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    graphy = json.loads(str_json)
    return graphy



def subtropical_high(grd,output_dir_root,smooth_times = 0,min_size = 500,necessary_height = 5840,sufficient_height = 5880):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    para = {"type":"subtropical_high",
            "smooth_times":smooth_times,"min_size":min_size,"necessary_height":necessary_height,"sufficient_height":sufficient_height,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":grid0.slon,"startlat":grid0.slat,"dlon":grid0.dlon,"dlat":grid0.dlat,
            "data":data,"output_dir_root":output_dir_root}
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    graphy = json.loads(str_json)
    return graphy


def south_asia_high(grd,output_dir_root,smooth_times = 0,min_size = 800,sn_height = 16800):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    para = {"type":"south_asia_high",
            "smooth_times":smooth_times,"min_size":min_size,"sn_height":sn_height,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":grid0.slon,"startlat":grid0.slat,"dlon":grid0.dlon,"dlat":grid0.dlat,
            "data":data,"output_dir_root":output_dir_root}
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    graphy = json.loads(str_json)
    return graphy




def tran_graphy_to_df(graphy):
    '''

    :param graphy:
    :return:
    '''
    if graphy is None: return None,None

    dtime = int(graphy["dtime"])

    time  = meteva.base.all_type_time_to_time64(graphy["time"])

    level = graphy["level"]

    ids = graphy["features"].keys()

    list1 = []
    for id in ids:
        center = graphy["features"][id]
        lon = center["centrePoint"]["lon"]
        lat = center["centrePoint"]["lat"]
        center_value = center["centrePoint"]["value"]
        area = center["features"]["area"]
        strenght = center["features"]["strenght"]
        dict1 = {"level":level,"time":time,"dtime":dtime,"id" :int(id),"lon":lon,"lat":lat,"value":center_value,"area":area,"strenght":strenght}
        list1.append(dict1)
    center = pd.DataFrame(list1)

    list1 = []
    for id in ids:
        points = graphy["features"][id]["axes"]["point"]
        if len(points)>0:
            array = np.array(points)
            lon = array[:,0]
            lat = array[:,1]
            df = pd.DataFrame({"lon":lon,"lat":lat})
            df["id"] = int(id)
            list1.append(df)
    if len(list1)>0:
        df = pd.concat(list1,axis = 0)
        df["level"] = level
        df["time"] = time
        df["dtime"] = dtime
        df["data0"] = 0
        axes = meteva.base.sta_data(df)
        return center,axes
    else:
        return center,None