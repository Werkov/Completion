#ifndef VOCABULARY_WRAPPER_H
#define VOCABULARY_WRAPPER_H

#include <Python.h>
#include "lm/model.hh"
#include "util/string_piece.hh" // needs compilation with -DHAVE_ICU
#include "token-dictionary.h"


class Vocabulary {
public:
    Vocabulary(const lm::ngram::Model::Vocabulary* vocab = 0, TokenDictionary* enumerate_vocab = 0);
    ~Vocabulary();
    lm::WordIndex BeginSentence() const;
    lm::WordIndex EndSentence() const;
    lm::WordIndex NotFound() const;
    lm::WordIndex Index(const StringPiece &str) const;
    bool IsWrapping() const;
    PyObject* GetTokens();
private:
    const lm::ngram::Model::Vocabulary * vocab_;
    TokenDictionary* enumerate_vocab_;
    PyObject* tokens_;
};
#endif