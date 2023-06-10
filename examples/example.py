#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
 Create Time: 2023/5/14
"""
import pdf2txt

# src_file = '../data/逍遥游.pdf'
# dest_file = './逍遥游.txt'
# src_file = '../data/逍遥游-带图.pdf'
# dest_file = './逍遥游-带图.txt'
# src_file = '../data/逍遥游-带表格.pdf'
# dest_file = './逍遥游-带表格.txt'
# src_file = '../data/逍遥游-分栏.pdf'
# dest_file = './逍遥游-分栏.txt'
# src_file = '../data/逍遥游-带表格.pdf'
# dest_file = './逍遥游-带表格.txt'
# src_file = '../data/逍遥游-页眉页脚.pdf'
# dest_file = './逍遥游-页眉页脚.txt'

src_file = '../data/逍遥游-页眉页脚-分栏-标题不分栏.pdf'
# dest_file = './逍遥游-页眉页脚-分栏-标题不分栏-withoutClip.txt'
# clip = None
dest_file = './逍遥游-页眉页脚-分栏-标题不分栏-withClip.txt'
clip = [75, 70, 510, 768]  # x0,y0,x1,y1

pdf2txt.convert(src_file, dest_file, column_num=2, clip=clip)


