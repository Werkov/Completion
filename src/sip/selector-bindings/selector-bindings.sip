%Module arpaselector

%Include ../mapped-types.sip

class ARPASelector {
%TypeHeaderCode
#include "ARPA-selector.h"
%End
public:
    ARPASelector(const std::string &str);
%MethodCode
    try {
        sipCpp = new ARPASelector(*a0);
    } catch(util::Exception e) {
        PyErr_SetString(PyExc_IOError, e.what());
        sipCpp = 0;
    }
%End

    void reset();
%Docstring
...
%End

    std::vector<std::string> unigramSuggestions(const std::string& prefix);
%Docstring
...
%End

    std::vector<std::string> bigramSuggestions(const std::string& prefix);
%Docstring
...
%End

    void shift(const std::string &token);
%Docstring
...
%End

};



