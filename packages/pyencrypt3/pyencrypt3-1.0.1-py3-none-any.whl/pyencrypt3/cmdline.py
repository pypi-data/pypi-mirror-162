# -*- coding: utf-8 -*-
"""
Created on 2022-08-10
@author:刘飞
@description:接收命令行参数
"""
import getopt
import sys

from pyencrypt3.encrypt_py import start_encrypt


def usage():
    """
python代码 加密|加固
参数说明：
    -i | --input_file_path    待加密文件或文件夹路径，可是相对路径或绝对路径
    -o | --output_file_path   加密后的文件输出路径，默认在input_file_path下创建dist文件夹，存放加密后的文件
    -I | --ignore_files       不需要加密的文件或文件夹，逗号分隔
    -m | --except_main_file   不加密包含__main__的文件(主文件加密后无法启动), 值为0、1。 默认为0
    -p | --pyc   编译为pyc格式,值为0、1。 默认为0
    """


def execute():
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "hi:o:I:m:p:",
            [
                "help",
                "input_file_path=",
                "output_file_path=",
                "ignore_files=",
                "except_main_file=",
                "pyc=",
            ],
        )
        input_file_path = output_file_path = ignore_files = ""
        except_main_file = 0
        pyc = 0

        for name, value in options:
            if name in ("-h", "--help"):
                print(usage.__doc__)
                sys.exit()

            elif name in ("-i", "--input_file_path"):
                input_file_path = value

            elif name in ("-o", "--output_file_path"):
                output_file_path = value

            elif name in ("-I", "--ignore_files"):
                ignore_files = value.split(",")

            elif name in ("-m", "--except_main_file"):
                except_main_file = int(value)
            elif name in ("-p", "--pyc"):
                pyc = int(value)

        if not input_file_path:
            print("需指定-i 或 input_file_path")
            print(usage.__doc__)
            sys.exit()

        start_encrypt(input_file_path, output_file_path, ignore_files, except_main_file, pyc)

    except getopt.GetoptError:
        print(usage.__doc__)
        sys.exit()
