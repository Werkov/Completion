BIN_DIR=bin
SRC_DIR=.
CXX = g++
MARKER=last_build.time
CXXFLAGS=-O3 -DNDEBUG 
OBJ_NAMES=$(addprefix util/, bit_packing ersatz_progress exception file_piece murmur_hash file mmap) \
          $(addprefix lm/, bhiksha binary_format config lm_exception model quantize read_arpa search_hashed search_trie trie trie_sort virtual_interface vocab)

OBJ=$(addsuffix .o, $(OBJ_NAMES))

$(BIN_DIR)/%.o: $(SRC_DIR)/%.cc
	$(CXX) -I$(SRC_DIR) $(CXXFLAGS) -c $< -o $@

.PHONY: all clean
	
all: $(MARKER) build_binary

$(MARKER): $(addprefix $(BIN_DIR)/, $(OBJ))
	touch $@

build_binary: $(addprefix $(BIN_DIR)/, $(OBJ))
	$(CXX) -I$(SRC_DIR) $(CXXFLAGS) $(SRC_DIR)/lm/build_binary.cc $(addprefix $(BIN_DIR)/, $(OBJ)) -lz -o build_binary

leak_test: $(addprefix $(BIN_DIR)/, $(OBJ))
	$(CXX) -I$(SRC_DIR) $(CXXFLAGS) $(SRC_DIR)/leak_test.cc $(addprefix $(BIN_DIR)/, $(OBJ)) -lz -o leak_test


clean:
	rm -f $(MARKER) $(addprefix $(BIN_DIR)/, $(OBJ))

