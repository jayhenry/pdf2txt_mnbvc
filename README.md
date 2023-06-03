[TOC]

## Intro
将pdf转换为txt文件，并且检查其分栏排版，以及是否有图像、表格。

## Usage
见 `examples/example.py`
```python
import pdf2txt

src_file = '../data/逍遥游.pdf'
dest_file = './逍遥游.txt'

pdf2txt.convert(src_file, dest_file)
```

## Features
- [x] pdf文字转成txt
- [x] 检查是否有图像，有则报错
- [x] 检查是否有表格
- [x] 检查排版分栏
- [ ] 换行符用 LF or CRLF?
- [ ] pdf中排版换行并非文字逻辑换行时是否去除？
    - 根据下列规则，满足则去除换行符：换行符前没有标点符号，并且最后一个字符位置接近右侧边缘。
- [ ] 去除header/footer? 
    - 很难判断是否为页眉页脚，改为接受一个文本框区域，只在该区域提取文本

## More about pdf & PyMuPDF
### PyMuPDF Basic Intro
https://pymupdf.readthedocs.io/en/latest/the-basics.html#extract-text-from-a-pdf

### PyMuPDF Page
https://pymupdf.readthedocs.io/en/latest/tutorial.html#working-with-pages

https://pymupdf.readthedocs.io/en/latest/page.html

下图来自 https://pymupdf.readthedocs.io/en/latest/textpage.html#structure-of-dictionary-outputs
<img alt="TextPageStructure" src="https://pymupdf.readthedocs.io/en/latest/_images/img-textpage.png">

### 页面坐标系
https://pymupdf.readthedocs.io/en/latest/rect.html#Rect.round

<!---
改变图片尺寸的方法见 https://m.runoob.com/markdown/md-image.html
![rect](https://pymupdf.readthedocs.io/en/latest/_images/img-rect-contains.png)
--->
<img alt="rect" src="https://pymupdf.readthedocs.io/en/latest/_images/img-rect-contains.png" width="50%">

### 页面坐标单位&fonesize单位


### drawings and graphics

https://pymupdf.readthedocs.io/en/latest/recipes-drawing-and-graphics.html


### 按自然阅读顺序提取文本
1. 最简单的提取[方法](https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/PDF2Text.py)，会按pdf文件添加元素的顺序进行提取。
2. 而有时候为了防止copy，一些pdf会打乱添加元素的顺序，但是排版上不影响阅读。这样简单地抽取文本就无法按照正常的阅读顺序排列，见这个[例子](https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/textmaker2.pdf)。
3. 为了解决上面的情况，有一些办法，一个简单的方法是讲文本Block根据坐标位置排序，按从上到下从左到右的顺序，像这个[例子](https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/PDF2TextBlocks.py)
4. 另外，有一个复杂一些的方法，[这个代码](https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/fitzcli.py)中的`page_layout`函数考虑到排版格式，大概流程是
    - 得到每个字符的位置信息，并且去掉[旋转的字符](https://pymupdf.readthedocs.io/en/latest/textpage.html#character-dictionary-for-extractrawdict)
    - 根据字符的位置，计算所有行坐标，忽略间隔小于`GRID`的行坐标
    - 遍历每一行，得到每行从左到右的字符列表
    - 计算字符宽度slot，用于后续判断空格
    - 根据上面的信息生成每行的string
    - 需要注意，通过此方法生成的text保持了原来pdf的排版信息。如pdf是[三栏](https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/demo1.pdf)，输出的text中也是[三栏](https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/demo1-text.jpg)，并不是文字流。

这些信息来源于 https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/README.md.

更多信息可见 https://pymupdf.readthedocs.io/en/latest/recipes-text.html#how-to-extract-text-in-natural-reading-order

### 提取表格
没有简单的方法能准确地判断表格在页面中的位置，这通常是一个需要AI、ML技术来解决的复杂问题。
但是对于一些简单的情况，可以使用PyMuPDF提供的vector graphics分析工具来判断表格的存在，比如是否有直线、矩形框等。
这些信息来源于 https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/table-analysis/README.md.

更多信息见:

https://pymupdf.readthedocs.io/en/latest/recipes-text.html#how-to-extract-tables-from-documents

https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/extract-table/README.md


### 什么是PDF表单(PDF Form)？

https://helpx.adobe.com/cn/acrobat/using/create-form.chromeless.html

https://helpx.adobe.com/cn/acrobat/using/create-form.chromeless.html




