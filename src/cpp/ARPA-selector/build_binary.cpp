#include <iostream>
#include <string>
#include <vector>

#include "util/exception.hh"
#include "ARPA-selector.h"
#include "binary-serialization.h"

using namespace std;

typedef vector<string> Args;

void printUsage(const string & binary) {
    cerr << "Usage: " << binary << " [-h] model-file binary-file" << endl;
    cerr << "\t-h\t\tshow the usage" << endl;
    cerr << "\tmodel-file\tARPA file or gzipped ARPA file" << endl;
    cerr << "\tbinary-file\toutput file with binary representation" << endl;
}

const int E_BAD_ARGS = 1;
const int E_BINARY_INPUT = 2;

int main(int argc, char **argv)
{
    Args args(argv, argv + argc);

    try {
        if(args.size() < 2) {
            throw E_BAD_ARGS;
        }
        if(args[1] == "-h") {
            cerr << "Convert language model in ARPA format to binary file for bigram suggestions." << endl;
            printUsage(args[0]);
            return 0;
        }
        if(args.size() < 3) {
            throw E_BAD_ARGS;
        }

        BinarySerialization bs;
        if(bs.isBinary(args[1], false)) {
            throw E_BINARY_INPUT;
        }

        ARPASelector sel(args[1], &bs);
        bs.writeToFile(args[2], &sel);
        return 0;
    }
    catch(int e) {
        switch(e) {
        case E_BAD_ARGS:
            cerr << args[0] << ": too few arguments." << endl;
            printUsage(args[0]);
            break;
        case E_BINARY_INPUT:
            cerr << args[0] << ": file `" << args[1] << "` is already in binary format." << endl;
            break;
        }
        return 1;
    }
    catch(util::Exception e) {
        cerr << args[0] << ": error" << endl;
        cerr << e.what() << endl;
        return 1;
    }
}
