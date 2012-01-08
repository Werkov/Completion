BIN_DIR=bin
SRC_DIR=.
CXX = g++
MARKER=last_build.time
CXXFLAGS=-O3 -DNDEBUG -DHAVE_ICU
OBJ_NAMES=$(addprefix util/, bit_packing ersatz_progress exception file_piece murmur_hash file mmap) \
          $(addprefix lm/, bhiksha binary_format config lm_exception model quantize read_arpa search_hashed search_trie trie trie_sort virtual_interface vocab)

OBJ=$(addsuffix .o, $(OBJ_NAMES))

$(BIN_DIR)/%.o: $(SRC_DIR)/%.cc
	$(CXX) -I$(SRC_DIR) $(CXXFLAGS) -c $< -o $@

.PHONY: all clean
	
all: $(MARKER)

$(MARKER): $(addprefix $(BIN_DIR)/, $(OBJ))
	touch $@

clean:
	rm -f $(MARKER) $(addprefix $(BIN_DIR)/, $(OBJ))

