#include "wrapper-helper.h"

PyObject* MyPyList_FromState(lm::ngram::State* state) {
     PyObject* result = PyList_New(3);
     PyList_SetItem(result, 0, arrayToPyList(state->words, sizeof(state->words)/sizeof(*state->words)));
     PyList_SetItem(result, 1, arrayToPyList(state->backoff, sizeof(state->backoff)/sizeof(*state->backoff)));
     PyList_SetItem(result, 2, PyLong_FromUnsignedLong(state->length));
    std::cerr << "lm::ngram::result->list: " << (int)state->length << std::endl;
     return result;
}

PyObject* arrayToPyList(const lm::WordIndex* array, size_t len) {
    PyObject* result = PyList_New(len);
    for (size_t i = 0; i < len; ++i) {
        PyList_SetItem(result, i, PyLong_FromUnsignedLong(array[i]));
    }
    return result;
}

PyObject* arrayToPyList(const float* array, size_t len) {
    PyObject* result = PyList_New(len);
    for (size_t i = 0; i < len; ++i) {
        PyList_SetItem(result, i, PyFloat_FromDouble(array[i]));
    }
    return result;
}

void PyListIntoArray(PyObject* list, lm::WordIndex* array) {
    for (size_t i = 0; i < (size_t)PyList_Size(list); ++i) {
        array[i] = (lm::WordIndex) PyLong_AsUnsignedLong(PyList_GetItem(list, i));
    }
}

void PyListIntoArray(PyObject* list, float* array) {
    for (size_t i = 0; i < (size_t)PyList_Size(list); ++i) {
        array[i] = (float) PyFloat_AsDouble(PyList_GetItem(list, i));
    }
}