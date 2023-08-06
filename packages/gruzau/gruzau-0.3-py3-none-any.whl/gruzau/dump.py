from uzoenr.uzoenr import Engine
from os import listdir
from sys import argv

helpme = """
gruzau-dump - web pages concatenator
Usage:
gruzau-dump <enc> <output-file> <input files>
"""

def main(save, fl, enc):
	"""Concatenate web pages to a single file
	
	Keyword arguments:
	save -- filename for single text document
	fl -- list of web pages
	enc -- encoding
	
	"""
	text = ''
	for fname in fl:
		P = Engine()
		with open(fname, encoding=enc) as f:
			P.feed(f.read())
			text = text + P.data + "\n\n\n\n\n\n\n"
	with open(save, "w") as f:
		f.write(text)


def start():
	try:
		main(argv[2], argv[3:], argv[1])
	except IndexError:
		print(helpme)

if __name__ == "__main__":
	start()
