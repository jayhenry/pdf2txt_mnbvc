#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
 Author: zhaopenghao
 Create Time: 2023/5/14
"""
from langchain.document_loaders import PyPDFLoader, PyMuPDFLoader, PDFMinerLoader

def convert(src_file, dest_file):
    """
    :param src_file: pdf
    :param dest_file: txt
    """
    loader = PyMuPDFLoader(src_file)
    docs = loader.load()
    with open(dest_file, 'w') as f:
        for d in docs:
            f.write(d.page_content)
