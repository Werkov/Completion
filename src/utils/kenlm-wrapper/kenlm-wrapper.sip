%Module kenlm 0


%ModuleHeaderCode
#include "wrapper-helper.h"
#include <iostream>
const unsigned char kMaxOrder = 6;
%End

namespace lm {
    typedef unsigned int WordIndex;
};





// State is converted to three-item list in accordance to lm::ngram::State public fields.
%MappedType lm::ngram::State {
%TypeHeaderCode
    #include "lm/model.hh"
%End

%ConvertFromTypeCode
    return MyPyList_FromState(sipCpp);
%End

%ConvertToTypeCode
         // Allow a Python string whenever a string is expected.
        if (sipIsErr == NULL)
             return PyList_Check(sipPy);
         if (sipPy == Py_None) {
             *sipCppPtr = NULL;
             return 0;
         }
         if (PyList_Check(sipPy)) {
             *sipCppPtr = new lm::ngram::State();
             PyListIntoArray(PyList_GetItem(sipPy, 0), (*sipCppPtr)->words);
             PyListIntoArray(PyList_GetItem(sipPy, 1), (*sipCppPtr)->backoff);
             (*sipCppPtr)->length = (unsigned char)PyLong_AsUnsignedLong(PyList_GetItem(sipPy, 2));
             return 0;
         }
         *sipCppPtr = 0;
         return 1;
%End
};

//
// Strings are stored as UTF-8 encoded strings (null terminated in std::string)
//
%MappedType StringPiece {
%TypeHeaderCode
#include "util/string_piece.hh" // needs compilation with -DHAVE_ICU
%End
%ConvertFromTypeCode
     return PyUnicode_FromStringAndSize(sipCpp->data(), sipCpp->size());
%End

%ConvertToTypeCode
         // Allow a Python string whenever a string is expected.
        if (sipIsErr == NULL)
             return PyUnicode_Check(sipPy);
         if (sipPy == Py_None) {
             *sipCppPtr = NULL;
             return 0;
         }
         if (PyUnicode_Check(sipPy)) {
             *sipCppPtr = new StringPiece(PyBytes_AS_STRING(PyUnicode_AsUTF8String(sipPy)));
             return 0;
         }
         //*sipCppPtr = (std::string*)sipForceConvertTo_std_string(sipPy,sipIsErr);
         *sipCppPtr = 0;
         return 1;
%End
};

%MappedType std::string {
%TypeHeaderCode
#include <string>
%End
%ConvertFromTypeCode
     const char *s = sipCpp->c_str();
     return PyUnicode_FromString(s);
%End

%ConvertToTypeCode
         // Allow a Python string whenever a string is expected.
         if (sipIsErr == NULL)
             return PyUnicode_Check(sipPy);
         if (sipPy == Py_None) {
             *sipCppPtr = NULL;
             return 0;
         }
         if (PyUnicode_Check(sipPy)) {
             *sipCppPtr = new std::string(PyBytes_AS_STRING(PyUnicode_AsUTF8String(sipPy)));
             return 0;
         }
         //*sipCppPtr = (std::string*)sipForceConvertTo_std_string(sipPy,sipIsErr);
         *sipCppPtr = 0;
         return 1;
%End
};

class Vocabulary {
%TypeHeaderCode
#include "vocabulary-wrapper.h"
%End
public:
    lm::WordIndex BeginSentence() const;
    lm::WordIndex EndSentence() const;
    lm::WordIndex NotFound() const;
    lm::WordIndex Index(const StringPiece &str) const;
%Docstring
Convert string into vocabulary entry index.
%End
    PyObject* GetTokens() const; //
%Docstring
Return whole vocabulary of associated model as a tuple (immutable list).
%End
};

class Model {
%TypeHeaderCode
#include "model-wrapper.h"
%End
public:
    Model(const std::string &str);
    Vocabulary GetVocabulary();
%Docstring
Return wrapped vocabulary object. Useful for converting tokens to vocabulary index and listing whole vocabulary.
%End
    lm::ngram::State BeginSentenceState();
    lm::ngram::State NullContextState();
    PyObject* Score(const lm::ngram::State& inState, unsigned int word); // return tuple of score + new state
%Docstring
Return tuple (prob, state), where 'prob' is conditional probability of 'word' given context 'inState'.
'state' is context after the word.
%End
};