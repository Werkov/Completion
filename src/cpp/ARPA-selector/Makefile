BIN_DIR = ../../../bin/selector
SRC_DIR = .
KENLM_BIN_DIR = ../../../bin/kenlm
KENLM_INC_DIR = ../../../libs/kenlm
OFILES = ARPA-selector.o binary-serialization.o
HFILES = ARPA-selector.h binary-serialization.h common.h
KENOFILES = $(addprefix $(KENLM_BIN_DIR)/, util/file_piece.o util/exception.o util/ersatz_progress.o util/mmap.o util/file.o \
	lm/read_arpa.o lm/lm_exception.o)

SHELL=/bin/bash
CXX = g++ 
CPPFLAGS = -DNDEBUG -I. -I $(KENLM_INC_DIR)
CXXFLAGS = -O3 -Wall -W 
LFLAGS = 
LIBS = -lz
.SUFFIXES: .o .cpp 


$(BIN_DIR)/%.o: $(SRC_DIR)/%.cpp $(SRC_DIR)/%.h
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<


all: $(addprefix $(BIN_DIR)/, $(OFILES) build_binary)

$(BIN_DIR)/build_binary: $(SRC_DIR)/build_binary.cpp $(addprefix $(BIN_DIR)/, $(OFILES))
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(addprefix $(BIN_DIR)/, $(OFILES)) $(KENOFILES) $(LIBS) -o $@ $<


clean:
	-rm -f $(addprefix $(BIN_DIR)/, $(OFILES) build_binary)

