#!/usr/bin/env python3

import sys

import argparse
import re
from string import ascii_letters


def stripTex(file):
    """Strip mathematics, content of chosen sequences, sequences and braces from TeX source."""
    S_TEXT          = 0
    S_INLINE        = 1
    S_DISPLAY       = 2
    S_DOLLAR_IN     = 3
    S_DOLLAR_OUT    = 4
    S_SEQUENCE      = 5
    S_EXPECT_ARG    = 6
    S_OPTIONAL      = 7

    # sequences whose 1st argument content is not desired text
    forbidden = {
        'begin', 'end', 'ref', 'eqref', 'usepackage', 'documentclass'
        'probbatch', 'probno', 'probpoints', 'probsolauthors', 'probsolvers', 'probavg',
        'illfig', 'fullfig', 'plotfig'
        'eq'
    }


    # -- strip comments --
    lines = []
    for line in file.readlines():
        line += '%'
        lines.append(line[:line.index('%')]) # TODO \%

    # -- strip mathematics and chosen sequence's arguments --
    # finite state machine with depth counter
    state = S_TEXT
    mode = S_TEXT
    depth = 0
    sequence = ''
    bracketStack = [] # contains either None or index in out where sequence argument starts
    out = []
    for c in ''.join(lines):
        #print(c, state)
        if state == S_TEXT:
            if c == '\\':
                state = S_SEQUENCE
                out.append(c)
            elif c == '$':
                state = S_DOLLAR_IN
            elif c == '{':
                out.append(c)
                bracketStack.append((len(out), None))
            elif c == '}':
                try:
                    out.append(c)
                    i, seq = bracketStack.pop() # not to shadow "global" sequence
                    if seq != None and seq in forbidden:
                        out = out[:i]
                except IndexError:
                    print('Unmatched right bracket.')
                    break
            else:
                out.append(c)
        elif state == S_INLINE:
            if c == '\\':
                state = S_SEQUENCE
                mode = S_INLINE
            elif c == '$':
                state = S_TEXT
                mode = S_TEXT
            elif c == '{':
                bracketStack.append((len(out), None))
            elif c == '}':
                try:
                    bracketStack.pop()                    
                except IndexError:
                    print('Unmatched right bracket.')
                    break
        elif state == S_DISPLAY:
            if c == '\\':
                state = S_SEQUENCE
                mode = S_DISPLAY
            elif c == '$':
                state = S_DOLLAR_OUT
            elif c == '{':
                bracketStack.append((len(out), None))
            elif c == '}':
                try:
                    bracketStack.pop()                    
                except IndexError:
                    print('Unmatched right bracket.')
                    break
        elif state == S_DOLLAR_OUT:
            if c == '$':
                state = S_TEXT
                mode = S_TEXT
            else:
                pass # stay in display mode
        elif state == S_DOLLAR_IN:
            if c == '$':
                state = S_DISPLAY
                mode = state
            else:
                state = S_INLINE
                mode = state
        elif state == S_SEQUENCE:            
            if c in ascii_letters:
                if mode == S_TEXT: out.append(c)
                sequence += c
            elif c == '[':
                if mode == S_TEXT: out.append(c)
                state = S_OPTIONAL
            elif c == '{':
                state = mode
                if out[-1] == '\\': # backslashed brace
                    out.append(c)
                else:
                    bracketStack.append((len(out), sequence))
                    sequence = ''
                    if mode == S_TEXT: out.append(c)
            else:
                if mode == S_TEXT: out.append(c)
                state = mode
                sequence = ''
        elif state == S_OPTIONAL: # here we suppose no nested [, ]
            if c == ']':
                if mode == S_TEXT: out.append(c)
                state = S_EXPECT_ARG
            else:
                if mode == S_TEXT: out.append(c)
        elif state == S_EXPECT_ARG:
            if c == '{':
                bracketStack.append((len(out), sequence))
                sequence  = ''
                if mode == S_TEXT: out.append(c)
            else:
                state = mode
                if mode == S_TEXT: out.append(c)
        else:
            print('Invalid state')
            break
    # end for
    noMath = ''.join(out)

    # -- finally simple regexp substitution --
    noMath = re.sub('~', ' ', noMath)
    noMath = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?', '', noMath)
    noMath = re.sub(r'[{}]', '', noMath)
    print(noMath)






def main():
    parser = argparse.ArgumentParser(description="Strip (La)TeX sequences from input files.")
    parser.add_argument("file", help="(La)TeX file", type=argparse.FileType('r'), nargs='+')

    args = parser.parse_args()


    for f in args.file:
        stripTex(f)
        f.close()


    

if __name__ == '__main__':
    main()


    
    


