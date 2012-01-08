#ifndef WRAPPER_HELPER_H
#define WRAPPER_HELPER_H

#include <sip.h>
#include "lm/model.hh"

PyObject* MyPyList_FromState(lm::ngram::State* state);

PyObject* arrayToPyList(const lm::WordIndex* array, size_t len);
PyObject* arrayToPyList(const float* array, size_t len);
void PyListIntoArray(PyObject* list, lm::WordIndex* array);
void PyListIntoArray(PyObject* list, float* array);


#endif