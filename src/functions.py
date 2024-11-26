import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon
from shapely.wkt import loads
from werkzeug.utils import secure_filename
import os
import fiona

def save_file(file, upload_folder):
    filename = secure_filename(file.filename)
    
    if not filename.lower().endswith('.gpkg') or filename.lower().endswith('.xml'):
        return "Invalid file type. Only .gpkg files are allowed.", 400
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)  
    

    json_files = []
    for layername in fiona.listlayers(file_path):
        print(f"Layer: {layername}")
        gdf = gpd.read_file(file_path, layer=layername)
        json_path = os.path.join(upload_folder, f"{os.path.splitext(filename)[0]}_{layername}.json")
        gdf.to_file(json_path, driver="GeoJSON")
        json_files.append(json_path)

    os.remove(file_path)
    return json_files
    
    

def write_geometry_to_file(geometry, output_file):
    with open(output_file, 'w') as f:
        f.write(str(geometry))
    print(f"Geometria guardada em {output_file}")


def plot_multipolygon(multipolygon, crs):
    gdf_multipolygon = gpd.GeoDataFrame([{'geometry': multipolygon}], crs=crs)
    
    gdf_multipolygon.plot()
    plt.show()


def check_neighbors(multipolygon1_wtk, multipolygon2_wtk):
    multipolygon1 = loads(multipolygon1_wtk)
    multipolygon2 = loads(multipolygon2_wtk)
    
    are_neighbors = multipolygon1.touches(multipolygon2)
    print(are_neighbors)

    return are_neighbors


#multipolygon1_wkt = "MULTIPOLYGON (((375484.1102 3661872.9156, 375484.1149000004 3661872.9123, 375447.2089999998 3661812.8916999996, 375445.1161000002 3661813.1611, 375444.4173999997 3661813.251, 375444.26999999955 3661813.2699999996, 375442.64470000006 3661810.758199999, 375436.5700000003 3661801.369999999, 375434.5700000003 3661798.7699999996, 375433.2312000003 3661797.5205000006, 375431.5700000003 3661795.9700000007, 375429.6596999997 3661794.867900001, 375428.96999999974 3661794.4700000007, 375427.3700000001 3661793.9700000007, 375426.42810000014 3661793.8522999994, 375425.76999999955 3661793.7699999996, 375423.5338000003 3661793.9190999996, 375422.76999999955 3661793.9700000007, 375421.0700000003 3661794.67, 375421.0521999998 3661795.0086000003, 375420.76999999955 3661800.369999999, 375421.46999999974 3661803.4700000007, 375423.6699999999 3661812.619999999, 375426.8700000001 3661825.619999999, 375428.7619000003 3661831.9837999996, 375431.26999999955 3661840.42, 375433.6699999999 3661847.0199999996, 375435.6699999999 3661852.2200000007, 375436.69409999996 3661853.9482000005, 375438.8700000001 3661857.619999999, 375444.26999999955 3661866.2200000007, 375452.26999999955 3661884.619999999, 375455.26999999955 3661887.0199999996, 375460.6699999999 3661887.2200000007, 375467.0700000003 3661884.619999999, 375468.1867000004 3661884.2564000003, 375475.6699999999 3661881.8200000003, 375484.1462000003 3661873.7291, 375484.1102 3661872.9156)))"
#multipolygon2_wkt = "MULTIPOLYGON (((375484.1102 3661872.9156, 375484.1149000004 3661872.9123, 375447.2089999998 3661812.8916999996, 375445.1161000002 3661813.1611, 375444.4173999997 3661813.251, 375444.26999999955 3661813.2699999996, 375442.64470000006 3661810.758199999, 375436.5700000003 3661801.369999999, 375434.5700000003 3661798.7699999996, 375433.2312000003 3661797.5205000006, 375431.5700000003 3661795.9700000007, 375429.6596999997 3661794.867900001, 375428.96999999974 3661794.4700000007, 375427.3700000001 3661793.9700000007, 375426.42810000014 3661793.8522999994, 375425.76999999955 3661793.7699999996, 375423.5338000003 3661793.9190999996, 375422.76999999955 3661793.9700000007, 375421.0700000003 3661794.67, 375421.0521999998 3661795.0086000003, 375420.76999999955 3661800.369999999, 375421.46999999974 3661803.4700000007, 375423.6699999999 3661812.619999999, 375426.8700000001 3661825.619999999, 375428.7619000003 3661831.9837999996, 375431.26999999955 3661840.42, 375433.6699999999 3661847.0199999996, 375435.6699999999 3661852.2200000007, 375436.69409999996 3661853.9482000005, 375438.8700000001 3661857.619999999, 375444.26999999955 3661866.2200000007, 375452.26999999955 3661884.619999999, 375455.26999999955 3661887.0199999996, 375460.6699999999 3661887.2200000007, 375467.0700000003 3661884.619999999, 375468.1867000004 3661884.2564000003, 375475.6699999999 3661881.8200000003, 375484.1462000003 3661873.7291, 375484.1102 3661872.9156)))"

#check_neighbors(multipolygon1_wkt, multipolygon2_wkt)

