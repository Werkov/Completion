%Module ARPAselector


//
// Strings are stored as UTF-8 encoded strings (0 terminated in std::string)
//
%MappedType std::string {
%TypeHeaderCode
#include <string>
%End
%ConvertFromTypeCode
     const char *s = sipCpp->c_str();
     return PyUnicode_FromString(s);
%End


%ConvertToTypeCode
    if (sipIsErr == 0) {
        return (sipPy == Py_None || PyUnicode_Check(sipPy));
    }
    if (sipPy == Py_None) {
        *sipCppPtr = 0;
        return sipGetState(sipTransferObj);
    }

    PyObject* tmpUtf = PyUnicode_AsUTF8String(sipPy);
    *sipCppPtr = new std::string(PyBytes_AS_STRING(tmpUtf));
    Py_DECREF(tmpUtf);
    return sipGetState(sipTransferObj);
%End
};

%MappedType std::vector<std::string>
{
%TypeHeaderCode
#include <vector>
%End

%ConvertFromTypeCode
  PyObject *list;
  if ((list = PyList_New(sipCpp->size())) == 0)
    return 0;

  std::vector<std::string>::iterator it;
  for (it = sipCpp->begin(); it != sipCpp->end(); ++it) {
    PyObject *item;
    if ((item = PyUnicode_FromString(it->c_str())) == 0) {
      Py_DECREF(list);
      return 0;
    }
    PyList_SET_ITEM(list, it - sipCpp->begin(), item);
  }
  return list;
%End

%ConvertToTypeCode
    // see: http://www.riverbankcomputing.co.uk/static/Docs/sip4/directives.html#directive-%ConvertToTypeCode
    if (sipIsErr == 0) {
        return PyList_Check(sipPy);
    }
    if (sipPy == Py_None) {
        *sipCppPtr = 0;
        return sipGetState(sipTransferObj);
    }
    *sipCppPtr = new std::vector<std::string>();
    for (int i = 0; i < PyList_GET_SIZE(sipPy); ++i) {
        std::string* item;
        int state;

        item = reinterpret_cast<std::string *>(sipConvertToType(
                                                PyList_GET_ITEM(sipPy, i),
                                                sipType_std_string, 0,
                                                SIP_NOT_NONE,
                                                &state, sipIsErr));
        if (*sipIsErr) {
            sipReleaseType(item, sipType_std_string, state);
            delete item;
            return 0;
        }

        (*sipCppPtr)->push_back(*item); // inserts copy
        sipReleaseType(item, sipType_std_string, state); // original can be deleter
    }

    return sipGetState(sipTransferObj);
%End
};

%Exception uauauau(SIP_Exception) /PyName=SulectorException,Default/
{
%TypeHeaderCode
#include "util/exception.hh"
%End
%RaiseCode
    const char *detail = sipExceptionRef.what();

    SIP_BLOCK_THREADS
    PyErr_SetString(sipException_std_exception, detail);
    SIP_UNBLOCK_THREADS
%End
};

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
        //PyErr_SetString(PyExc_IOError, std::string("File '" + *a0 + "' can't be loaded.").c_str());
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

