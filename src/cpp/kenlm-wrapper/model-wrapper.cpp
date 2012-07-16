#include "model-wrapper.h"

Model::Model(const std::string& str, bool loadVocabulary) {
    try {
        lm::ngram::Config config;
        this->enumerate_vocab_ = new TokenDictionary();
        if(loadVocabulary) {
            config.enumerate_vocab = static_cast<lm::EnumerateVocab*>(this->enumerate_vocab_);
        }
        //this->model_ = new lm::ngram::Model(str.c_str(), config);
        this->model_ = new lm::ngram::QuantArrayTrieModel(str.c_str(), config);

        this->reset();
    } catch (util::ErrnoException) {
        this->model_ = 0;
        PyErr_SetString(PyExc_IOError, std::string("File '" + str + "' can't be opened.").c_str());
    }
}

Model::~Model() {
    delete this->enumerate_vocab_;
    delete this->model_;
}

PyObject* Model::vocabulary() {
    return this->enumerate_vocab_->GetContainer();
}


float Model::probability(const std::string &token, bool changeContext) {
    if(this->model_ == 0) {
        PyErr_SetString(PyExc_RuntimeError, std::string("Model not loaded.").c_str());
        return 0;
    }
    lm::ngram::State outState;
    float result = this->model_->Score(this->state_, this->model_->GetVocabulary().Index(token), outState);
    if(changeContext) {
        this->state_ = outState;
    }
    return result > -30 ? result * 3.3219281 : -100; //scale from base 10 to base 2, crop to -100
}

void Model::shift(const std::string &token) {
    this->probability(token, true);
}

void Model::reset(const std::vector<std::string>& context) {
    if(this->model_ == 0) {
        PyErr_SetString(PyExc_RuntimeError, std::string("Model not loaded.").c_str());
        return;
    }
    if(context.size() == 0) {
        this->state_ = this->model_->BeginSentenceState();
    } else {
        std::vector<lm::WordIndex> indexedContext;
        for(std::vector<std::string>::const_reverse_iterator it = context.rbegin(); it != context.rend(); ++it) {
            indexedContext.push_back(this->model_->GetVocabulary().Index(*it));
        }
        this->model_->GetState(&(*indexedContext.begin()), &(*indexedContext.end()), this->state_);
    }
}
