# import numpy as np
# from osgeo import gdal
# import pandas as pd
#
# # 读取热岛tiff影像
# hotspot_ds = gdal.Open("D:\\WME\\02-热环境\\04-数据\\Tiff数据-LST\\年际热岛\\原始\\2009.tif")
# hotspot_arr = hotspot_ds.GetRasterBand(1).ReadAsArray()
# # 将NaN值替换为0
# hotspot_arr = np.nan_to_num(hotspot_arr)
# # 读取土地类型tiff影像
#
# print(hotspot_arr)
# landuse_ds = gdal.Open("D:\\WME\\CLCD\\CLCD_2009.tif")
# landuse_arr = landuse_ds.GetRasterBand(1).ReadAsArray()
#
# # 将热岛等级按照土地利用类型进行分组，计算每个土地利用类型上的热岛等级的平均值
# unique_landuse = np.unique(landuse_arr)
# hotspot_mean_by_landuse = {}
# for landuse in unique_landuse:
#     if landuse not in [0, 3, 5]:
#         # 选择对应土地类型上的像元值
#         hotspot_by_landuse = hotspot_arr[landuse_arr == landuse]
#         # 排除值为0的像元
#         hotspot_by_landuse = hotspot_by_landuse[hotspot_by_landuse != 0]
#         # 计算平均值
#         hotspot_mean = np.mean(hotspot_by_landuse)
#         hotspot_mean_by_landuse[landuse] = hotspot_mean
#
# # 将结果输出到Excel文件
# df = pd.DataFrame.from_dict(hotspot_mean_by_landuse, orient='index', columns=['平均热岛等级'])
# df.index.name = '土地利用类型'
# # df.to_excel('D:\\WME\\02-热环境\\04-数据\\统计数据\\每个LULC上平均热岛等级\\2001.xlsx')
# print(df)


import glob
import numpy as np
from osgeo import gdal
import pandas as pd

# 定义读取文件夹路径和输出 Excel 文件路径
hotspot_folder = r'D:\WME\02-热环境\04-数据\Tiff数据-LST\年际热岛\原始\clear'
landuse_folder = r'D:\WME\CLCD'
output_file = r'D:\WME\02-热环境\04-数据\统计数据\每个LULC上平均温度\result.xlsx'

# 读取所有热岛和土地利用类型的文件，按年份进行处理
hotspot_files = sorted(glob.glob(f'{hotspot_folder}\\*.tif'))
landuse_files = sorted(glob.glob(f'{landuse_folder}\\*.tif'))

dfs = []
for year, (hotspot_file, landuse_file) in enumerate(zip(hotspot_files, landuse_files), start=2001):
    # 读取热岛和土地利用类型文件
    hotspot_ds = gdal.Open(hotspot_file)
    hotspot_arr = hotspot_ds.GetRasterBand(1).ReadAsArray()
    # 将NaN值替换为0
    hotspot_arr = np.nan_to_num(hotspot_arr)

    landuse_ds = gdal.Open(landuse_file)
    landuse_arr = landuse_ds.GetRasterBand(1).ReadAsArray()

    # 将热岛等级按照土地利用类型进行分组，计算每个土地利用类型上的热岛等级的平均值
    unique_landuse = np.unique(landuse_arr)
    hotspot_mean_by_landuse = {}
    for landuse in unique_landuse:
        if landuse not in [0, 3, 5]:
            # 选择对应土地类型上的像元值
            hotspot_by_landuse = hotspot_arr[landuse_arr == landuse]
            # 排除值为0的像元
            hotspot_by_landuse = hotspot_by_landuse[hotspot_by_landuse != 0]
            # 计算平均值
            hotspot_mean = np.mean(hotspot_by_landuse)
            hotspot_mean_by_landuse[landuse] = hotspot_mean

    # 将结果存入 DataFrame
    df = pd.DataFrame.from_dict(hotspot_mean_by_landuse, orient='index', columns=[f'{year}平均热岛等级'])
    dfs.append(df)

# 合并所有 DataFrame，并输出到 Excel 文件
result_df = pd.concat(dfs, axis=1)
result_df.index.name = '土地利用类型'
result_df.to_excel(output_file)
print(result_df)

