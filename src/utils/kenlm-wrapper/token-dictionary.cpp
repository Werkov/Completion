#include "token-dictionary.h"

void TokenDictionary::Add(lm::WordIndex index, const StringPiece &str){
    //std::cerr << "adding word" << std::endl;
    this->push_back(str);
}