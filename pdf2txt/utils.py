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


def clean_list(values):
    """Remove items from values that are too close to predecessor."""
    for i in range(len(values) - 1, 0, -1):
        v1 = values[i]
        v0 = values[i - 1]
        if v1 - v0 <= 3:  # too close to predecessor
            del values[i]


def check_table(page):
    # https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/table-analysis/gridlines-to-pandas.py
    # vertical / horizontal line coordinates. Python 'sets' avoid duplicates.
    vert = set()  # vertical (x-) coordinates
    hori = set()  # horizontal (y-) coordinates
    paths = page.get_drawings()  # all line art / vector graphics on page
    for p in paths:  # iterate over vector graphics to find the lines
        for item in p["items"]:  # look at lines and "thin" rectangles
            if item[0] == "l":  # a line
                p1, p2 = item[1:]  # start and stop points
                if p1.x == p2.x:  # a vertical line!
                    vert.add(p1.x)  # store this column border
                elif p1.y == p2.y:  # a horizontal line!
                    hori.add(p1.y)  # store this row border
            # many apparent 'lines' are thin rectangles really ...
            elif item[0] == "re":  # a rectangle item
                rect = item[1]  # rect coordinates
                if rect.width <= 3 and rect.height > 10:
                    vert.add(rect.x0)  # thin vertical rect: treat like col border
                elif rect.height <= 3 and rect.width > 10:
                    hori.add(rect.y1)  # treat like row border
    vert = sorted(list(vert))  # sorted, without duplicates
    clean_list(vert)  # remove "almost" duplicate coordinates
    hori = sorted(list(hori))  # sorted, without duplicates
    clean_list(hori)  # remove "almost" duplicate coordinates
    print(f"There are {len(hori)} lines in page {page.number}")
    assert len(hori) < 2, f"Found horizontal lines >=2, there maybe tables in page {page.number}"


def check_col_num(page, column_num):
    # https://pymupdf.readthedocs.io/en/latest/app1.html#blocks
    # (x0, y0, x1, y1, "lines in block", block_no, block_type)
    blocks = page.get_text("blocks")
    bxy_list =[]
    for b in blocks:
        bxy_list.append([round(i) for i in b[:4]])
    bxy_list = np.array(bxy_list)
    # print(f'Page {page.number}'.center(50, '-'))
    # print(bxy_list)
    cols_per_row = np.zeros((bxy_list[:, 3].max()))
    for b in bxy_list:
        x0, y0, x1, y1 = b
        cols_per_row[y0:y1] += 1

    real_col_num = cols_per_row.max()
    # print("cols_per_row: \n", cols_per_row)

    # n_blocks = len(blocks)
    assert real_col_num == column_num, f"Found {real_col_num} blocks in page {page.number}"


def check_format(page: fitz.Page, column_num):
    # check if there's a figure or not
    image_list = page.get_images()
    assert len(image_list) == 0, f"Found image in page {page.number}"

    # xtodo: check if there's a form or not
    assert page.first_widget is None, f"Found form in page {page.number}"

    # xtodo: check if there's a table or not
    check_table(page)

    # xtodo: check column_num
    check_col_num(page, column_num)

