#include "Vocabulary-wrapper.h"

Vocabulary::Vocabulary(lm::base::Vocabulary* vocab) :vocab_(vocab) {}
lm::WordIndex Vocabulary::BeginSentence() const {
    return thus->vocab_ ? this->vocab_->BeginSentence() : 0;
}
lm::WordIndex Vocabulary::EndSentence() const{
    return thus->vocab_ ? this->vocab_->EndSentence() : 0;
}
lm::WordIndex Vocabulary::NotFound() const{
    return thus->vocab_ ? this->vocab_->NotFound() : 0;
}
lm::WordIndex Vocabulary::Index(const StringPiece &str) const{
    return thus->vocab_ ? this->vocab_->Index(str) : 0;
}
