#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
 Author: zhaopenghao
 Create Time: 2023/5/14
"""
# from langchain.document_loaders import PyPDFLoader, PyMuPDFLoader, PDFMinerLoader
from typing import List, Optional
import pprint

import numpy as np
import fitz
from fitz.fitz import (
    TEXT_INHIBIT_SPACES,
    TEXT_PRESERVE_LIGATURES,
    TEXT_PRESERVE_WHITESPACE,
)

from .layout import page_layout


def convert(src_file: str, dest_file: str,
            do_check: bool = False, column_num: int = 1,
            clip: Optional[list] = None,  # [x0, y0, x1, y1]
            sort: bool = False,
            mode: str = 'simple',  # layout, todo: support 'auto'
            flags_conf: Optional[dict] = None,
            layout_conf: Optional[dict] = None,
            ) -> None:
    print(f"start convert {src_file} to {dest_file}" )
    doc = fitz.open(src_file, filetype='pdf')
    assert isinstance(doc, fitz.Document)
    print(f">> PDF info: PageCount {doc.page_count}, metadata:")
    # https://pymupdf.readthedocs.io/en/latest/tutorial.html#accessing-meta-data
    pprint.pprint(doc.metadata)

    # flags
    flags = TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE
    flags_conf = flags_conf or {}
    if flags_conf.get("convert_white", False):
        flags ^= TEXT_PRESERVE_WHITESPACE
    if flags_conf.get("noligatures", False):
        flags ^= TEXT_PRESERVE_LIGATURES
    if flags_conf.get("extra_spaces", False):
        flags ^= TEXT_INHIBIT_SPACES

    if clip is not None:
        assert len(clip) == 4, "clip must be list: [x0, y0, x1, y1]"
        clip = fitz.Rect(clip)

    with open(dest_file, 'wb') as f:
        # https://pymupdf.readthedocs.io/en/latest/document.html#Document.pages
        # for page in doc.pages():  # both are ok
        for page in doc:
            assert isinstance(page, fitz.Page)
            # assert not isinstance(page, fitz.TextPage)
            # fitz.TextPage
            if do_check:
                check_format(page, column_num)

            # Page.get_text()会提取当前页内容生成一个TextPage对象，然后实际调用的是TextPage.extractText()
            # 关于TextPage的概念可以参考 https://pymupdf.readthedocs.io/en/latest/app1.html#general-structure-of-a-textpage
            if mode == 'simple':
                simple_extract(f, page, clip, sort, flags)
            else:
                assert mode == 'layout', f"mode must be one of [simple, layout]! {mode} is not supported."
                assert column_num == 1, f"layout mode doesn't support column_num>1 now."
                layout_conf = layout_conf or {}
                grid = layout_conf.get('grid', 2)
                fontsize = layout_conf.get('fontsize', 3)
                page_layout(page, f, grid, fontsize, noformfeed=True, skip_empty=False, flags=flags, clip=clip)


def simple_extract(f, page, clip, sort, flags):
    # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_text
    # https://pymupdf.readthedocs.io/en/latest/textpage.html
    text = page.get_text(
        # “text” – TextPage.extractTEXT(), default
        # “blocks” – TextPage.extractBLOCKS()
        # “words” – TextPage.extractWORDS()
        # “html” – TextPage.extractHTML()
        # “xhtml” – TextPage.extractXHTML()
        # “xml” – TextPage.extractXML()
        # “dict” – TextPage.extractDICT()
        # “json” – TextPage.extractJSON()
        # “rawdict” – TextPage.extractRAWDICT()
        # “rawjson” – TextPage.extractRAWJSON()
        "text",  # default, TextPage.extractTEXT()
        # (rect-like)–(new in v1.17.7)restrict extracted text to this rectangle. If None, the full page is taken
        clip=clip,  # default None
        # flags (int) – (new in v1.16.2) indicator bits to control whether to include images or
        # how text should be handled with respect to white spaces and ligatures.
        flags=flags,
        # use a previously created TextPage. This reduces execution time very significantly:
        # by more than 50% and up to 95%, depending on the extraction option. If specified,
        # the ‘flags’ and ‘clip’ arguments are ignored, because they are textpage-only properties.
        # If omitted, a new, temporary textpage will be created.
        textpage=None,
        # sort (bool) – (new in v1.19.1) sort the output by vertical, then horizontal coordinates.
        # In many cases, this should suffice to generate a “natural” reading order
        sort=sort,
    )

    # blocks的提取: https://pymupdf.readthedocs.io/en/latest/app1.html#blocks
    # (x0, y0, x1, y1, "lines in block", block_no, block_type)

    f.write(text.encode("utf8", errors="surrogatepass"))
    eop = b'\n'
    f.write(eop)
    return


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

