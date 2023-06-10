# https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/textbox-extraction/textbox-extract-2.py

import fitz

doc = fitz.open("../data/逍遥游-页眉页脚-分栏-标题不分栏-批注.pdf")  # any supported document type
page = doc[0]  # we want text from this page

"""
-------------------------------------------------------------------------------
Identify the rectangle.
-------------------------------------------------------------------------------
"""
rect = page.first_annot.rect  # this annot has been prepared for us!

print(rect)
# output: Rect(74.87010192871094, 70.5579833984375, 509.9519958496094, 768.178955078125)
