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
- [ ] 去除header/footer?

## More about pdf & PyMuPDF
### 什么是PDF表单(PDF Form)？

https://helpx.adobe.com/cn/acrobat/using/create-form.chromeless.html

https://helpx.adobe.com/cn/acrobat/using/create-form.chromeless.html

### PyMuPDF Basic Intro
https://pymupdf.readthedocs.io/en/latest/the-basics.html#extract-text-from-a-pdf

### PyMuPDF Page
https://pymupdf.readthedocs.io/en/latest/tutorial.html#working-with-pages

https://pymupdf.readthedocs.io/en/latest/page.html

### 页面坐标系
https://pymupdf.readthedocs.io/en/latest/rect.html#Rect.round

<!---
改变图片尺寸的方法见 https://m.runoob.com/markdown/md-image.html
![rect](https://pymupdf.readthedocs.io/en/latest/_images/img-rect-contains.png)
--->
<img alt="rect" src="https://pymupdf.readthedocs.io/en/latest/_images/img-rect-contains.png" width="50%">

### 按自然阅读顺序提取文本
最简单的提取[方法](https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/PDF2Text.py)，会按pdf文件添加元素的顺序进行提取。
而有时候为了防止copy，一些pdf会打乱添加元素的顺序，但是排版上不影响阅读。这样简单地抽取文本就无法按照正常的阅读顺序排列，见这个[例子](https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/textmaker2.pdf)。
这些信息来源于 https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/README.md.

更多信息可见 https://pymupdf.readthedocs.io/en/latest/recipes-text.html#how-to-extract-text-in-natural-reading-order

### 提取表格
没有简单的方法能准确地判断表格在页面中的位置，这通常是一个需要AI、ML技术来解决的复杂问题。
但是对于一些简单的情况，可以使用PyMuPDF提供的vector graphics分析工具来判断表格的存在，比如是否有直线、矩形框等。
这些信息来源于 https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/table-analysis/README.md.

更多信息见:

https://pymupdf.readthedocs.io/en/latest/recipes-text.html#how-to-extract-tables-from-documents

https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/extract-table/README.md





