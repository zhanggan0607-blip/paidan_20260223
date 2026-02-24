#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML转PDF转换脚本
将培训手册HTML文件转换为PDF格式
"""

from xhtml2pdf import pisa
import os

def html_to_pdf():
    html_path = r'D:\共享文件\SSTCP-paidan260120\培训手册\SSTCP维保管理系统培训手册.html'
    pdf_path = r'D:\共享文件\SSTCP-paidan260120\培训手册\SSTCP维保管理系统培训手册.pdf'
    
    print(f"正在转换: {html_path}")
    print(f"输出文件: {pdf_path}")
    
    with open(html_path, 'rb') as html_file:
        with open(pdf_path, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(html_file, dest=pdf_file)
    
    if not pisa_status.err:
        print(f"PDF生成成功: {pdf_path}")
        print(f"文件大小: {os.path.getsize(pdf_path) / 1024:.2f} KB")
    else:
        print(f"PDF生成失败，错误数: {pisa_status.err}")

if __name__ == '__main__':
    html_to_pdf()
