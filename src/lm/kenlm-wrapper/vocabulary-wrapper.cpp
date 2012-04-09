#include "vocabulary-wrapper.h"

Vocabulary::Vocabulary(const lm::ngram::Model::Vocabulary* vocab, TokenDictionary* enumerate_vocab)
: vocab_(vocab), enumerate_vocab_(enumerate_vocab), tokens_(0) {
}

Vocabulary::~Vocabulary() {
    Py_XDECREF(this->tokens_); // we don't need it anymore but someone else can
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

bool Vocabulary::IsWrapping() const {
    return this->vocab_ != 0;
}

PyObject* Vocabulary::GetTokens() {
    if (this->tokens_ == 0) {
        this->tokens_ = PyTuple_New(this->enumerate_vocab_->size());
        for (TokenDictionary::const_iterator it = this->enumerate_vocab_->begin(); it != this->enumerate_vocab_->end(); ++it) {
            PyTuple_SetItem(this->tokens_, it - this->enumerate_vocab_->begin(), PyUnicode_FromString(it->c_str()));
        }
        Py_INCREF(this->tokens_); // we also have cached reference to this list
    }
    return this->tokens_;
}
