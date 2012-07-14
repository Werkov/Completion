#include <iostream>

#include "util/exception.hh"
#include "ARPA-selector.h"
#include "binary-serialization.h"

using namespace std;

int main(int argc, char **argv)
{
    try {
        BinarySerialization bs;
        ARPASelector sel(argv[1], bs);

        if(argc > 2) {
            bs.writeToFile(argv[2], &sel);
        }
        //std::cerr << sel.wordToIndex(argv[2]) << std::endl;
//     for(ARPASelector::Unigrams::const_iterator it = sel.unigrams_.begin(); it != sel.unigrams_.end(); ++it){
//         std::cerr << *it << std::endl;
//     }
        std::string tmp;
        sel.shift("pan");
        do {
            std::cout << "Ask: ";
            std::cin >> tmp;
            if(tmp == "end") break;
            //    ARPASelector::Unigrams suggestions = sel.bigramSuggestions(tmp);
            ARPASelector::Unigrams suggestions = sel.unigramSuggestions(tmp);
            for(ARPASelector::Unigrams::const_iterator it = suggestions.begin(); it != suggestions.end(); ++it) {
                std::cerr << *it << std::endl;
            }
        } while(1);
        return 0;
    }
    catch(util::Exception e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}
