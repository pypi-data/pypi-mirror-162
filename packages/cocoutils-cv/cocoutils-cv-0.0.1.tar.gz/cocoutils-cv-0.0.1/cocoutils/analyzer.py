#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: analyzer.py
# Author: Rayson.Shi
# Mail: raysonshi@qq.com
# Created Time:  2022-8-5 23:17:34
#############################################

import collections
import numpy as np
from pycocotools.coco import COCO
from cocoutils.drwaUtils import DrawUtils


class Analyzer:
    def __init__(self, coco_path, save_path=None, map_size=8):
        """
        Analyze coco datasets through charts
        :param coco_path (str) : the path of Coco format JSON file
        :param save_path (dir) : the dir to save the chart, if None, it will display directly on the desktop
        :param map_size (int)  : Determine the number of heatmap grids
        """
        super(Analyzer, self).__init__()
        self.coco = COCO(coco_path)
        self.map_size = map_size
        self.s_threshold = 32 * 32
        self.m_threshold = 96 * 96
        self.__drawUtil = DrawUtils(save_path)
        self.__create_data()
        self.__draw()

    def __create_data(self):
        img_ids = self.coco.getImgIds()
        ano_ids = self.coco.getAnnIds()
        cat_ids = self.coco.getCatIds()
        imgs_num = len(img_ids)
        anos_num = len(ano_ids)
        cat_num = len(cat_ids)
        self.imgs_data = np.zeros((imgs_num, 4))
        self.anos_data = np.zeros((anos_num, 8))
        self.cats_data = np.zeros((cat_num, 2))
        for ig_id in img_ids:
            img_sample = self.coco.loadImgs(ig_id)[0]
            self.imgs_data[ig_id, 0] = img_sample["width"]
            self.imgs_data[ig_id, 1] = img_sample["height"]
            img_area = img_sample["width"] * img_sample["height"]
            relate_anos_ids = self.coco.getAnnIds(ig_id)
            self.imgs_data[ig_id, 3] = len(relate_anos_ids)
            for ano_id in relate_anos_ids:
                ano_sample = self.coco.loadAnns(ano_id)[0]
                self.anos_data[ano_id, 0] = ano_sample["area"]
                self.anos_data[ano_id, 1] = self.__calObjSize(ano_sample["area"], self.s_threshold, self.m_threshold)
                self.anos_data[ano_id, 2] = ano_sample['area'] / img_area
                self.anos_data[ano_id, 3] = ano_sample["bbox"][3] / ano_sample["bbox"][2]
                self.anos_data[ano_id, 4] = ano_sample["category_id"]
                self.anos_data[ano_id, 5], self.anos_data[ano_id, 6] = self.__calMapIndex(ano_sample["bbox"], \
                                                                                   self.map_size,      \
                                                                                   img_sample["height"], \
                                                                                   img_sample["width"])
                self.anos_data[ano_id, 7] = ano_sample["image_id"]
        for c_id in cat_ids:
            self.cats_data[:, 0] = self.coco.getImgIds(catIds=[c_id])[0]
            self.cats_data[:, 1] = sum(self.anos_data[:, 4] == c_id)

    def __draw(self):
        overall_labels, overall_values = self.__calOverallInformation()
        self.__drawUtil.drawBar("General information", "name", "number", overall_labels, overall_values)

        img_size_labels, img_size_values = self.__calImgSize()
        self.__drawUtil.drawBar("Image size number", "image size", "image number", img_size_labels, img_size_values, 10)

        obj_number_labels, img_number_values = self.__calImgObjNumber()
        self.__drawUtil.drawBar("Number of targets per picture", "object number", "image number", obj_number_labels, img_number_values)

        cats_labels, cats_values = self.__calCategoryNumber()
        self.__drawUtil.drawPie("Quantity proportion of each category", cats_labels, cats_values)
        self.__drawUtil.drawBar("Number of each category", "category name", "category number", cats_labels, cats_values)

        cat_labels, img_values = self.__calCatImgNumber()
        self.__drawUtil.drawBar("Number of pictures in each category", "category name", "image number",
                              cat_labels, img_values)

        size_label, size_values = self.__calAbsArea()
        self.__drawUtil.drawBar("Absolute target area", "object size", "object number", size_label, size_values)

        relative_size = self.__calRealateSize()
        self.__drawUtil.drawHist("Object relative area distribution", "relative size", "number", relative_size)

        object_areas = self.anos_data[:, 0]
        self.__drawUtil.drawHist("Object area distribution", "area", "number", object_areas, 100)

        map_values = self.__calMapDist()
        labels = [str(i) for i in range(self.map_size)]
        self.__drawUtil.drawHeatmap("Object position distribution", labels, labels, map_values)

        aspect_ratio = self.__calAspectRatio()
        self.__drawUtil.drawHist("Aspect ratio distribution", "Aspect ratio", "number", aspect_ratio)

    def __calOverallInformation(self):
        labels = ["image number", "annotation number", "category number"]
        values = [self.imgs_data.shape[0], self.anos_data.shape[0], self.cats_data.shape[0]]
        return labels, values

    def __calImgSize(self):
        labels = []
        values = []
        unique_ws = np.unique(self.imgs_data[:, 0])
        for u_w in unique_ws:
            realate_indexs = np.where(self.imgs_data[:, 0]==u_w)
            realte_hs = self.imgs_data[:, 1][realate_indexs]
            unique_hs = np.unique(realte_hs)
            for u_h in unique_hs:
                hs = np.where(realte_hs==u_h)[0]
                la = "(" + str(u_w) + "," + str(u_h) +")"
                labels.append(la)
                val = hs.size
                values.append(val)
        return labels, values

    def __calImgObjNumber(self):
        data = collections.Counter(self.imgs_data[:, 3])
        labes = [int(x) for x in list(data.keys())]
        values = list(data.values())
        return labes, values

    def __calCategoryNumber(self):
        labels = []
        values = []
        cat_ids = self.coco.getCatIds()
        for c_i in cat_ids:
            la = self.coco.loadCats(c_i)[0]["name"]
            val = np.where(self.anos_data[:, 4]==c_i)[0].size
            labels.append(la)
            values.append(val)
        return labels, values

    def __calAbsArea(self):
        labels = ["small", "medium", "big"]
        values = []
        for i in range(3):
            val = np.where(self.anos_data[:, 1]==i)[0].size
            values.append(val)
        return labels, values

    def __calRealateSize(self):
        return self.anos_data[:, 2]

    def __calMapDist(self):
        values = np.zeros((self.map_size, self.map_size))
        for i in range(self.map_size):
            for j in range(self.map_size):
                x_indexs = np.where(self.anos_data[:, 5] == i)
                r_y = self.anos_data[:, 6][x_indexs]
                val = np.where(r_y==j)[0].size
                values[i, j] = val
        return values

    def __calAspectRatio(self):
        return self.anos_data[:, 3]

    def __calCatImgNumber(self):
        values = []
        cat_ids = self.coco.getCatIds()
        label = [x["name"] for x in self.coco.loadCats(cat_ids)]
        for c_i in cat_ids:
            index = np.where(self.anos_data[:, 4] == c_i)
            related_img_id = self.anos_data[:, 7][index]
            val = np.unique(related_img_id).size
            values.append(val)
        return label, values

    def __calObjSize(self, area, s_thredshold, m_threshold):
        return 0 if area < s_thredshold else (1 if area < m_threshold else 2)

    def __calMapIndex(self, bbox, map_size, img_h, img_w):
        center_x = bbox[0] + int(bbox[2] / 2)
        center_y = bbox[1] + int(bbox[3] / 2)
        x_index = int((center_x / img_w) * map_size)
        y_index = int((center_y / img_h) * map_size)
        return x_index, y_index

if __name__=="__main__":
    coco = r"coco.json"
    analysis_result = r"analysis_result"
    Analyzer(coco, analysis_result)


