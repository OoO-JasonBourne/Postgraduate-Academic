import numpy as np
import rasterio
import pandas as pd

UHI_NDBI_list = []
UHI_NDVI_list = []
UHI_NDWI_list = []
LST_NDBI_list = []
LST_NDVI_list = []
LST_NDWI_list = []
def corrCal(temp, index):
    # 加载地表温度和NDVI的TIFF影像
    with rasterio.open(temp) as temp_ds, rasterio.open(index) as ndvi_ds:
    # with rasterio.open('./UHI/2001.tif') as temp_ds, rasterio.open('./NDWI/NDWI_2001.tif') as ndvi_ds:
        # 读取地表温度和NDVI数据
        temp_data = temp_ds.read(1)
        ndvi_data = ndvi_ds.read(1)

        # 将 NoData 值设为 NaN
        temp_data[temp_data == temp_ds.nodata] = np.nan
        ndvi_data[ndvi_data == ndvi_ds.nodata] = np.nan

        # 排除 NaN 值和 0 值
        valid_mask = (~np.isnan(temp_data)) & (~np.isnan(ndvi_data)) & (temp_data != 0) & (ndvi_data != 0)

        # # 排除 NaN 值和 0 值以及小于0的值
        # valid_mask = (~np.isnan(temp_data)) & (~np.isnan(ndvi_data)) & (temp_data != 0) & (ndvi_data != 0) & (ndvi_data >= 0)

        # 提取有效数据
        valid_temp_data = temp_data[valid_mask]
        valid_ndvi_data = ndvi_data[valid_mask]
        # print(valid_ndvi_data)

        # 计算相关系数
        correlation_coefficient = np.corrcoef(valid_temp_data, valid_ndvi_data)[0, 1]

        # 打印结果
        # print("相关系数：", correlation_coefficient)
        return correlation_coefficient
def corrCal_NDVI(temp, index):
    # 加载地表温度和NDVI的TIFF影像
    with rasterio.open(temp) as temp_ds, rasterio.open(index) as ndvi_ds:
    # with rasterio.open('./UHI/2001.tif') as temp_ds, rasterio.open('./NDWI/NDWI_2001.tif') as ndvi_ds:
        # 读取地表温度和NDVI数据
        temp_data = temp_ds.read(1)
        ndvi_data = ndvi_ds.read(1)

        # 将 NoData 值设为 NaN
        temp_data[temp_data == temp_ds.nodata] = np.nan
        ndvi_data[ndvi_data == ndvi_ds.nodata] = np.nan

        # # 排除 NaN 值和 0 值
        # valid_mask = (~np.isnan(temp_data)) & (~np.isnan(ndvi_data)) & (temp_data != 0) & (ndvi_data != 0)

        # 排除 NaN 值和 0 值以及小于0的值
        valid_mask = (~np.isnan(temp_data)) & (~np.isnan(ndvi_data)) & (temp_data != 0) & (ndvi_data != 0) & (ndvi_data >= 0)

        # 提取有效数据
        valid_temp_data = temp_data[valid_mask]
        valid_ndvi_data = ndvi_data[valid_mask]
        # print(valid_ndvi_data)

        # 计算相关系数
        correlation_coefficient = np.corrcoef(valid_temp_data, valid_ndvi_data)[0, 1]

        # 打印结果
        # print("相关系数：", correlation_coefficient)
        return correlation_coefficient
for i in range(2001, 2021):
    # 城市热岛 - NDBI
    UHI = './UHI/' + str(i) + '.tif'
    LST = './LST/LST_' + str(i) + '.tif'

    NDBI = './NDBI/NDBI_' + str(i) + '.tif'
    NDVI = './NDVI/NDVI_' + str(i) + '.tif'
    NDWI = './NDWI/NDWI_' + str(i) + '.tif'

    UHI_NDBI = corrCal(UHI, NDBI)
    UHI_NDVI = corrCal_NDVI(UHI, NDVI)
    UHI_NDWI = corrCal(UHI, NDWI)
    LST_NDBI = corrCal(LST, NDBI)
    LST_NDVI = corrCal_NDVI(LST, NDVI)
    LST_NDWI = corrCal(LST, NDWI)

    UHI_NDBI_list.append(UHI_NDBI)
    UHI_NDVI_list.append(UHI_NDVI)
    UHI_NDWI_list.append(UHI_NDWI)
    LST_NDBI_list.append(LST_NDBI)
    LST_NDVI_list.append(LST_NDVI)
    LST_NDWI_list.append(LST_NDWI)



print('UHI_NDBI_list', UHI_NDBI_list)
print('UHI_NDVI_list', UHI_NDVI_list)
print('UHI_NDWI_list', UHI_NDWI_list)
print('LST_NDBI_list', LST_NDBI_list)
print('LST_NDVI_list', LST_NDVI_list)
print('LST_NDWI_list', LST_NDWI_list)

# 创建一个字典，包含这六个数组
data = {
    'UHI_NDBI': UHI_NDBI_list,
    'UHI_NDVI': UHI_NDVI_list,
    'UHI_NDWI': UHI_NDWI_list,
    'LST_NDBI': LST_NDBI_list,
    'LST_NDVI': LST_NDVI_list,
    'LST_NDWI': LST_NDWI_list
}


# 创建一个DataFrame对象
df = pd.DataFrame(data)

# 保存为Excel文件
df.to_excel('output.xlsx', index=False)