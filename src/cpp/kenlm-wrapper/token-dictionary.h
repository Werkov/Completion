#ifndef TOKEN_DICTIONARY_H
#define TOKEN_DICTIONARY_H

#include <Python.h>
#include <string>
#include <iostream>
#include "util/string_piece.hh" // needs compilation with -DHAVE_ICU
#include "lm/enumerate_vocab.hh"
#include "lm/word_index.hh"

/**
 * Class wraps Python container (here frozenset) and provides interface for adding words used by KenLM.
 */
class TokenDictionary : public lm::EnumerateVocab {
public:
    TokenDictionary();
    ~TokenDictionary();
    virtual void Add(lm::WordIndex index, const StringPiece &str);
    PyObject* GetContainer();
private:
    bool immutable_; // flag for not modifying container content after publishing it
    PyObject* vocabulary_;
};
#endif
