#include "Model-wrapper.h"

Model::Model(const std::string &str) {
    try {
        this->model_ = new lm::ngram::Model(str.c_str(), lm::ngram::Config());
    } catch (util::ErrnoException) {
        this->model_ = 0;
        PyErr_SetString(PyExc_IOError, ("File '" + str + "' can't be opened.").c_str());
    }

}

Model::~Model() {
    delete this->model_;
}

Vocabulary Model::GetVocabulary() {
    return Vocabulary(&this->model_->GetVocabulary());
}

lm::ngram::State Model::BeginSentenceState() {
    return this->model_->BeginSentenceState();
}

lm::ngram::State Model::NullContextState() {
    return this->model_->NullContextState();
}

double Model::Score(const lm::ngram::State& inState, lm::WordIndex word, lm::ngram::State& outState) {
    return this->model_->Score(inState, word, outState);
}