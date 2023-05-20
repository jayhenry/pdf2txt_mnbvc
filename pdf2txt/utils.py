#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
 Author: zhaopenghao
 Create Time: 2023/5/14
"""
from langchain.document_loaders import PyPDFLoader, PyMuPDFLoader, PDFMinerLoader

def convert(src_file, dest_file, column_num=1):
    """
    :param src_file: pdf
    :param dest_file: txt
    """

    check_format(column_num)

    loader = PyMuPDFLoader(src_file)
    docs = loader.load()
    with open(dest_file, 'w') as f:
        for d in docs:
            f.write(d.page_content)


def check_format(column_num):
    # check if there's figure or not
    # check if there's table or not
    # check column_num
    pass

