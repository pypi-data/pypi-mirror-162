import os
from sys import argv, exit
from configparser import ConfigParser


def main(fname):
    cfg = ConfigParser()
    cfg.read(os.path.expanduser("~")+"/.uzoenr/bm.ini")
    speak = cfg["Speech"]["app"]
    os.system(f"cat ~/.uzoenr/library/{fname} | {speak} -s20 -vru")

def start():
    try:
        fnamo = argv[1]
        app = argv[0]
        main(fnamo)
    except IndexError:
        print("Объединение набора страниц в один текстовый файл:")
        print("Использование:")
        print(f'{app}: имя-итогового-файла имя-файла-со-списком-страниц')
    except FileNotFoundError:
        print(f"{fnamo}: Файл не найден")

if __name__ == '__main__':
    start()
