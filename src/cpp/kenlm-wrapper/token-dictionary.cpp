#include "token-dictionary.h"

TokenDictionary::TokenDictionary() :  immutable_(false), vocabulary_(PyFrozenSet_New(0)) {
    
}

TokenDictionary::~TokenDictionary() {
    Py_DECREF(this->vocabulary_); // we don't need it anymore
    
}

void TokenDictionary::Add(lm::WordIndex index, const StringPiece &str){
    if(!this->immutable_) {
        PyObject* pyString = PyUnicode_FromStringAndSize(str.data(), str.size());        
        PySet_Add(this->vocabulary_, pyString);
        Py_DECREF(pyString);
    } // else raise error?
}

PyObject* TokenDictionary::GetContainer() {
    if(!this->immutable_) { // first time we hand over the container
        this->immutable_ = true; // don't allow adding later
    }
    Py_INCREF(this->vocabulary_); // we also cache the vocabulary object
    return this->vocabulary_;
}