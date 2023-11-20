import numpy as np
import rasterio

# 输入温度图像文件路径
input_file = r"D:\\WME\\02-热环境\\04-数据\\Tiff数据-LST\\年际热岛\\原始\\2019_2.tif"

# 输出热岛等级图像文件路径
output_file = r"D:\\WME\\02-热环境\\04-数据\\Tiff数据-LST\年际热岛\\重分类\\2019_2.tif"

# 读取温度图像
with rasterio.open(input_file) as src:
    profile = src.profile
    temperature = src.read(1)

    # 创建热岛等级数组，并初始化为 0
    heat_island = np.zeros_like(temperature)

    # 获取不包含 NaN 值的布尔掩码
    valid_mask = ~np.isnan(temperature)
    print(np.nanmean(temperature[valid_mask]))
    print(np.nanstd(temperature[valid_mask]))
    # 根据阈值划分温度图像的热岛等级，只处理不包含 NaN 值的像素
    high_threshold = np.nanmean(temperature[valid_mask]) + np.nanstd(temperature[valid_mask])
    high_threshold_2 = np.nanmean(temperature[valid_mask]) + 0.5 * np.nanstd(temperature[valid_mask])
    low_threshold = np.nanmean(temperature[valid_mask]) - 0.5 * np.nanstd(temperature[valid_mask])
    low_threshold_2 = np.nanmean(temperature[valid_mask]) - np.nanstd(temperature[valid_mask])

    # 使用布尔掩码来筛选出不包含 NaN 值的像素，并根据条件进行替换
    heat_island[(temperature > high_threshold) & valid_mask] = 5
    heat_island[(temperature <= high_threshold) & (temperature > high_threshold_2) & valid_mask] = 4
    heat_island[(temperature <= high_threshold_2) & (temperature > low_threshold) & valid_mask] = 3
    heat_island[(temperature <= low_threshold) & (temperature > low_threshold_2) & valid_mask] = 2
    heat_island[(temperature <= low_threshold_2) & valid_mask] = 1

# 将结果保存为新的栅格图像文件
with rasterio.open(output_file, 'w', **profile) as dst:
    dst.write(heat_island, 1)

with rasterio.open(output_file) as src:
    heat_island = src.read(1)
    transform = src.transform

    # 计算每个值的频数
    hist, _ = np.histogram(heat_island, bins=np.arange(1, 8))

    # 计算每个值所占的面积百分比
    area_percentage = hist / np.sum(hist) * 100

    # 输出结果
    print("Heat Island Level\tArea Percentage (%)")
    for i in range(1, 6):
        print(f"{i}\t\t\t{area_percentage[i-1]:.2f}")