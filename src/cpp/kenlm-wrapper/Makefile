BIN_DIR = ../../../bin/kenlm-wrapper
SRC_DIR=.
KENLM_BIN_DIR = ../../../libs/kenlm
KENLM_INC_DIR = ../../../libs/kenlm
TARGET = $(BIN_DIR)/kenlm-wrapper.o
OFILES = model-wrapper.o token-dictionary.o
HFILES = model-wrapper.h token-dictionary.h
KENOFILES = $(addprefix $(KENLM_BIN_DIR)/, {lm/CMakeFiles/kenlm.dir,util/CMakeFiles/kenlm_util.dir}/*.o)
PYINC=`env python3 -c "import distutils.sysconfig as dsc; print(dsc.get_python_inc())"`

SHELL=/bin/bash
CXX = g++ 
LINK = ld
CPPFLAGS = -DNDEBUG -I. -I$(KENLM_INC_DIR) -I$(PYINC) -DKENLM_MAX_ORDER=6
CXXFLAGS = -O3 -Wall -W -fPIC
LFLAGS = -r # relocatable for further linking
LIBS = -lz
.SUFFIXES: .o .cpp


$(BIN_DIR)/%.o: $(SRC_DIR)/%.cpp $(SRC_DIR)/%.h
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<


all: $(TARGET)

$(OFILES): $(HFILES)

$(TARGET): $(addprefix $(BIN_DIR)/, $(OFILES))
	$(LINK) $(LFLAGS) -o $(TARGET) $(addprefix $(BIN_DIR)/, $(OFILES)) $(KENOFILES)

clean:
	-rm -f $(TARGET)
	-rm -f $(addprefix $(BIN_DIR)/, $(OFILES))

