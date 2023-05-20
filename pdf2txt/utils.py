#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
 Author: zhaopenghao
 Create Time: 2023/5/14
"""
# from langchain.document_loaders import PyPDFLoader, PyMuPDFLoader, PDFMinerLoader
import fitz
import pprint


def convert(src_file, dest_file, column_num=1):
    """
    :param src_file: pdf
    :param dest_file: txt
    """
    print(f"start convert {src_file} to {dest_file}" )
    doc = fitz.open(src_file, filetype='pdf')
    assert isinstance(doc, fitz.Document)
    print(f">> PDF info: PageCount {doc.page_count}, metadata:")
    pprint.pprint(doc.metadata)

    with open(dest_file, 'w', encoding='utf8') as f:
        for page in doc:
            check_format(page, column_num)
            text = page.get_text()
            f.write(text)


def check_format(page: fitz.Page, column_num):
    # check if there's figure or not
    image_list = page.get_images()
    assert len(image_list) == 0, f"Found image in page {page.number}"
    #todo:
    # page.get_drawings()

    # todo: check if there's table or not
    assert page.first_widget is None, f"Found form in page {page.number}"
    # todo: check column_num
    pass

