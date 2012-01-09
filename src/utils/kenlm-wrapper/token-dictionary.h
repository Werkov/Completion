#ifndef TOKEN_DICTIONARY_H
#define TOKEN_DICTIONARY_H

#include <vector>
#include <iostream>
#include "util/string_piece.hh" // needs compilation with -DHAVE_ICU
#include "lm/enumerate_vocab.hh"
#include "lm/word_index.hh"

class TokenDictionary : public lm::EnumerateVocab, public std::vector<StringPiece> {
public:
    virtual void Add(lm::WordIndex index, const StringPiece &str);
};
#endif