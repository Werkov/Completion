#include "ARPA-selector.h"

#include <iostream>
#include <sys/mman.h>

namespace sorting {

class UnigramAccessor {
public:
    typedef std::string Key;

    Key operator()(const ARPASelector::Unigrams::const_iterator it) const {
        return *it;
    }
};
class UnigramPrefixAccessor {
public:
    typedef std::string Key;

    UnigramPrefixAccessor(const std::string & prefix) : prefixLen_(prefix.size()) {}

    Key operator()(const ARPASelector::Unigrams::const_iterator it) const {
        return it->substr(0, prefixLen_);
    }
private:
    size_t prefixLen_;
};

class WordIndexAccessor {
public:
    typedef std::string Key;

    WordIndexAccessor(const ARPASelector::Unigrams & unigrams) :
        unigrams_(unigrams) {}

    const Key & operator()(const WordIndex index) const {
        return unigrams_[index];
    }
private:
    const ARPASelector::Unigrams & unigrams_;
};

class WordIndexPrefixAccessor {
public:
    typedef std::string Key;

    WordIndexPrefixAccessor(const ARPASelector::Unigrams & unigrams, const std::string & prefix) :
        unigrams_(unigrams),
        prefixLen_(prefix.size()) {}

    const Key operator()(const ARPASelector::Bigrams::const_iterator it) const {
        return unigrams_[*it].substr(0, prefixLen_);
    }
private:
    const ARPASelector::Unigrams & unigrams_;
    size_t prefixLen_;
};

class WordIndexComparator {
public:
    WordIndexComparator(const ARPASelector::Unigrams & unigrams) :
        accessor_(unigrams) {}

    bool operator()(WordIndex a, WordIndex b) const {
        return accessor_(a) < accessor_(b);
    }
private:
    const WordIndexAccessor accessor_;
};

} // namespace sorting

ARPASelector::ARPASelector(const std::string& filename, BinarySerialization& serialization) {
    if(serialization.isBinary(filename)) {
        serialization.loadFromFile(filename, this);
    } else {
        loadFromARPA(filename);
    }
    reset();
}

void ARPASelector::loadFromARPA(const std::string& filename) {
    VERBOSE_INFO("Loading ARPA file `" << filename << "`.");
    typedef std::vector<uint64_t> Counts;

    Counts counts;

    util::FilePiece f(filename.c_str(), &std::cerr);
    lm::ReadARPACounts(f, counts);

    if(counts.size() < 2) {
        UTIL_THROW(lm::FormatLoadException, "Selector needs at least a bigram model.");
    }
    lm::ProbBackoff dummy; // we don't need backoff values

    // -- load unigrams --
    unigrams_.reserve(counts[0]);
    BigramMap bigramMap(counts[0]);
    offsets_.resize(counts[0]);

    lm::ReadNGramHeader(f, 1);
    for(uint64_t i = 0; i < counts[0]; ++i) {
        f.ReadFloat(); // probability
        if (f.get() != '\t') UTIL_THROW(lm::FormatLoadException, "Expected tab after probability");
        unigrams_.push_back(f.ReadDelimited(lm::kARPASpaces).as_string());
        lm::ReadBackoff(f, dummy);
    }

    VERBOSE_INFO("Loaded unigrams.");
    std::sort(unigrams_.begin(), unigrams_.end());
    VERBOSE_INFO("Sorted unigrams.");

    // -- load bigrams --
    lm::ReadNGramHeader(f, 2);

    for(uint64_t i = 0; i < counts[1]; ++i) {
        f.ReadFloat(); // probability
        if (f.get() != '\t') UTIL_THROW(lm::FormatLoadException, "Expected tab after probability");
        std::string firstWord = f.ReadDelimited(lm::kARPASpaces).as_string();
        std::string secondWord = f.ReadDelimited(lm::kARPASpaces).as_string();

        uint64_t first  = wordToIndex(firstWord);
        uint64_t second = wordToIndex(secondWord);

        bigramMap[first].push_back(second);

        lm::ReadBackoff(f, dummy);
    }
    VERBOSE_INFO("Loaded bigrams.");

    // -- sort bigrams and create offset table
    sorting::WordIndexComparator cmp(unigrams_);

    Offset currentOffset = 0;
    for(BigramMap::iterator it = bigramMap.begin(); it != bigramMap.end(); ++it) {
        std::sort(it->begin(), it->end(), cmp);
        bigrams_.insert(bigrams_.end(), it->begin(), it->end());
        offsets_[it - bigramMap.begin()] = currentOffset;
        currentOffset += it->size();
        it->clear();
    }

    VERBOSE_INFO("Sorted bigrams.");
    VERBOSE_INFO("Finished loading.");
}

WordIndex ARPASelector::wordToIndex(const std::string& word) const {
    Unigrams::const_iterator result;
    if(util::BinaryFind(sorting::UnigramAccessor(), unigrams_.begin(), unigrams_.end(), word, result)) {
        return (result - unigrams_.begin());
    } else {
        return std::numeric_limits<WordIndex>::max();
    }
}

ARPASelector::Unigrams ARPASelector::unigramSuggestions(const std::string& prefix) {
    Unigrams result;

    sorting::UnigramPrefixAccessor accessor(prefix);
    Unigrams::const_iterator end = util::BinaryBelow(accessor, unigrams_.begin(), unigrams_.end(), prefix);

    Unigrams::const_iterator beg = end;
    while(beg >= unigrams_.begin() && accessor(beg) == prefix) --beg;
    if(beg < end) {
        result.insert(result.end(), beg + 1, end);
    }

    return result;
}


void ARPASelector::shift(const std::string& token) {
    context_ = wordToIndex(token);
}
void ARPASelector::reset()
{
    context_ = std::numeric_limits<WordIndex>::max();
}



ARPASelector::Unigrams ARPASelector::bigramSuggestions(const std::string& prefix) {
    Unigrams result;
    if(context_ == std::numeric_limits<WordIndex>::max()) {
        return result;
    }

    Offset bBegin = offsets_[context_];
    Offset bEnd = (context_ < offsets_.size()) ? offsets_[context_ + 1] : bigrams_.size();

    sorting::WordIndexPrefixAccessor accessor(unigrams_, prefix);
    Bigrams::const_iterator end = util::BinaryBelow(accessor, bigrams_.begin() + bBegin, bigrams_.begin() + bEnd, prefix);

    Bigrams::const_iterator beg = end;
    while(beg >= bigrams_.begin() && accessor(beg) == prefix) --beg;
    for(Bigrams::const_iterator it = beg + 1; it < end; ++it) {
        result.push_back(unigrams_[*it]);
    }

    return result;
}

