#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
 Create Time: 2023/5/14
"""
import pdf2txt

# src_file = '../data/逍遥游.pdf'
# dest_file = './逍遥游.txt'
src_file = '../data/逍遥游-带图.pdf'
dest_file = './逍遥游-带图.txt'

pdf2txt.convert(src_file, dest_file)

