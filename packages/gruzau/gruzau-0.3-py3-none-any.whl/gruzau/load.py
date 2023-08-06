from sys import argv
from uzoenr.uzoenr import load

def main(fname, urli):
    page = []
    with open(urli) as f:
        urls = f.read().split('\n')
    for url in urls[:-1]:
        page.append(load(url))
    with open(fname, 'w') as f:
        f.write('\n\n'.join(['\n'.join(i) for i in page]))

def start():
    try:
        main(argv[1], argv[2])
    except IndexError:
        print("Объединение набора страниц в один текстовый файл:")
        print("Использование:")
        print(argv[0]+': имя-итогового-файла имя-файла-со-списком-страниц')

if __name__ == '__main__':
    start()
