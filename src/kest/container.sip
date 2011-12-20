// Define the SIP wrapper to the word library.

%Module container 0

// %TypeHeaderCode
// #include "foo.hpp"
// %End

struct FooContainer {
	int members;
	//float values[4];
};

FooContainer* createContainer(int members);
void disposeContainer(FooContainer* container);
void updateContainer(FooContainer* container);
int containerInfo(FooContainer* container);
