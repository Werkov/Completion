TARGET = kenlm-wrapper.o
OFILES = Model-wrapper.o Vocabulary-wrapper.o
HFILES = Model-wrapper.h Vocabulary-wrapper.h

CC = gcc
CXX = g++ 
LINK = ld
CPPFLAGS = -DNDEBUG -DHAVE_ICU -I. -I/afs/ms.mff.cuni.cz/u/k/koutnym/bc/Completion/libs/kenlm -I/usr/include/python3.1
CFLAGS = -O2 -Wall -W
CXXFLAGS = -O2 -Wall -W `pkg-config --libs --cflags icu-uc icu-io` 
LFLAGS = -r
LIBS = -lz
.SUFFIXES: .c .o .cpp .cc .cxx .C


.cpp.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.cc.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.cxx.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.C.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.c.o:
	$(CC) -c $(CFLAGS) $(CPPFLAGS) -o $@ $<

all: $(TARGET)

$(OFILES): $(HFILES)

$(TARGET): $(OFILES)
	$(LINK) $(LFLAGS) -o $(TARGET) $(OFILES) ../../../libs/kenlm/bin/{lm,util}/*.o
#	$(LINK) $(LFLAGS) -o $(TARGET) $(OFILES) $(LIBS)


clean:
	-rm -f $(TARGET)
	-rm -f $(OFILES)
