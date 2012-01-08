#ifndef MODEL_WRAPPER_H
#define MODEL_WRAPPER_H

#include <sip.h>
#include <string>
#include "lm/model.hh"
#include "Vocabulary-wrapper.h"


class Model {
public:
    Model(const std::string &str);
    ~Model();
    Vocabulary GetVocabulary();
    lm::ngram::State BeginSentenceState();
    lm::ngram::State NullContextState();
    PyObject* Score(const lm::ngram::State& inState, lm::WordIndex word);
private:
    lm::ngram::Model* model_;
};
#endif