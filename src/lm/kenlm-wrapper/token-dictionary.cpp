#include "token-dictionary.h"

void TokenDictionary::Add(lm::WordIndex index, const StringPiece &str){
    std::string tmp; // StringPiece points still to the same memory, therefore we have to make a copy
    tmp.assign(str.data(), str.size());
    this->push_back(tmp);
}