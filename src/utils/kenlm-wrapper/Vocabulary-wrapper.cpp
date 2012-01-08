#include "Vocabulary-wrapper.h"


Vocabulary::Vocabulary(const lm::ngram::Model::Vocabulary* vocab) : vocab_(vocab) {
}

lm::WordIndex Vocabulary::BeginSentence() const {
    return this->vocab_ ? this->vocab_->BeginSentence() : 0;
}

lm::WordIndex Vocabulary::EndSentence() const {
    return this->vocab_ ? this->vocab_->EndSentence() : 0;
}

lm::WordIndex Vocabulary::NotFound() const {
    return this->vocab_ ? this->vocab_->NotFound() : 0;
}

lm::WordIndex Vocabulary::Index(const StringPiece &str) const {
    return this->vocab_ ? this->vocab_->Index(str) : 0;
}
