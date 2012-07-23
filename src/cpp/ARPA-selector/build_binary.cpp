#include <iostream>
#include <string>
#include <vector>
#include <sstream>

#include "util/exception.hh"
#include "ARPA-selector.h"
#include "binary-serialization.h"

using namespace std;

typedef vector<string> Args;

void printUsage(const string & binary) {
    cerr << "Usage: " << binary << " [-h|-c C] model-file binary-file" << endl;
    cerr << "\t-h\t\tshow the usage" << endl;
    cerr << "\t-c C\t\twhen loading ARPA ignore bigrams with logprob < C\t[-5]" << endl;
    cerr << "\tmodel-file\tARPA file or gzipped ARPA file" << endl;
    cerr << "\tbinary-file\toutput file with binary representation" << endl;
}

const int E_BAD_ARGS = 1;
const int E_BINARY_INPUT = 2;

int main(int argc, char **argv)
{
    Args args(argv, argv + argc);
    float crop = -5;
    int shiftArgs = 0;
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
        if(args[1] == "-c") {
            if(args.size() < 5) {
                throw E_BAD_ARGS;
            }
            std::istringstream iss;
            iss.str(args[2]);          
            iss >> crop;
            shiftArgs = 2;
        }

        BinarySerialization bs;
        if(bs.isBinary(args[1+shiftArgs], false)) {
            throw E_BINARY_INPUT;
        }

        ARPASelector sel(args[1+shiftArgs], crop, &bs);
        bs.writeToFile(args[2+shiftArgs], &sel);
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
