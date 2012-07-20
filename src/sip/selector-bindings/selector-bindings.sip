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
Reset selector to null context.
%End

    std::vector<std::string> unigramSuggestions(const std::string& prefix);
%Docstring
Return suggestions starting with given prefix.
Returned order is lexicographic on C++ strings.
%End

    std::vector<std::string> bigramSuggestions(const std::string& prefix);
%Docstring
Return suggestions starting with given prefix pruned with current context.
Returned order is lexicographic on C++ strings.
For null context return always empty list.
%End

    void shift(const std::string &token);
%Docstring
Update context with given token.
%End

};



