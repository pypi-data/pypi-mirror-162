#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: drwaUtils.py
# Author: Rayson.Shi
# Mail: raysonshi@qq.com
# Created Time:  2022-8-5 23:17:34
#############################################
import os
import matplotlib.pyplot as plt
import numpy as np


class DrawUtils():
    def __init__(self, save_path):
        super(DrawUtils, self).__init__()
        self.save_path = save_path
        if self.save_path and not os.path.exists(save_path):
            os.mkdir(self.save_path)
        plt.rcParams['font.sans-serif'] = 'SimHei'  # 设置中文显示
        plt.rcParams["axes.unicode_minus"] = False

    def drawPie(self, title, labels, values):
        indexs = list(reversed(np.argsort(values)))
        labels = [labels[i] for i in indexs]
        values = [values[i] for i in indexs]
        explode = [0.01 for _ in range(len(labels))]
        plt.pie(values, explode=explode, labels=labels, autopct='%1.1f%%')
        plt.title(title)
        if self.save_path:
            save_path = os.path.join(self.save_path, title + ".jpg")
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
            plt.close()

    def drawHeatmap(self, title, x_lables, y_labels, map_vales):
        plt.xticks(np.arange(len(x_lables)), labels=x_lables, rotation_mode="anchor", ha="right")
        plt.yticks(np.arange(len(y_labels)), labels=y_labels)
        for i in range(len(x_lables)):
            for j in range(len(y_labels)):
                plt.text(j, i, int(map_vales[i, j]), ha="center", va="center", color="w")
        plt.title(title)
        plt.imshow(map_vales)
        plt.colorbar()
        plt.tight_layout()
        if self.save_path:
            save_path = os.path.join(self.save_path, title + ".jpg")
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
            plt.close()

    def drawBar(self, title, x_name, y_name, labels, values, max_number=None):
        indexs = list(reversed(np.argsort(values)))
        labels = [labels[i] for i in indexs]
        values = [values[i] for i in indexs]
        if max_number and (len(labels) > max_number):
            labels = labels[:max_number]
            values = values[:max_number]
            print("{} chart only show the top {}".format(title, max_number))
        plt.bar(range(len(labels)), values)
        if type(labels[0])==str and len(labels) > 8:
            plt.xticks(range(len(labels)), labels, rotation=-45)
        else:
            plt.xticks(range(len(labels)), labels)
        for i in range(len(labels)):
            plt.text(i, values[i], '%.i' % values[i], fontsize=10, ha='center', va='bottom')
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        plt.title(title)
        if self.save_path:
            save_path = os.path.join(self.save_path, title + ".jpg")
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
            plt.close()

    def drawHist(self, title, x_names, y_name, values, bins=100):
        plt.hist(values, bins=bins, facecolor="blue", edgecolor="black", alpha=0.7)
        plt.xlabel(x_names)
        plt.ylabel(y_name)
        plt.title(title)
        if self.save_path:
            save_path = os.path.join(self.save_path, title + ".jpg")
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
            plt.close()

