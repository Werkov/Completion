#ifndef MODEL_WRAPPER_H
#define MODEL_WRAPPER_H

#include <sip.h>
#include <string>
#include <vector>
#include "lm/model.hh"
#include "token-dictionary.h"


class Model {
public:
    Model(const std::string &str);
    ~Model();
    PyObject* vocabulary();
    void reset(const std::vector<std::string>& context = std::vector<std::string>());
    float probability(const std::string &token, bool changeState = true);
private:
    lm::ngram::QuantArrayTrieModel* model_;
    TokenDictionary* enumerate_vocab_; //model wrapper owner until Vocabulary is filled
    lm::ngram::State state_;
};
#endif