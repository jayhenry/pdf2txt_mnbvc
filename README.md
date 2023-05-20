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
- [] 检查是否有表格
- [] 检查排版分栏
- [] 换行符用 LF or CRLF?
- [] pdf中排版换行并非文字逻辑换行时是否去除？
- [] 去除header/footer?

## More about pdf
什么是PDF表单(PDF Form)？

https://helpx.adobe.com/cn/acrobat/using/create-form.chromeless.html

https://helpx.adobe.com/cn/acrobat/using/create-form.chromeless.html

## More about PyMuPDF
https://pymupdf.readthedocs.io/en/latest/the-basics.html#extract-text-from-a-pdf

https://pymupdf.readthedocs.io/en/latest/tutorial.html#working-with-pages

https://pymupdf.readthedocs.io/en/latest/page.html

https://pymupdf.readthedocs.io/en/latest/recipes-text.html



