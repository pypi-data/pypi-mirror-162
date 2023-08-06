#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: transfer.py
# Author: Rayson.Shi
# Mail: raysonshi@qq.com
# Created Time:  2022-8-5 23:17:34
#############################################
from pycocotools.coco import COCO
import xml.etree.ElementTree as ET
from tqdm import tqdm
from cocoutils.utils import *


class Transfer:
    def __init__(self):
        super(Transfer, self).__init__()
        """
        Only detection format conversion is supported
        """
        self.coco_data = COCO_FORMAT
    
    def custom(self, dst_coco, img_abs_paths, cats, bboxes):
        """
        Custom dataset conversion to coco format
        :param dst_coco (str) : the path of Coco format JSON file to save
        :param img_abs_pathsh (list) : picture absolute address list, ["path/to/img1.jpg", "path/to/img2.jpg",...]
        :param img_abs_pathsh (list) : category name list, [["cat1","cat1","cat2"], ["cat2"],...]
        :param bboxes (list)  : xywh list, [[xywh1,xywh2,xyw3], [xywh4],...]
        The three must match one by one
        """
        assert len(cats) == len(bboxes), "The number of categories and Bboxes must be equal!"
        img_id, ano_id, cats_name = 0, 0, []
        for i, ig_p in enumerate(img_abs_paths):
            img_name = os.path.basename(ig_p)
            img = cv2.imread(ig_p)
            h, w, _ = img.shape
            img_sample = setImageSample(img_id, img_name, h, w)
            for j, (cat, xywh) in enumerate(zip(cats[i], bboxes[i])):
                cat_id, cat_sample = setCategorySample(cat, cats_name)
                if cat_sample:
                    self.coco_data["categories"].append(cat_sample)
                else:
                    ano_sample = setAnnotationSample(ano_id, img_id, cat_id, xywh)
                self.coco_data["annotations"].append(ano_sample)
                ano_id += 1
            self.coco_data["images"].append(img_sample)
            img_id += 1
        with open(dst_coco, "w") as f2:
            json.dump(self.coco_data, f2, cls=MyEncoder)
        print("Complete data conversion to {}".format(dst_coco))

    def lableme2coco(self, dst_coco, labelme_dir):
        """
        Labelme format to coco format
        :param dst_coco (str) : the path of Coco format JSON file to save
        :param labelme_dir (str) : JSON file folder
        """
        img_id, ano_id, cat_names = 0, 0, []
        js_paths = [os.path.join(labelme_dir, x) for x in os.listdir(labelme_dir) if x.endswith(".json")]
        for js_p in tqdm(js_paths):
            with open(js_p, "r") as f:
                data = json.load(f)
            img_name = data["imagePath"]
            img_h = data["imageHeight"]
            img_w = data["imageWidth"]
            img_sample = setImageSample(img_id, img_name, img_h, img_w)
            labelme_anos = data["shapes"]
            if len(labelme_anos) == 0:
                continue
            flag = ano_id
            for ano in labelme_anos:
                if ano["shape_type"] != "rectangle":
                    print("{} format not supported!".format(ano["shape_type"]))
                    continue
                cat = ano["label"]
                cat_id, cat_sample = setCategorySample(cat, cat_names)
                if cat_sample:
                    self.coco_data["categories"].append(cat_sample)
                points = ano["points"]
                xyxy = points2xyxy(points)
                xyxy = checkXyxy(xyxy, img_w, img_h)
                if xyxy is None:
                    continue
                xywh = xyxy2xywh(xyxy)
                anos_sample = setAnnotationSample(ano_id, img_id, cat_id, xywh)
                self.coco_data["annotations"].append(anos_sample)
                ano_id += 1
            if flag == ano_id:
                continue
            self.coco_data["images"].append(img_sample)
            img_id += 1
        with open(dst_coco, "w") as f2:
            json.dump(self.coco_data, f2, cls=MyEncoder)
        print("Complete data conversion to {}".format(dst_coco))

    def voc2coco(self, dst_coco, xml_dir):
        """
        voc format to coco format
        :param dst_coco (str) : the path of Coco format JSON file to save
        :param xml_dir (str) : XML file folder
        """
        img_id, ano_id, cat_names = 0, 0, []
        xml_names = [x for x in os.listdir(xml_dir) if x.endswith(".xml")]
        for name in tqdm(xml_names):
            xml_path = os.path.join(xml_dir, name)
            tree = ET.parse(xml_path)
            root = tree.getroot()
            img_name = getAndCheck(root, "filename", 1).text
            size = getAndCheck(root, 'size', 1)
            img_w = int(getAndCheck(size, 'width', 1).text)
            img_h = int(getAndCheck(size, 'height', 1).text)
            img_sample = setImageSample(img_id, img_name, img_h, img_w)
            flag = ano_id
            for obj in getAndCheck(root, 'object'):
                cat = getAndCheck(obj, 'name', 1).text
                cat_id, cat_sample = setCategorySample(cat, cat_names)
                if cat_sample:
                    self.coco_data["categories"].append(cat_sample)
                bndbox = getAndCheck(obj, 'bndbox', 1)
                x_min = int(float(getAndCheck(bndbox, 'xmin', 1).text))
                y_min = int(float(getAndCheck(bndbox, 'ymin', 1).text))
                x_max = int(float(getAndCheck(bndbox, 'xmax', 1).text))
                y_max = int(float(getAndCheck(bndbox, 'ymax', 1).text))
                xyxy = [x_min, y_min, x_max, y_max]
                xyxy = checkXyxy(xyxy, img_w, img_h)
                if xyxy is None:
                    continue
                xywh = xyxy2xywh(xyxy)
                ano_sample = setAnnotationSample(ano_id, img_id, cat_id, xywh)
                self.coco_data["annotations"].append(ano_sample)
                ano_id += 1
            if flag == ano_id:
                continue
            self.coco_data["images"].append(img_sample)
            img_id += 1
        with open(dst_coco, "w") as f:
            json.dump(self.coco_data, f, cls=MyEncoder)
        print("Complete data conversion to {}".format(dst_coco))

    def yolo2coco(self, dst_coco, txt_dir,  img_dir, cat_names=None):
        """
        yolo txt format to coco format
        :param dst_coco (str) : the path of Coco format JSON file to save
        :param txt_dir (str) : txt file folder
        :param img_dir (str) : picture folder
        :param cat_names (list) : specify category name, if None, use index as name
        """
        img_id, ano_id = 0, 0
        cat_names = [] if (cat_names is None) else cat_names
        cat_ids = []
        txt_names = [x for x in os.listdir(txt_dir) if x.endswith(".txt")]
        for txt_n in tqdm(txt_names):
            txt_p = os.path.join(txt_dir, txt_n)
            img_name = txt_n.replace(".txt", ".jpg")
            img_p = os.path.join(img_dir, img_name)
            if not os.path.exists(img_p):
                print("img path: {} not find!".format(img_p))
                img_p = img_p.replace(".jpg", ".png")
                print("try to find .png format!")
                if not os.path.exists(img_p):
                    print("img path: {} not find!".format(img_p))
                    continue
            img = cv2.imread(img_p)
            img_h, img_w, _ = img.shape
            img_sample = setImageSample(img_id, img_name, img_h,img_w)
            flag = ano_id
            with open(txt_p, "r") as f:
                anos = f.readlines()
                for ano in anos:
                    ano = ano.replace("\n", "").split(" ")
                    cat_id, yolo_box = int(float(ano[0])), list(map(float, ano[1:]))
                    if cat_id not in cat_ids:
                        cat_ids.append(cat_id)
                    xyxy = yoloBox2xyxy(yolo_box, img_h, img_w)
                    xyxy = checkXyxy(xyxy, img_w, img_h)
                    if xyxy is None:
                        continue
                    xywh = xyxy2xywh(xyxy)
                    ano_sample = setAnnotationSample(ano_id, img_id, cat_id, xywh)
                    self.coco_data["annotations"].append(ano_sample)
                    ano_id += 1
                if flag == ano_id:
                    continue
                self.coco_data["images"].append(img_sample)
                img_id += 1
        if len(cat_names) != 0:
            for i, c_n in enumerate(cat_names):
                _, cat_sample = setCategorySample(c_n, [])
                cat_sample["id"] = i
                self.coco_data["categories"].append(cat_sample)
        else:
            for c_i in cat_ids:
                _, cat_sample = setCategorySample(str(c_i), cat_names)
                self.coco_data["categories"].append(cat_sample)
        with open(dst_coco, "w") as f:
            json.dump(self.coco_data, f, cls=MyEncoder)
        print("Complete data conversion to {}".format(dst_coco))

    def mergeCoco(self, dst_coco, main_coco, second_coco):
        """
        Merge two coco datasets
        :param dst_coco (str) : the path of Coco format JSON file to save
        :param main_coco (str) : the path of Coco, as head
        :param second_coco (str) : the path of Coco, as tail
        """
        with open(main_coco, "r") as f1:
            main_data = json.load(f1)
        second_data = COCO(second_coco)
        main_imgs = main_data["images"]
        main_imgs_num = len(main_imgs)
        main_anos = main_data["annotations"]
        main_anos_num = len(main_anos)
        main_cat_names = [x["name"] for x in main_data["categories"]]
        cat_img_id = main_imgs[-1]["id"] + 1 if main_imgs_num < main_imgs[-1]["id"] else main_imgs_num
        cat_ano_id = main_anos[-1]["id"] + 1 if main_anos_num < main_imgs[-1]["id"] else main_anos_num
        second_cat_names = [x["name"] for x in second_data.loadCats(second_data.getCatIds())]
        t_img_id = 0
        t_ano_id = 0
        second_imgs_ids = second_data.getImgIds()
        for second_ig_id in second_imgs_ids:
            second_img_info = second_data.loadImgs(second_ig_id)[0]
            add_img_id = cat_img_id + t_img_id
            second_img_info["id"] = add_img_id
            second_ano_ids = second_data.getAnnIds(second_ig_id)
            if len(second_ano_ids) == 0:
                continue
            for second_ano_id in second_ano_ids:
                second_ano_info = second_data.loadAnns(second_ano_id)[0]
                second_cat_id = second_ano_info["category_id"]
                second_cat = second_cat_names[second_cat_id]
                add_cat_id, cat_sample = setCategorySample(second_cat, main_cat_names)
                if cat_sample:
                    main_data["categories"].append(cat_sample)
                add_ano_di = cat_ano_id + t_ano_id
                second_ano_info["id"] = add_ano_di
                second_ano_info["image_id"] = add_img_id
                second_ano_info["category_id"] = add_cat_id
                main_data["annotations"].append(second_ano_info)
                t_ano_id += 1
            main_data["images"].append(second_img_info)
            t_img_id += 1

        self.coco_data["images"] = main_data["images"]
        self.coco_data["annotations"] = main_data["annotations"]
        self.coco_data["categories"] = main_data["categories"]
        with open(dst_coco, "w") as f:
            json.dump(self.coco_data, f, cls=MyEncoder)
        print("Complete data conversion to {}".format(dst_coco))


if __name__=="__main__":
    labelme_dir = r"test"
    dst_coco = "coco.json"
    transfer = Transfer
    transfer.lableme2coco(dst_coco, labelme_dir)