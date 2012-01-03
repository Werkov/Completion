#ifndef VOCABULARY_WRAPPER_H
#define VOCABULARY_WRAPPER_H

#include "lm/model.hh"
#include "util/string_piece.hh" // needs compilation with -DHAVE_ICU


class Vocabulary {
public:
    Vocabulary(const lm::ngram::Model::Vocabulary* vocab = 0);
    lm::WordIndex BeginSentence() const;
    lm::WordIndex EndSentence() const;
    lm::WordIndex NotFound() const;
    lm::WordIndex Index(const StringPiece &str) const;
private:
    const lm::ngram::Model::Vocabulary * vocab_;
};
#endif