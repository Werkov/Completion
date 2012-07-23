#ifndef ARPA_SELECTOR_H
#define ARPA_SELECTOR_H

#include <string>
#include <vector>
#include <algorithm>
#include <limits>

#include "util/exception.hh"
#include "util/file_piece.hh"
#include "lm/weights.hh"
#include "lm/read_arpa.hh"
#include "util/sorted_uniform.hh"

#include "common.h"
#include "binary-serialization.h"

class BinarySerialization;

class ARPASelector {
public:
    typedef std::vector<std::string> Unigrams;
    typedef std::vector<Offset> Offsets;
    typedef std::vector<WordIndex> Bigrams;


    /**
     * Create selector from ARPA file, gzipped ARPA file or binary file. 
     * Serialization is optional (default is BinarySerialization) and
     * ARPASelector doesn't take ownership.
     * */
    ARPASelector(const std::string & filename, BinarySerialization* serialization = 0);
    

    /**
     * Update context with given token.
     * */
    void shift(const std::string & token);

    /**
     * Reset selector to null context.
     * */
    void reset();

    /**
     * Return suggestions starting with given prefix pruned with current context.
     * Returned order is lexicographic on C++ strings.
     * For null context return always empty list and for unloaded bigrams as well.
     * */
    Unigrams bigramSuggestions(const std::string & prefix = "");

    /**
     * Return suggestions starting with given prefix.
     * Returned order is lexicographic on C++ strings.
     * */
    Unigrams unigramSuggestions(const std::string & prefix = "");


private:
    typedef std::vector<Offsets> BigramMap;
    
    Unigrams unigrams_;
    Bigrams bigrams_;
    Offsets offsets_;

    void loadFromARPA(const std::string & filename);
    WordIndex wordToIndex(const std::string & word) const;    
    WordIndex context_;

    friend class BinarySerialization;
};

#endif // ARPA_SELECTOR_H
