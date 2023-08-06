#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: checker.py
# Author: Rayson.Shi
# Mail: raysonshi@qq.com
# Created Time:  2022-8-5 23:17:34
#############################################
import random
from pycocotools.coco import COCO
import logging
from cocoutils.utils import *


class Checker():
    def __init__(self, coco_path):
        """
        Check dataset outliers and visualization
        :param coco_path (str) : the path of Coco format JSON file
        """
        super(Checker, self).__init__()
        self.coco = COCO(coco_path)
        random.seed(123)
        self.__cat_colors = [[random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)] \
                           for _ in self.coco.cats]

    def drawImg(self, img_dir, img_id, save_dir=None):
        """
        Draw annotations through image index
        :param img_dir (str) : picture save folder
        :param img_id (int) : image id
        :param save_dir (int) : save the picture folder after drawing, if None, it will display directly on the desktop
        """
        img_sample = self.coco.loadImgs(img_id)[0]
        img_name = img_sample["file_name"]
        img_path = os.path.join(img_dir, img_name)
        img = cv2.imread(img_path)
        ano_ids = self.coco.getAnnIds(img_id)
        for a_i in ano_ids:
            ano_sample = self.coco.loadAnns(a_i)[0]
            cat_id = ano_sample["category_id"]
            cat_sample = self.coco.loadCats(cat_id)[0]
            if ano_sample["bbox"] is not None:
                if (len(ano_sample["bbox"]) > 0):
                    drawBox(img, ano_sample["bbox"], self.__cat_colors[cat_id])
                    bt = ano_sample["bbox"][:2]
                    bt[1] = bt[1] - 5
                    drawTxt(img, cat_sample["name"], bt, (0,245,0))
        if save_dir:
            save_path = os.path.join(save_dir, img_name)
            cv2.imwrite(save_path, img)
            print("Saving img to {}".format(save_path))
        else:
            cv2.imshow(img_name, img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def check(self, img_dir=None, log="check.txt"):
        """
        Check annotations and pictures
        :param img_dir (str) : picture save folder, if None, do not check whether the picture exists
        :param log (path) : address to save inspection results
        """
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log, mode='w')
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("%(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        img_ids = self.coco.getImgIds()
        unique_img_ids = set(img_ids)
        ano_ids = self.coco.getAnnIds()
        unique_ano_ids = set(ano_ids)
        img_names = []
        cat_ids = self.coco.getCatIds()
        cats = self.coco.loadCats(cat_ids)
        wrong_ano_number = 0
        assert len(img_ids) > 0, "the images is empty!"
        assert len(ano_ids) > 0, "the annotations is empty!"
        assert len(cats) > 0, "the categories is empty!"
        for ig_id in img_ids:
            img_sample = self.coco.loadImgs(ig_id)[0]
            img_w = img_sample["width"]
            img_h = img_sample["height"]
            img_names.append(img_sample["file_name"])
            if img_dir:
                img_path = os.path.join(self.img_dir, img_sample["file_name"])
                if not os.path.exists(img_path):
                    logger.info("img id: {} path {} result: Path does not exist! ".format(ig_id, img_path))
            t_ano_ids = self.coco.getAnnIds(ig_id)
            if len(t_ano_ids) == 0:
                logger.info("img id: {} result: No annotation information! ".format(ig_id, img_path))
                wrong_ano_number += 1
            for ano_id in t_ano_ids:
                ano_sample = self.coco.loadAnns(ano_id)[0]
                cat_id = ano_sample["category_id"]
                if cat_id not in cat_ids:
                    logger.info("img id: {} ano id: {} category id: {} result: No annotation information!".format(ig_id, ano_id, cat_id))
                    wrong_ano_number += 1
                xywh = ano_sample["bbox"]
                wrong_ano_number = checkXywh(wrong_ano_number, ig_id, ano_id, xywh, img_w, img_h, logger)
        if len(unique_ano_ids) != len(ano_ids):
            logger.info(
                "Mismatch! the total ano id number is: {}, remove duplicate ano number is {}" \
                  .format(len(ano_ids), len(unique_ano_ids)))
        if len(unique_img_ids) != len(img_ids):
            logger.info(
                "Mismatch! the total img id number is: {}, remove duplicate img number is {}" \
                  .format(len(img_ids), len(unique_img_ids)))
        unique_img_names = set(img_names)
        if len(unique_img_names) != len(img_names):
            logger.info(
                "Mismatch! the total img name number is: {},remove duplicate img name number is {}" \
                  .format(len(img_names), len(unique_img_names)))
        print("Total annotation number is {}, the wrong annotation number is {}".format(len(ano_ids), wrong_ano_number))
        print("Saving check log to {}".format(log))

    def repair(self, save_path, img_dir=None):
        """
        Repair annotations
        :param save_path (str) : save the repaired coco address
        :param img_dir (str) : picture save folder, if None, do not check whether the picture exists
        """
        new_img_id = 0
        new_ano_id = 0
        new_coco = COCO_FORMAT
        cat_ids = self.coco.getCatIds()
        img_ids = self.coco.getImgIds()
        for ig_i in img_ids:
            img_info = self.coco.loadImgs(ig_i)[0]
            img_h = img_info["height"]
            img_w = img_info["width"]
            img_name = img_info["file_name"]
            if img_dir:
                img_path = os.path.join(img_dir, img_name)
                if not os.path.exists(img_path):
                    print("img path {} not exists!".format(img_path))
                    continue
            ano_ids = self.coco.getAnnIds(ig_i)
            if len(ano_ids) == 0:
                print("img id {} have't annotations!".format(ig_i))
                continue
            flag = 0
            for a_i in ano_ids:
                ano_info = self.coco.loadAnns(a_i)[0]
                cat_id = ano_info["category_id"]
                if cat_id not in cat_ids:
                    print("img id: {} ano id: {} category id: {} result: No annotation information!".format(ig_i, a_i,cat_id))
                    continue
                xywh = ano_info["bbox"]
                xywh = repairBox(xywh, img_h, img_w)
                ano_info["bbox"] = xywh
                ano_info["image_id"] = new_img_id
                ano_info["id"] = new_ano_id
                new_coco["annotations"].append(ano_info)
                new_ano_id += 1
                flag += 1
            if flag != 0:
                img_info["id"] = new_img_id
                new_coco["images"].append(img_info)
                new_img_id += 1
        new_coco["categories"] = self.coco.loadCats(cat_ids)
        with open(save_path, "w") as f:
            json.dump(new_coco, f, cls=MyEncoder)
            print("Complete data conversion to {}".format(save_path))


if __name__=="__main__":
    coco = "coco.json"
    repair_coco = "repair_coco.json"
    img_dir = "result"
    img_id = 2
    check = Checker(coco)

    check.drawImg(img_id)

    check.check()

    check.repair(repair_coco)








