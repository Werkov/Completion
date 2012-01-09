#include "model-wrapper.h"

Model::Model(const std::string &str) {
    try {
        std::cerr << "Beg" << std::endl;
        lm::ngram::Config config;
        std::cerr << "A" << std::endl;
        this->enumerate_vocab_ = new TokenDictionary();
        std::cerr << "B" << std::endl;
        config.enumerate_vocab = static_cast<lm::EnumerateVocab*>(this->enumerate_vocab_);
        std::cerr << "C" << std::endl;
        this->model_ = new lm::ngram::Model(str.c_str(), config);
        std::cerr << "D" << std::endl;
    } catch (util::ErrnoException) {
        this->model_ = 0;
//        delete this->enumerate_vocab_;
//        this->enumerate_vocab_ = 0;
        PyErr_SetString(PyExc_IOError, ("File '" + str + "' can't be opened.").c_str());
    }

}

//Model::~Model() {
//    delete this->model_;
//}

Vocabulary Model::GetVocabulary() {
    std::cerr << "cD" << std::endl;
    return Vocabulary(&this->model_->GetVocabulary(), this->enumerate_vocab_);
    if(!this->vocabulary.IsWrapping()){
        this->vocabulary = Vocabulary(&this->model_->GetVocabulary(), this->enumerate_vocab_);
        this->enumerate_vocab_ = 0; // lost ownership, be compatible with destructor
    }
    return this->vocabulary;    
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