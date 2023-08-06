import os
from random import shuffle
import shutil


PACKAGE_DIR = os.path.dirname(__file__)

PADDLE_DIR = os.path.join(
    PACKAGE_DIR,
    "../",
    "paddle"
)


def replace_tensor_file():
    """replace the source tensor/tensor.py file to make it executable
    """
    with open(os.path.join(PACKAGE_DIR, 'tensor.py'), "r", encoding='utf-8') as f:
        target_tensor_content = f.read()
    
    with open(os.path.join(PADDLE_DIR, 'tensor', 'tensor.py'), 'w', encoding='utf-8') as f:
        f.write(target_tensor_content)


def add_tensor_pyi_file():
    """add tensor.pyi file to the target dir to make it intelligence in IDE
    """
    shutil.copyfile(
        os.path.join(PACKAGE_DIR, 'tensor.pyi'),
        os.path.join(PADDLE_DIR, 'tensor', 'tensor.pyi')
    )


def main():
    replace_tensor_file()
    add_tensor_pyi_file()