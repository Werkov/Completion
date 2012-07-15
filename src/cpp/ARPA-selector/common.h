#ifndef COMMON_H
#define COMMON_H

#include <iostream>
#include <inttypes.h>

typedef uint32_t Offset;
typedef uint32_t WordIndex;

#define VERBOSE_INFO(messageStream) do { \
    std::cerr << "ARPASelector:\t" << messageStream << std::endl; \
} while(0)


#endif
