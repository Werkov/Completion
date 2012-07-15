#ifndef BINARY_SERIALIZATION_H
#define BINARY_SERIALIZATION_H

#include <string>
#include <sys/mman.h>
#include <limits>

#include "util/file.hh"
#include "util/exception.hh"

#include "common.h"
#include "ARPA-selector.h"

class ARPASelector;

class BinarySerialization {
public:
    void writeToFile(const std::string & filename, const ARPASelector * selector);
    void loadFromFile(const std::string & filename, ARPASelector * selector);
    bool isBinary(const std::string & filename, bool checkFormat = true);
};

namespace {
const char kMagicBytes[] = "lm bigram selector version 1.0\n\0";
struct BinaryHeader {
    char magicBytes[sizeof(kMagicBytes)];
    WordIndex wiUnit;
    WordIndex wiMax;
    Offset oUnit;
    Offset oMax;
    void setReference() {
        memcpy(magicBytes, kMagicBytes, sizeof(kMagicBytes));
        wiUnit = 1;
        wiMax = std::numeric_limits<WordIndex>::max();
        oUnit = 1;
        oMax = std::numeric_limits<Offset>::max();
    }
    bool operator==(const BinaryHeader & other){
        return this->wiUnit == other.wiUnit
            && this->wiMax == other.wiMax
            && this->oUnit == other.oUnit
            && this->oMax == other.oMax
            && !memcmp(this->magicBytes, other.magicBytes, sizeof(kMagicBytes));
    }
};

struct BinaryMetadata {
    size_t unigramCount;
    size_t bigramCount;
};
} //namespace

#endif // BINARY_SERIALIZATION_H
