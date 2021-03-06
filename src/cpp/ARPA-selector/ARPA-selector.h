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
    ARPASelector(const std::string & filename, float cropProbability, BinarySerialization* serialization = 0);
    

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
     * 
     * Also return probability of given prefix in given context (`prefixProb` parameter).
     * It's a MLE from uniform distribution.
     * 
     * If there are more suggestions than `limit` return empty list. For limit 0 return
     * all suggestions.
     * */
    Unigrams bigramSuggestions(double & prefixProb, const std::string & prefix = "", Offset limit = 0);

    /**
     * Return suggestions starting with given prefix.
     * Returned order is lexicographic on C++ strings.
     * 
     * Also return probability of given prefix (`prefixProb` parameter).
     * It's a MLE from uniform distribution.
     * 
     * If there are more suggestions than `limit` return empty list. For limit 0 return
     * all suggestions.

     * */
    Unigrams unigramSuggestions(double & prefixProb, const std::string & prefix = "", Offset limit = 0);


private:
    typedef std::vector<Offsets> BigramMap;
    
    Unigrams unigrams_;
    Bigrams bigrams_;
    Offsets offsets_;

    void loadFromARPA(const std::string & filename, float cropProbability);
    WordIndex wordToIndex(const std::string & word) const;    
    WordIndex context_;

    friend class BinarySerialization;
};

#endif // ARPA_SELECTOR_H
