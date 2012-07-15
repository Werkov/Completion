%Module kenlm

%Include ../mapped-types.sip

class Model {
%TypeHeaderCode
#include "model-wrapper.h"
%End
public:
    Model(const std::string &str);
    PyObject* vocabulary();
%Docstring
Return frozenset of tokens representing words in model's vocabulary.
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
