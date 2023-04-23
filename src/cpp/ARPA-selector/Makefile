BIN_DIR = ../../../bin/selector
SRC_DIR = .
KENLM_BIN_DIR = ../../../libs/kenlm
KENLM_INC_DIR = ../../../libs/kenlm
OFILES = ARPA-selector.o binary-serialization.o
HFILES = ARPA-selector.h binary-serialization.h common.h
#KENOFILES = $(addprefix $(KENLM_BIN_DIR)/util/CMakeFiles/kenlm_util.dir/, file_piece.cc.o exception.cc.o ersatz_progress.cc.o mmap.cc.o file.cc.o read_compressed.cc.o) \
#	    $(addprefix $(KENLM_BIN_DIR)/lm/CMakeFiles/kenlm.dir/, read_arpa.cc.o lm_exception.cc.o)
KENOFILES = $(wildcard $(KENLM_BIN_DIR)/util/CMakeFiles/kenlm_util.dir/*.o)\
	    $(wildcard $(KENLM_BIN_DIR)/util/CMakeFiles/kenlm_util.dir/double-conversion/*.o)\
	    $(wildcard $(KENLM_BIN_DIR)/lm/CMakeFiles/kenlm.dir/*.o)

SHELL=/bin/bash
CXX = g++ 
CPPFLAGS = -DNDEBUG -I. -I $(KENLM_INC_DIR) -DKENLM_MAX_ORDER=6
CXXFLAGS = -O3 -Wall -W -fPIC
LFLAGS = 
LIBS = -lz -llzma -lbz2
.SUFFIXES: .o .cpp 


$(BIN_DIR)/%.o: $(SRC_DIR)/%.cpp $(SRC_DIR)/%.h
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<


all: $(addprefix $(BIN_DIR)/, $(OFILES) build_binary)

$(BIN_DIR)/build_binary: $(SRC_DIR)/build_binary.cpp $(addprefix $(BIN_DIR)/, $(OFILES))
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(addprefix $(BIN_DIR)/, $(OFILES)) $(KENOFILES) $(LIBS) -o $@ $<


clean:
	-rm -f $(addprefix $(BIN_DIR)/, $(OFILES) build_binary)

