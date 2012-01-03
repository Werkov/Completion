%Module kenlm 0

namespace num{

typedef double value_type;

class Fraction{
%TypeHeaderCode
#include "Fraction.h"
%End
public:
    Fraction();
    Fraction(int a, int b);
    num::Fraction add(num::Fraction b);
    num::Fraction reduce();
    num::value_type val();
    int a;
    int b;
};
};

namespace lm {
    typedef unsigned int WordIndex;
};

%MappedType StringPiece {
%TypeHeaderCode
#include "util/string_piece.hh"
%End
%ConvertFromTypeCode
     const char *s = sipCpp->as_string().c_str();
     return PyBytes_FromString(s);
%End

%ConvertToTypeCode
         // Allow a Python string whenever a string is expected.
         if (sipIsErr == NULL)
             return PyBytes_Check(sipPy);
         if (sipPy == Py_None) {
             *sipCppPtr = NULL;
             return 0;
         }
         if (PyBytes_Check(sipPy)) {
             *sipCppPtr = new StringPiece(PyBytes_AS_STRING(sipPy));
             return 0;
         }
         // *sipCppPtr = (StringPiece *)sipForceConvertTo_std_string(sipPy,sipIsErr);
         *sipCppPtr = 0;
         return 1;
%End


};

class Vocabulary {
%TypeHeaderCode
#include "Vocabulary-wrapper.h"
%End
public:
    lm::WordIndex BeginSentence() const;
    lm::WordIndex EndSentence() const;
    lm::WordIndex NotFound() const;

    lm::WordIndex Index(const StringPiece &str) const;
};

class Model {
%TypeHeaderCode
#include "Model-wrapper.h"
%End
public:
    Model(PyObject* filename);
    Vocabulary GetVocabulary();
    State BeginSentenceState();
    State NullContextState()
    double Score(const State& inState, lm::WordIndex word, State& outState);
};