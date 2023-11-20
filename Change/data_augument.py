import numpy as np
import cv2
import random
from tqdm import trange
import os

img_w = 256
img_h = 256
data_path='F:/DeskTop/data/1/'
save_path='F:/DeskTop/data/'
image_sets = os.listdir(data_path+'image1')
#print(image_sets)
def gamma_transform(img, gamma):
    gamma_table = [np.power(x / 255.0, gamma) * 255.0 for x in range(256)]
    gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)
    return cv2.LUT(img, gamma_table)

def random_gamma_transform(img, gamma_vari):
    log_gamma_vari = np.log(gamma_vari)
    alpha = np.random.uniform(-log_gamma_vari, log_gamma_vari)
    gamma = np.exp(alpha)
    return gamma_transform(img, gamma)
    

def rotate(xb,yb,angle):
    M_rotate = cv2.getRotationMatrix2D((img_w/2, img_h/2), angle, 1)
    xb = cv2.warpAffine(xb, M_rotate, (img_w, img_h))
    yb = cv2.warpAffine(yb, M_rotate, (img_w, img_h))
    return xb,yb
    
def blur(img):
    img = cv2.blur(img, (3, 3));
    return img

def add_noise(img):
    for i in range(200): #添加点噪声
        temp_x = np.random.randint(0,img.shape[0])
        temp_y = np.random.randint(0,img.shape[1])
        img[temp_x][temp_y] = 255
    return img
    
    
def data_augment(xb,yb):
    if np.random.random() < 0.25:
        xb,yb = rotate(xb,yb,90)
    if np.random.random() < 0.25:
        xb,yb = rotate(xb,yb,180)
    if np.random.random() < 0.25:
        xb,yb = rotate(xb,yb,270)
    if np.random.random() < 0.25:
        xb = cv2.flip(xb, 1)  # flipcode > 0：沿y轴翻转
        yb = cv2.flip(yb, 1)
        
    if np.random.random() < 0.25:
        xb = random_gamma_transform(xb,1.0)
        
    if np.random.random() < 0.25:
        xb = blur(xb)
    
    if np.random.random() < 0.2:
        xb = add_noise(xb)
        
    return xb,yb

def creat_dataset(image_num, mode):
    print('creating dataset...')
    image_each = image_num / len(image_sets)
    g_count = 0
    for i in trange(len(image_sets)):
        count = 0
        src_img_1 = cv2.imread(data_path+'image1/' + image_sets[i])  # 3 channels
        src_img_2 = cv2.imread(data_path + 'image2/' + image_sets[i])  # 3 channels
        label_img = cv2.imread(data_path + 'label/' + image_sets[i])  # 3 channel
        X_height,X_width,_ = src_img_1.shape
        while count < image_each:
            random_width = random.randint(0, X_width - img_w - 1)
            random_height = random.randint(0, X_height - img_h - 1)
            src_roi_1 = src_img_1[random_height: random_height + img_h, random_width: random_width + img_w,:]
            src_roi_2 = src_img_2[random_height: random_height + img_h, random_width: random_width + img_w, :]
            label_roi = label_img[random_height: random_height + img_h, random_width: random_width + img_w,:]
            if mode == 'augment':
                src_roi_1,label_roi = data_augment(src_roi_1,label_roi)
                src_roi_2, label_roi = data_augment(src_roi_2, label_roi)
            if count<image_each*0.75:
                cv2.imwrite((save_path + 'cut-change_1/image/%d.png' % g_count), src_roi_1)
                cv2.imwrite((save_path + 'cut-change_1/label/%d.png' % g_count), label_roi)
                cv2.imwrite((save_path + 'cut-change_2/image/%d.png' % g_count), src_roi_2)
                cv2.imwrite((save_path + 'cut-change_2/label/%d.png' % g_count), label_roi)
            else:
                cv2.imwrite((save_path+'cut-change_1/validation/image/%d.png' % g_count),src_roi_1)
                cv2.imwrite((save_path+'cut-change_1/validation/label/%d.png' % g_count),label_roi)
                cv2.imwrite((save_path + 'cut-change_2/validation/image/%d.png' % g_count), src_roi_2)
                cv2.imwrite((save_path + 'cut-change_2/validation/label/%d.png' % g_count), label_roi)
            count += 1 
            g_count += 1
mode='augment'
creat_dataset(100*len(image_sets),mode)
