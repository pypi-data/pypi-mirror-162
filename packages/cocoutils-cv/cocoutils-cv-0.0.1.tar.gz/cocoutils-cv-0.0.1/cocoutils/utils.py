#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: utils.py
# Author: Rayson.Shi
# Mail: raysonshi@qq.com
# Created Time:  2022-8-5 23:17:34
#############################################
import os
import numpy as np
import cv2
import json
import copy
import datetime


LICENSE = {
"id": None, "name": None, "url": None,
}


COCO_FORMAT  = {
"info": [], "images": [], "annotations": [], "categories":[], "licenses": LICENSE
}


INFO = {
"year": None, "version": None, "description": None, "contributor": None, "url": None, "date_created": None,
}


IMAGE = {
"id": None, "width": None, "height": None, "file_name": None, "license": None, "flickr_url": None, "coco_url": None, "date_captured": None,
}


ANNOTATION = {
"id": None, "image_id": None, "category_id": None, "segmentation": None, "area": None, "bbox": None, "iscrowd": 0,
}


CATEGORIE = {
"id": None, "name": None, "supercategory": None,
}


def xywh2xyxy(xywh):
    x2 = xywh[2] + xywh[0]
    y2 = xywh[3] + xywh[1]
    return [xywh[0], xywh[1], x2, y2]


def xyxy2xywh(xyxy):
    w = xyxy[2] - xyxy[0]
    h = xyxy[3] - xyxy[1]
    return [xyxy[0], xyxy[1], w, h]


def getAndCheck(root, name, length=None):
    vals = root.findall(name)
    if len(vals) == 0:
        raise NotImplementedError('Can not find %s in %s.' % (name, root.tag))
    if length and len(vals) != length:
        raise NotImplementedError('The size of %s is supposed to be %d, but is %d.' % (name, length, len(vals)))
    if length == 1:
        vals = vals[0]
    return vals


def checkImgEists(name, formats=[".jpg", ".png"]):
    for f in formats:
        path = os.path.join(name, f)
        if os.path.exists(path):
            return path
    return None


def setImageSample(img_id, img_name, h, w):
    img_sample = copy.deepcopy(IMAGE)
    img_sample["id"] = img_id
    img_sample["file_name"] = img_name
    img_sample["height"] = h
    img_sample["width"] = w
    return img_sample


def setAnnotationSample(ano_id, img_id, cat_id, bbox, polygon=None):
    ano_sample = copy.deepcopy(ANNOTATION)
    ano_sample["id"] = ano_id
    ano_sample["image_id"] = img_id
    ano_sample["category_id"] = cat_id
    ano_sample["bbox"] = list(map(int, bbox))
    ano_sample["area"] = bbox[2] * bbox[3]
    ano_sample["segmentation"] = polygon
    return ano_sample


def setCategorySample(cat, cat_names):
    if cat in cat_names:
        return cat_names.index(cat),None
    else:
        cat_id = len(cat_names)
        cat_sample = copy.deepcopy(CATEGORIE)
        cat_sample["id"] = cat_id
        cat_sample["name"] = cat
        cat_sample["supercategory"] = None
        cat_names.append(cat)
        return cat_id, cat_sample


def points2xyxy(points):
    points = np.array(points).reshape(-1, 2)
    x1 = np.min(points[:, 0])
    x2 = np.max(points[:, 0])
    y1 = np.min(points[:, 1])
    y2 = np.max(points[:, 1])
    return [x1, y1, x2, y2]


def yoloBox2xyxy(yolo_box, img_h, img_w):
    center_x = int(img_w * yolo_box[0])
    center_y = int(img_h * yolo_box[1])
    box_w = int(img_w * yolo_box[2])
    box_h = int(img_h * yolo_box[3])
    x1 = center_x - int(box_w/2)
    x2 = center_x + int(box_w/2)
    y1 = center_y - int(box_h/2)
    y2 = center_y + int(box_h/2)
    return [x1, y1, x2, y2]


def checkXyxy(xyxy, img_w, img_h):
    x1, y1, x2, y2 = xyxy
    if any([x1<0, y1<0, x2<0, y2<0]):
        print("illegal input xyxy lower than 0: {},{},{},{}".format(x1,y1,x2,y2))
        return None
    if any([x1>img_w, x2>img_w]) or any([y1>img_h, y2>img_h]):
        print("illegal input xyxy exceeds picture size: {},{},{},{}".format(x1, y1, x2, y2))
        return None
    if any([x2-x1<2, y2-y1<2]):
        print("illegal input xyxy: {},{},{},{}".format(x1, y1, x2, y2))
        return None
    return xyxy


def repairBox(xywh, img_h, img_w):
    xyxy = xywh2xyxy(xywh)
    x1 = np.clip(xyxy[0], 1, img_w-1)
    x2 = np.clip(xyxy[2], 1, img_w-1)
    y1 = np.clip(xyxy[1], 1, img_h-1)
    y2 = np.clip(xyxy[3], 1, img_h-1)
    xywh = xyxy2xywh([x1, y1, x2, y2])
    return xywh


def drawBox(img, xywh, color):
    xyxy = xywh2xyxy(xywh)
    cv2.rectangle(img, tuple(xyxy[:2]), tuple(xyxy[2:]), color, 2)


def drawTxt(img, txt, point, color):
    cv2.putText(img, txt, tuple(point), cv2.FONT_HERSHEY_SIMPLEX, 0.75, tuple(color), 2)


def drawPolygons(img, polygons, color, alpha=0.7):
    mask = img.copy()
    cv2.fillPoly(mask, [polygons], color)
    add_img = cv2.addWeighted(img, alpha, mask, 1-alpha)
    return add_img


def drawKeypoints(img, keypoints, skeleton, point_color=[0, 0, 255], line_color=[0, 255, 0]):
    for sk in skeleton:
        pt1 = keypoints[sk[0]]
        pt2 = keypoints[sk[1]]
        cv2.line(img, pt1, pt2, line_color, 2)
    for p in keypoints:
        cv2.circle(img, p, 4, point_color)


def checkXywh(wrong_ano_number, img_id, ano_id, xywh, img_w, img_h, log):
    xyxy = xywh2xyxy(xywh)
    x1, y1, x2, y2 = xyxy
    if any([x1<0, y1<0, x2<0, y2<0]):
        log.info("img id: {} ano id: {}  xywh: {} img w: {} img h: {} result: Invalid values!".format(img_id, ano_id, xywh, img_w, img_h))
        wrong_ano_number += 1
    if any([x1>img_w, x2>img_w]) or any([y1>img_h, y2>img_h]):
        log.info("img id: {} ano id: {}  xywh: {} img w: {} img h: {} result: Over the border!".format(img_id, ano_id, xywh, img_w, img_h))
        wrong_ano_number += 1
    if any([x2-x1<2, y2-y1<2]):
        log.info("img id: {} ano id: {}  xywh: {} img w: {} img h: {} result: Invalid values!".format(img_id, ano_id, xywh, img_w, img_h))
        wrong_ano_number += 1
    return wrong_ano_number


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        elif isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return super(MyEncoder, self).default(obj)
