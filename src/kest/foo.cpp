#include "foo.hpp"


FooContainer* createContainer(int members) {
	FooContainer* res = new FooContainer();
	res->members = members;
	return res;
}

void disposeContainer(FooContainer* container) {
	delete container;
}

void updateContainer(FooContainer* container) {
	container->members += 1;
}

int containerInfo(FooContainer* container) {
	return container->members;
}

