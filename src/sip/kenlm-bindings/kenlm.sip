%Module kenlm

%Include ../mapped-types.sip

class Model {
%TypeHeaderCode
#include "model-wrapper.h"
%End
public:
    Model(const std::string &str, bool loadVocabulary = true);
%MethodCode
    try {
        sipCpp = new Model(*a0, a1);
    } catch(util::Exception e) {
        PyErr_SetString(PyExc_IOError, e.what());
        sipCpp = 0;
    }
%End
    PyObject* vocabulary();
%Docstring
Return frozenset of tokens representing words in model's vocabulary.
When vocabulary isn't loaded, return empty set.
%End
    void reset(const std::vector<std::string>& context = std::vector<std::string>());
%Docstring
Set the model to the state reached by the sequence of given words or to the begin-sentence state.
%End
    float probability(const std::string &token, bool changeContext = true);
%Docstring
Return log2 probability of word in model's current state.
Word is used to change the state of model unless specified changeState = False.

For unknown words -100 is returned.
%End
    void shift(const std::string &token);
%Docstring
Change model's current state with given token.
%End

};
