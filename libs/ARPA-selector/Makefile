TARGET = test
OFILES = main.o ARPA-selector.o binary-serialization.o
HFILES = ARPA-selector.h binary-serialization.h common.h
KENOFILES = $(addprefix ../kenlm/bin/, util/file_piece.o util/exception.o util/ersatz_progress.o util/mmap.o util/file.o \
	lm/read_arpa.o lm/lm_exception.o)

SHELL=/bin/bash
CC = gcc
CXX = g++ 
LINK = ld
CPPFLAGS = -DNDEBUG -I. -I ../kenlm
CXXFLAGS = -O2 -Wall -W 
LFLAGS = 
LIBS = -lz
.SUFFIXES: .o .cpp 


.cpp.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<


all: $(TARGET)

$(OFILES): $(HFILES)

$(TARGET): $(OFILES)
	$(CXX) -o $(TARGET) $(OFILES) $(KENOFILES) $(LIBS)
#	$(LINK) $(LFLAGS) -o $(TARGET) $(OFILES) #../../../libs/kenlm/bin/{lm,util}/*.o
#	$(LINK) $(LFLAGS) -o $(TARGET) $(OFILES) $(LIBS)


clean:
	-rm -f $(TARGET)
	-rm -f $(OFILES)
