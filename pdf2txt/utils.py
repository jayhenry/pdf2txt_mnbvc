#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
 Author: zhaopenghao
 Create Time: 2023/5/14
"""
# from langchain.document_loaders import PyPDFLoader, PyMuPDFLoader, PDFMinerLoader
import pprint

import fitz

import numpy as np


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
            assert isinstance(page, fitz.Page)
            # assert not isinstance(page, fitz.TextPage)
            check_format(page, column_num)
            text = page.get_text()

            # https://pymupdf.readthedocs.io/en/latest/app1.html#plain-text
            # text = page.get_text("text", sort=True)

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
    # https://pymupdf.readthedocs.io/en/latest/app1.html#blocks
    # (x0, y0, x1, y1, "lines in block", block_no, block_type)
    blocks = page.get_text("blocks")
    x =[]
    for b in blocks:
        x.append([round(i) for i in b[:4]])
    x = np.array(x)
    # print(f'Page {page.number}'.center(50, '-'))
    # print(x)
    cols_per_row = np.zeros((x[:, 3].max()))
    for b in x:
        x0, y0, x1, y1 = b
        cols_per_row[y0:y1] += 1

    real_col_num = cols_per_row.max()
    # print("cols_per_row: \n", cols_per_row)

    # n_blocks = len(blocks)
    assert real_col_num == column_num, f"Found {real_col_num} blocks in page {page.number}"

