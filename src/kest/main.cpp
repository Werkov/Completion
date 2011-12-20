#include "lm/model.hh"
#include "foo.hpp"

#include <iostream>
#include <string>
#include <vector>


class MyEnum : public lm::EnumerateVocab {
private:
	size_t size;
	std::vector<std::string> vocab;
public:
	MyEnum() : size(0) {}
	
	virtual ~MyEnum() {}

    virtual void Add(lm::WordIndex index, const StringPiece &str){
		this->size += 1;
		//std::cerr << "adding: " << str.as_string() << std::endl;
		this->vocab.push_back(str.as_string());
	}
	size_t getSize(){
		return this->size;
	}
	void printVocab(){
		std::cerr << "Printing vocab of size: " << this->vocab.size() << std::endl;
		for(std::vector<std::string>::const_iterator it = this->vocab.begin(); it != this->vocab.end(); ++it){
			std::cerr << *it << ", ";
		}
	}
	
};

int main() {
   using namespace lm::ngram;
   MyEnum myEnum;
   Config cnf;
   cnf.enumerate_vocab = &myEnum;
   Model model("../../sample-data/povidky.arpa", cnf);
   State state(model.BeginSentenceState()), out_state;
   const Vocabulary &vocab = model.GetVocabulary();
   std::string word;
   std::cerr << myEnum.getSize() << std::endl;
   myEnum.printVocab();
   while (std::cin >> word) {
     std::cout << model.Score(state, vocab.Index(word), out_state) << '\n';
     state = out_state;
   }
   
   FooContainer* fc = createContainer(10);
   updateContainer(fc);
   std::cout << "Info: " << containerInfo(fc) << std::endl;
 }