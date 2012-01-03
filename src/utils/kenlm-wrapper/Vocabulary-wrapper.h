#ifndef VOCABULARY_WRAPPER_H
#define VOCABULARY_WRAPPER_H

#include "lm/word_index.hh"
#include "lm/virtual_interface.hh"
#include "util/string_piece.hh"

class Vocabulary {
public:
    Vocabulary(lm::base::Vocabulary* vocab = 0);
    lm::WordIndex BeginSentence() const;
    lm::WordIndex EndSentence() const;
    lm::WordIndex NotFound() const;
    lm::WordIndex Index(const StringPiece &str) const;
private:
    lm::base::Vocabulary * vocab_;
};
#endif