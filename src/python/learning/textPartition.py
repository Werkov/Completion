#!/usr/bin/env python3
import os.path
import sys

import argparse

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import learning.partition

def main():
    parser = argparse.ArgumentParser(description="""\
    Split text file into several files with given distribution of 'units'.
    
    Example: distribution `1 10 2` yields three files.
        First contains first in every 13 consecutive units,
        second contains second to eleventh units
        and last contains twelveth to thirteenth unit.""", formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("file", help="text file", type=argparse.FileType('r'))
    parser.add_argument("-u", help="unit (l: line, w: wiki article, t: TeX paragraph)\t[%(default)s]", choices="lwt", default="l")
    parser.add_argument("d", help="distribution amounts", type=int, nargs='+')

    separators = {
        'l': learning.partition.lineSeparator,
        'w': learning.partition.WikiSeparator(),
        't': learning.partition.TexSeparator()
    }

    args = parser.parse_args()

    learning.partition.splitFile(args.file, args.d, separators[args.u])
    args.file.close()
   
    

if __name__ == '__main__':
    main()


    
    


