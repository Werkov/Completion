%Module arpaselector


%Include ../mapped-types.sip

class ARPASelector {
%Docstring
Create selector from ARPA file, gzipped ARPA file or binary file.
%End
%TypeHeaderCode
#include "ARPA-selector.h"
%End
public:
    ARPASelector(const std::string &str, float crop = -5);
%MethodCode
    try {
        sipCpp = new ARPASelector(*a0, a1);
    } catch(util::Exception e) {
        PyErr_SetString(PyExc_IOError, e.what());
        sipCpp = 0;
    }
%End

    void reset();
%Docstring
Reset selector to null context.
%End

    std::vector<std::string> unigramSuggestions(double & prefixProb, const std::string& prefix, unsigned int limit);
%Docstring
Return suggestions starting with given prefix.
Returned order is lexicographic on C++ strings.

Also return probability of given prefix (tupled with the list).
It's a MLE from uniform distribution.
%End
//%MethodCode
//     // haha
//%End

    std::vector<std::string> bigramSuggestions(double & prefixProb, const std::string& prefix, unsigned int limit);
%Docstring
Return suggestions starting with given prefix pruned with current context.
Returned order is lexicographic on C++ strings.
For null context return always empty list and for unloaded bigrams as well.

Also return probability of given prefix in given context (tupled with the list).
It's a MLE from uniform distribution.
%End

    void shift(const std::string &token);
%Docstring
Update context with given token.
%End

};



