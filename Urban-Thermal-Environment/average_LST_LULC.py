import numpy as np
from osgeo import gdal
import pandas as pd

# 读取热岛tiff影像
hotspot_ds = gdal.Open("D:\WME\\02-热环境\\04-数据\\Tiff数据-LST\\年际热岛\重分类\\2001.tif")
hotspot_arr = hotspot_ds.GetRasterBand(1).ReadAsArray()

# 读取土地类型tiff影像
landuse_ds = gdal.Open("D:\\WME\\CLCD\\CLCD_ShangHai_2001.tif")
landuse_arr = landuse_ds.GetRasterBand(1).ReadAsArray()

# 将热岛等级按照土地利用类型进行分组，计算每个土地利用类型上的热岛等级的平均值
unique_landuse = np.unique(landuse_arr)
hotspot_mean_by_landuse = {}
for landuse in unique_landuse:
    if landuse not in [0]:
        # 选择对应土地类型上的像元值
        hotspot_by_landuse = hotspot_arr[landuse_arr == landuse]
        # 排除值为0的像元
        hotspot_by_landuse = hotspot_by_landuse[hotspot_by_landuse != 0]
        # 计算平均值
        hotspot_mean = np.mean(hotspot_by_landuse)
        hotspot_mean_by_landuse[landuse] = hotspot_mean

# 将结果输出到Excel文件
df = pd.DataFrame.from_dict(hotspot_mean_by_landuse, orient='index', columns=['平均热岛等级'])
df.index.name = '土地利用类型'
# df.to_excel('hotspot_mean_by_landuse.xlsx')
print(df)
