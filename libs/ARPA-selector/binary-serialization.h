#ifndef BINARY_SERIALIZATION_H
#define BINARY_SERIALIZATION_H

#include <string>
#include <sys/mman.h>

#include "util/file.hh"
#include "util/exception.hh"

#include "common.h"
#include "ARPA-selector.h"

class ARPASelector;

class BinarySerialization {
public:
    void writeToFile(const std::string & filename, const ARPASelector * selector);
    void loadFromFile(const std::string & filename, ARPASelector * selector);
    bool isBinary(const std::string & filename);
};

namespace {
const char kMagicBytes[] = "lm bigram selector version 1.0\n\0";
struct BinaryHeader {
    char magicBytes[sizeof(kMagicBytes)];
    WordIndex wordIndexCheck;
    Offset offsetsCheck;
    void setReference() {
        memcpy(magicBytes, kMagicBytes, sizeof(kMagicBytes));
        wordIndexCheck = 1;
        offsetsCheck = 1;
    }
};

struct BinaryMetadata {
    size_t unigramCount;
    size_t bigramCount;
};
} //namespace

#endif // BINARY_SERIALIZATION_H
