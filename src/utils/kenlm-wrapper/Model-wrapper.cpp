#include "Model-wrapper.h"
#include "wrapper-helper.h"

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

PyObject* Model::Score(const lm::ngram::State& inState, unsigned int word) {
    lm::ngram::State outState = inState;
    double result = this->model_->Score(inState, (lm::WordIndex)word, outState);
    return Py_BuildValue("(fO)", result, MyPyList_FromState(&outState));
}