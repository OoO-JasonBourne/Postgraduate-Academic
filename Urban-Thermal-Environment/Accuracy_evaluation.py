import numpy as np
import rasterio


path_ref = 'D:/WME/02-热环境/04-数据/Tiff数据-LST/精度评定/img_20080519.tif'
path_new = 'D:/WME/02-热环境/04-数据/Tiff数据-LST/精度评定/20080519_finished.tif'
# res = calculate_metrics(path_ref, path_new)
# print(res)

# 读取两幅影像
with rasterio.open(path_ref) as src1, rasterio.open(path_new) as src2:
    # 确认两幅影像的尺寸、分辨率和投影等参数都一致
    # assert src1.width == src2.width and src1.height == src2.height
    # assert src1.res == src2.res
    # assert src1.crs == src2.crs

    # 读取影像像素值
    img1 = src1.read(1)
    img2 = src2.read(1)
    img1 = np.nan_to_num(img1)
    img2 = np.nan_to_num(img2)
    # 计算像素值范围和量化级别
    min_val, max_val = np.minimum(img1.min(), img2.min()), np.maximum(img1.max(), img2.max())
    q = max_val - min_val

    # 计算ERGAS指标
    M, N = src1.width, src1.height
    ergas = 100 * np.sqrt(np.mean(np.square((img1 - img2) / img1))) / np.sqrt(q) * np.sqrt(M * N) / np.sqrt(M + N)

    # 计算PSNR指标
    psnr = 10 * np.log10((q ** 2) / np.mean(np.square(img1 - img2)))

    # 计算RMSE指标
    rmse = np.sqrt(np.mean(np.square(img1 - img2)))
    # diff = img1 - img2
    # rmse = np.sqrt(np.nanmean(diff ** 2))
    # 计算SAM指标
    a = np.stack((img1, img2))
    a = np.transpose(a, [1, 2, 0])
    sam = np.arccos(np.clip(np.sum(a[..., 0] * a[..., 1], axis=-1) / (
                np.linalg.norm(a[..., 0], axis=-1) * np.linalg.norm(a[..., 1], axis=-1)), -1.0, 1.0))
    sam = np.rad2deg(sam)

    # 计算CC指标
    cc = np.corrcoef(img1.flatten(), img2.flatten())[0, 1]

    # 打印结果
    print('ERGAS:', ergas)
    print('PSNR:', psnr)
    print('RMSE:', rmse)
    print('SAM:', sam)
    print('CC:', cc)

