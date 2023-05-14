#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
 Create Time: 2023/5/14
"""
import pdf2txt

src_file = './test.pdf'
dest_file = './test.txt'

pdf2txt.convert(src_file, dest_file)

