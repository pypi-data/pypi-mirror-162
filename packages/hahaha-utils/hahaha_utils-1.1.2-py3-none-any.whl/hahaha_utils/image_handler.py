# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           image_handler.py
   Description:
   Author:        
   Create Date:    2020/07/15
-------------------------------------------------
   Modify:
                   2020/07/15:
-------------------------------------------------
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import random
import scipy.misc
import scipy.signal
import scipy.ndimage
from matplotlib.font_manager import FontProperties

class ImageHandler(object):

    def noise_remove_cv2(self, image_name, k):
        """
        8邻域降噪
        Args:
            image_name: 图片文件命名
            k: 判断阈值

        Returns:

        """

        def calculate_noise_count(img_obj, w, h):
            """
            计算邻域非白色的个数
            Args:
                img_obj: img obj
                w: width
                h: height
            Returns:
                count (int)
            """
            count = 0
            width, height = img_obj.shape
            for _w_ in [w - 1, w, w + 1]:
                for _h_ in [h - 1, h, h + 1]:
                    if _w_ > width - 1:
                        continue
                    if _h_ > height - 1:
                        continue
                    if _w_ == w and _h_ == h:
                        continue
                    if img_obj[_w_, _h_] < 240:  # 二值化的图片设置为255
                        count += 1
            return count

        img = cv2.imread(image_name, 1)
        # 灰度
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        w, h = gray_img.shape
        for _w in range(w):
            for _h in range(h):
                if _w == 0 or _h == 0:
                    gray_img[_w, _h] = 255
                    continue
                # 计算邻域pixel值小于255的个数
                pixel = gray_img[_w, _h]
                if pixel == 255:
                    continue

                if calculate_noise_count(gray_img, _w, _h) < k:
                    gray_img[_w, _h] = 255
        return gray_img

    def image_gray(self):
        from PIL import Image

        #  load a color image
        im = Image.open('./test/514951_id_front2860F9AB-4DB9-4FB0-944E-3C53BD03545A.jpg')  # 当前目录创建picture文件夹

        #  convert to grey level imageL
        # Lim = im.convert('L')

        # # 浮点算法
        # im = np.array(im)
        # im[:, :, 0] = im[:, :, 0] * 0.3
        # im[:, :, 1] = im[:, :, 1] * 0.59
        # im[:, :, 2] = im[:, :, 2] * 0.11
        # im = np.sum(im, axis=2)

        # # 整数算法
        # im = np.array(im, dtype=np.float32)
        # im[..., 0] = im[..., 0] * 30.0
        # im[..., 1] = im[..., 1] * 59.0
        # im[..., 2] = im[..., 2] * 11.0
        # im = np.sum(im, axis=2)
        # im[..., :] = im[..., :] / 100.0

        # # 平均值算法
        # im = np.array(im, dtype=np.float32)
        # im = np.sum(im, axis=2)
        # im[..., :] = im[..., :] / 3.0

        # # 位移法
        # im = np.array(im, dtype=np.int32)
        # im[..., 0] = im[..., 0] * 28.0
        # im[..., 1] = im[..., 1] * 151.0
        # im[..., 2] = im[..., 2] * 77.0
        # im = np.sum(im, axis=2)
        # arr = [np.right_shift(y.item(), 8) for x in im for y in x]
        # arr = np.array(arr)
        # arr.resize(im.shape)

        # # 单通道法（只取绿色通道）
        # im = np.array(im, dtype=np.int32)
        # im[..., 0] = 0
        # im[..., 2] = 0
        # im = np.sum(im, axis=2)

        #    ++++++++++++二值化+++++++++++++++
        # # 取中间阀值
        # im = np.array(im.convert('L'))
        # im = np.where(im[..., :] < 127, 0, 255)

        # # 取所有像素点灰度的平均值
        # im_gray1 = im.convert('L')
        # im_gray1 = np.array(im_gray1)
        # avg_gray = np.average(im_gray1)
        # im = np.where(im_gray1[..., :] < avg_gray, 0, 255)

        #    ++++++++++++灰度变换+++++++++++++++
        # # 反相
        # im_gray = im.convert('L')
        # im_arr = np.array(im_gray)
        # im = 255 - im_arr

        # # 将像素值变换到100~200之间
        # im_gray = im.convert('L')
        # im_arr = np.array(im_gray)
        # print(im_gray)
        # im = (100.0 / 255) * im_arr + 100
        # self.showimg(Image.fromarray(im))

        # 将像素值求平方，使较暗的像素值变得更小
        im_gray = im.convert('L')
        im_arr = np.array(im_gray)
        im = 255.0 * (im_arr / 255.0) ** 2
        self.showimg(Image.fromarray(im))



        self.showimg(Image.fromarray(im), isgray=True)
        # Lim.save('./test/pice.jpg')

        # #  setup a converting table with constant threshold
        # threshold = 115
        # table = []
        # for i in range(256):
        #     if i < threshold:
        #         table.append(0)
        #     else:
        #         table.append(1)
        #
        # # convert to binary image by the table
        # bim = Lim.point(table, '1')
        #
        # bim.save('./test/picf.png')

    # 获取图片
    def get_image(self, image_path):
        image = Image.open(image_path)

        return image

    # 显示图片
    def showimg(self, image, isgray=False):
        # image =
        plt.axis("off")
        if isgray == True:
            plt.imshow(image, cmap='gray')
        else:
            plt.imshow(image)
        plt.imshow(image)
        plt.show()


if __name__ == '__main__':
    ih = ImageHandler()
    image = ih.get_image('./test/514951_id_front2860F9AB-4DB9-4FB0-944E-3C53BD03545A.jpg')
    # ih.showimg(image)

    # ih.image_gray()

    image = ih.noise_remove_cv2("./test/514951_id_front2860F9AB-4DB9-4FB0-944E-3C53BD03545A.jpg", 4)
    cv2.imshow('img', image)


    cv2.waitKey(100000)