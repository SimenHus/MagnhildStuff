import os
import sys




def BASE_PATH() -> str:
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    else:
        return os.path.abspath('.')
    

def verify_existance(path) -> bool:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def absolute_path(relative_path) -> str:
    base_path = BASE_PATH()
    return os.path.join(base_path, relative_path)


def output_folder() -> str:
    path = os.path.join(os.getcwd(), 'output')
    verify_existance(path)
    return path

def debug_folder() -> str:
    path = os.path.join(os.getcwd(), 'debug')
    verify_existance(path)
    return path

def join(*args) -> str:
    return os.path.join(*args)


def initialize() -> None:
    output_folder()
    debug_folder()