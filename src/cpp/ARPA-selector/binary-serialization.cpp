#include "binary-serialization.h"

#include <iostream>

void BinarySerialization::loadFromFile(const std::string& filename, ARPASelector* selector) {
    VERBOSE_INFO("Loading binary file `" << filename << "`.");

    util::scoped_fd fd(util::OpenReadOrThrow(filename.c_str()));
    // load and check header
    BinaryHeader binaryHeader, referenceHeader;
    util::ReadOrThrow(fd.get(), &binaryHeader, sizeof(BinaryHeader));
    referenceHeader.setReference();
    if(!memcmp(&binaryHeader, &referenceHeader, sizeof(BinaryHeader))) {
        UTIL_THROW(util::Exception, "Header of " << filename << " doesn't match expected format.");
    }

    // load metadata
    BinaryMetadata binaryMetadata;
    util::ReadOrThrow(fd.get(), &binaryMetadata, sizeof(BinaryMetadata));

    // load unigram and bigram tables
    size_t mappedSize =
        sizeof(BinaryHeader) +
        sizeof(BinaryMetadata) +
        sizeof(Offset) * binaryMetadata.unigramCount +
        sizeof(WordIndex) * binaryMetadata.bigramCount;

    util::scoped_memory data;
    util::MapRead(util::POPULATE_OR_LAZY, fd.get(), 0, mappedSize, data);

    const Offset* offsetsBegin = reinterpret_cast<const Offset*>(data.begin() + sizeof(BinaryHeader) + sizeof(BinaryMetadata));
    const Offset* offsetsEnd = offsetsBegin + binaryMetadata.unigramCount;
    selector->offsets_ = ARPASelector::Offsets(offsetsBegin, offsetsEnd);

    const WordIndex* bigramsBegin = reinterpret_cast<const WordIndex*>(offsetsEnd);
    selector->bigrams_ = ARPASelector::Bigrams(bigramsBegin, bigramsBegin + binaryMetadata.bigramCount);
    VERBOSE_INFO("Loaded tables for unigrams and bigrams.");

    // load vocabulary (see `ReadWords()` in kenlm/lm/vocab.cc)
    selector->unigrams_ = ARPASelector::Unigrams();
    selector->unigrams_.reserve(binaryMetadata.unigramCount);
    if ((off_t)-1 == lseek(fd.get(), mappedSize, SEEK_SET)) UTIL_THROW(util::ErrnoException, "Seek failed"); // why lm::ngram::SeekOrThrow isn't util SeekOrThrow

    const std::size_t kInitialRead = 16384;
    std::string buffer;
    buffer.reserve(kInitialRead + 100);
    buffer.resize(kInitialRead);
    while (true) {
        ssize_t got = read(fd.get(), &buffer[0], kInitialRead);
        UTIL_THROW_IF(got == -1, util::ErrnoException, "Reading vocabulary words");
        if (got == 0) break;
        buffer.resize(got);
        while (buffer[buffer.size() - 1]) {
            char next_char;
            ssize_t ret = read(fd.get(), &next_char, 1);
            UTIL_THROW_IF(ret == -1, util::ErrnoException, "Reading vocabulary words");
            UTIL_THROW_IF(ret == 0, lm::FormatLoadException, "Missing null terminator on a vocab word.");
            buffer.push_back(next_char);
        }
        // Ok now we have null terminated strings.
        for (const char *i = buffer.data(); i != buffer.data() + buffer.size(); ) {
            std::size_t length = strlen(i);
            selector->unigrams_.push_back(std::string(i, i + length));
            i += length + 1 /* null byte */;
        }
    }
    VERBOSE_INFO("Loaded vocabulary.");
    VERBOSE_INFO("Finished loading.");
}


void BinarySerialization::writeToFile(const std::string& filename, const ARPASelector* selector) {
    VERBOSE_INFO("Writing binary file `" << filename << "`.");
    size_t mappedSize =
        sizeof(BinaryHeader) +
        sizeof(BinaryMetadata) +
        sizeof(Offset) * selector->unigrams_.size() +
        sizeof(WordIndex) * selector->bigrams_.size();

    util::scoped_fd fd;
    uint8_t* data = reinterpret_cast<uint8_t*>(util::MapZeroedWrite(filename.c_str(), mappedSize, fd));
    uint8_t* cursor = data;

    // write header and metadata
    BinaryHeader binaryHeader;
    binaryHeader.setReference();
    *reinterpret_cast<BinaryHeader*>(cursor) = binaryHeader;
    cursor += sizeof(BinaryHeader);

    BinaryMetadata binaryMetadata;
    binaryMetadata.unigramCount = selector->unigrams_.size();
    binaryMetadata.bigramCount = selector->bigrams_.size();
    *reinterpret_cast<BinaryMetadata*>(cursor) = binaryMetadata;
    cursor += sizeof(BinaryMetadata);

    // write offsets to bigram table
    for(ARPASelector::Offsets::const_iterator it = selector->offsets_.begin(); it != selector->offsets_.end(); ++it) {
        *reinterpret_cast<Offset*>(cursor) = *it;
        cursor += sizeof(Offset);
    }

    // write bigram table
    for(ARPASelector::Bigrams::const_iterator it = selector->bigrams_.begin(); it != selector->bigrams_.end(); ++it) {
        *reinterpret_cast<WordIndex*>(cursor) = *it;
        cursor += sizeof(WordIndex);
    }

    // write unigram (word) table concatenated into single string
    std::string buffer;
    for(ARPASelector::Unigrams::const_iterator it = selector->unigrams_.begin(); it != selector->unigrams_.end(); ++it) {
        buffer.append(*it);
        buffer.push_back(0);
    }

    if ((off_t)-1 == lseek(fd.get(), 0, SEEK_END))
        UTIL_THROW(util::ErrnoException, "Failed to seek in binary to vocab words");
    util::WriteOrThrow(fd.get(), buffer.data(), buffer.size());

    // store to disk
    if (msync(reinterpret_cast<void*>(data), mappedSize, MS_SYNC))  {
        UTIL_THROW(util::ErrnoException, "msync failed for " << filename);
    }
    VERBOSE_INFO("Finished writing.");
}

bool BinarySerialization::isBinary(const std::string& filename) {
    util::scoped_fd fd(util::OpenReadOrThrow(filename.c_str()));
    // load and check header
    BinaryHeader binaryHeader, referenceHeader;
    util::ReadOrThrow(fd.get(), &binaryHeader, sizeof(BinaryHeader));
    referenceHeader.setReference();
    if(!memcmp(&(binaryHeader.magicBytes), &(referenceHeader.magicBytes), sizeof(referenceHeader.magicBytes))) {
        return true;
    } else {
        return false;
    }
}


