#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : pdf
# @Time         : 2022/6/30 下午3:41
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


from meutils.pipe import *
import fitz  # pymupdf 速度更快


def extract_text(filename):
    return '\n'.join(page.get_text().strip() for page in fitz.Document(filename))


def pdf2text(file_or_dir_or_files, n_jobs=3):
    if isinstance(file_or_dir_or_files, str) or not isinstance(file_or_dir_or_files, Iterable):
        p = Path(file_or_dir_or_files)
        if p.is_file():
            file_or_dir_or_files = [p]
        elif p.is_dir():
            file_or_dir_or_files = p.glob('*.pdf')
        else:
            raise ValueError('无效文件')

    _ = file_or_dir_or_files | xJobs(lambda p: (p, extract_text(p)), n_jobs)

    return pd.DataFrame(_, columns=['filename', 'text'])


def word2text(filename):
    pass


if __name__ == '__main__':
    pass
