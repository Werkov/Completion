#include "Vocabulary-wrapper.h"

Vocabulary::Vocabulary(const lm::ngram::Model::Vocabulary* vocab, TokenDictionary* enumerate_vocab)
: vocab_(vocab), enumerate_vocab_(enumerate_vocab), tokens_(0) {
}

Vocabulary::~Vocabulary() {
    std::cerr << "about decring reference " << (int)this->tokens_ << std::endl;
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
        std::cerr << "|voc| " << this->enumerate_vocab_->size() << std::endl;
        this->tokens_ = PyTuple_New(this->enumerate_vocab_->size());
        //this->tokens_ = PyTuple_New(10);
        for (TokenDictionary::const_iterator it = this->enumerate_vocab_->begin(); it != this->enumerate_vocab_->end(); ++it) {
            std::cerr << "tupling (" << (it - this->enumerate_vocab_->begin()) <<"): " << it->size() << std::endl;
            PyTuple_SetItem(this->tokens_, it - this->enumerate_vocab_->begin(), PyUnicode_FromStringAndSize(it->data(), it->size()));
        }
        PyTuple_SetItem(this->tokens_, 0, PyUnicode_FromStringAndSize(this->enumerate_vocab_->begin()->data(), this->enumerate_vocab_->begin()->size()));
        Py_INCREF(this->tokens_); // we also have cached reference to this list
        std::cerr << "Inced reference" << std::endl;
    }
    return this->tokens_;
}
