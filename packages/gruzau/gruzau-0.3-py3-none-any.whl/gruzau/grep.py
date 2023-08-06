import configparser, os.path, sys
def main(query, page):
    if type(page) is not list:
        raise TypeError("Страница должна быть списком строк")
    if type(query) is str:
        return [line for line in page if query in line]
    elif type(query) is tuple and type(query[0]) is int and type(query[1]) is int:
        return page[query[0]:query[1]+1]

if __name__ == "__main__":
    with open(os.path.expanduser("~")+"/.uzoenr/library/"+sys.argv[1]) as f:
        page = f.read().split("\n")
    if len(sys.argv) == 4:
        query = tuple([int(sys.argv[2]), int(sys.argv[3])])
    elif len(sys.argv) == 3:
        query = sys.argv[2]
    else:
        raise RuntimeError("Неправильные аргументы. Читай справку")
    print("\n".join(main(query, page)))
