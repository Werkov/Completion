SHELL = bash

WMT_COLLECTION_DIR=${TMT_ROOT}/share/data/resources/wmt/
DATASET = news-dev2009
INPUT_SGM_CS  = $(WMT_COLLECTION_DIR)/*/*/$(DATASET)-ref.cs.sgm
INPUT_SGM_EN  = $(WMT_COLLECTION_DIR)/*/*/$(DATASET)-src.en.sgm

RUNS_DIR = runs_$(DATASET)
PLAIN_INPUT_DIR = $(RUNS_DIR)/plain_input
LINES_PER_FILE = 51

PWD  := $(shell pwd)
DATE := $(shell date +%Y-%m-%d_%H-%M-%S)
# To compute correct NIST you should preserve case, i.e. CASE := -c
CASE :=
SHOW_RECENT := 5
NICE     := 5
#Additional parameters to qrunblocks, e.g.
# QPARAM="--export=TMT_DICT_FILE"
# by default use just orion, tauri, fireball

# Short description of the experiment
D :=
# relative path to the scenario
S          := scenarios/00_best.scen
SCENARIO   := $(PWD)/$(S)
SHORT_SCEN := $(notdir $(basename $(SCENARIO)))
ALL_RES    := res_$(DATASET).tsv

BASE_TRY := $(shell [ -r $(RUNS_DIR)/baseline ] && echo -n $(RUNS_DIR)/ && cat $(RUNS_DIR)/baseline || echo no_baseline_available )
LAST_TRY := $(shell ls -d -t $(RUNS_DIR)/[0-9]* 2>/dev/null | head -n 1)
NEW_NUM  := $(shell perl -e '$$m=0; for(<$(RUNS_DIR)/*>){/\/(\d+)_/ and $$1 > $$m and $$m=$$1;} printf "%03d", $$m+1;')
NEW_TRY  := $(RUNS_DIR)/$(NEW_NUM)_$(DATE)_$(SHORT_SCEN)

# cluster settings
JOBS=21
MEM=10g
#QUEUE := '*@t*,*@f*,*@o*,*@c*' #no hyperion, just tauri, fireball, orion and cosmos - there are no such names on the new cluster
QUEUE := '*'
QPARAMS := "-q $(QUEUE) -hard -l mem_free=$(MEM) -l act_mem_free=$(MEM)"

CMPT=${TMT_ROOT}/tools/compare_translations


info:
	# For help on this Makefile run 'make help'
	# Your current baseline is saved in    $(BASE_TRY)
	# Your last experiment is saved in     $(LAST_TRY)
	# New experiment would be now saved to $(NEW_TRY)

define HELP_MESSAGE
# USAGE:
# First you need to convert sgm files to tmt files
make in
# This command converted files from $(DATASET)
# You can change it with e.g.
make in DATASET=newstest2011
# Now translate and evaluate all files with the scenario $(S)
make translate eval
# Now try an alternative scenario
make translate eval S=scenarios/02_my_alternative.scen
# All the experiments are saved in $(RUNS_DIR) in a subdirectory with current date in name.
# You can add a short description of the experiment to be logged:
make translate eval D="changed regexp in block XY"
# Useful comparison of outputs of the two scenarios is saved in compared_with_* files. You can see the same info with
make compare
# which compares the baseline with the last experiment.
# To set the last experiment as the baseline (after you have checked it is better than the previous one) write
make baseline
# This will print the name of the last experiment directory to $(RUNS_DIR)/baseline.
# If you want to comfortably set another experiment as the baseline, look up its prefix number, e.g.
make baseline-042
# will set $(RUNS_DIR)/042_2010-01-14_14-07-02_my_scenario (let's say) as the baseline.
# To compare experiments with numbers 042 and 046 (without changing $(RUNS_DIR)/baseline) run:
make compare-042:046
# To evaluate experiment number 046 (if you have forgotten to add eval after translate):
make eval-046
# If you don't want to print commands being executed, use "make -s".
endef
export HELP_MESSAGE

help:
	@echo "$$HELP_MESSAGE" | egrep --color '^(make.*|)'

# Set the last experiment as the baseline
baseline:
	echo $(notdir $(LAST_TRY)) > $(RUNS_DIR)/baseline

# Set the experiment with given prefix number as the baseline
baseline-%:
	basename $(RUNS_DIR)/$*_* > $(RUNS_DIR)/baseline

tr translate: $(PLAIN_INPUT_DIR)
	@mkdir -p $(NEW_TRY)/treexfiles
	@svn info | grep Revision | cut -c 11- > $(NEW_TRY)/svn_revision
	echo "$(D)" > $(NEW_TRY)/description
	treex -d $(SCENARIO) > $(NEW_TRY)/scenario.scen
	mkdir -p $(NEW_TRY)/treexfiles/

	time treex -p --jobs=$(JOBS) --qsub=$(QPARAMS) --workdir=$(NEW_TRY) \
	Read::AlignedSentences en_src=\" $(PLAIN_INPUT_DIR)/en* \" cs_ref=\" $(PLAIN_INPUT_DIR)/cs* \" \
	$(SCENARIO) \
	Write::Treex path=$(NEW_TRY)/treexfiles/ Write::TranslationResume source_language=en > $(NEW_TRY)/output.txt

	cat $(NEW_TRY)/output.txt | grep '^TST' | cut -f 2- > $(NEW_TRY)/plain_output.txt

	@rm -f $(NEW_TRY)/treexfiles/*~
	@make -s print_warn          LAST_TRY=$(NEW_TRY) > $(NEW_TRY)/log_warn
	@make -s print_uninitialized LAST_TRY=$(NEW_TRY) > $(NEW_TRY)/log_uninitialized
	head $(NEW_TRY)/log_*


in: $(PLAIN_INPUT_DIR)

# extracting input plain-text data from sgm files
$(PLAIN_INPUT_DIR):
	mkdir -p $(PLAIN_INPUT_DIR)
	@echo First run for $(DATASET), preparing input plain-text files in $(PLAIN_INPUT_DIR)
	cat $(INPUT_SGM_EN) | perl -nle '/^<seg[^>]*> ?([^<]+)</ && print $$1;'> $(PLAIN_INPUT_DIR)/all-en.txt
	cat $(INPUT_SGM_CS) | perl -nle '/^<seg[^>]*> ?([^<]+)</ && print $$1;'> $(PLAIN_INPUT_DIR)/all-cs.txt
	split -d -l $(LINES_PER_FILE) $(PLAIN_INPUT_DIR)/all-en.txt $(PLAIN_INPUT_DIR)/en-$(DATASET)_
	split -d -l $(LINES_PER_FILE) $(PLAIN_INPUT_DIR)/all-cs.txt $(PLAIN_INPUT_DIR)/cs-$(DATASET)_

eval:
	@echo Preparing data in $(NEW_TRY)/results
	mkdir -p $(NEW_TRY)/results
	cat $(NEW_TRY)/plain_output.txt | \
	 ${TMT_ROOT}/share/data/resources/wmt/2010/scripts/wrap-xml.perl cz $(INPUT_SGM_EN) TectoMT > $(NEW_TRY)/results/$(DATASET)-tst.cz.sgm
	export TMT_VERSION=`cat $(NEW_TRY)/svn_revision` && \
	export DESCRIPTION=`cat $(NEW_TRY)/description` && \
	${TMT_ROOT}/share/external_tools/mteval/mteval-v11b.pl $(CASE) \
	 -r $(INPUT_SGM_CS) \
	 -s $(INPUT_SGM_EN) \
	 -t $(NEW_TRY)/results/$(DATASET)-tst.cz.sgm |\
	 tee $(NEW_TRY)/results/$(DATASET)_results.score |\
	 perl -ne 'print join("\t",$$2,$$1,"$(DATASET)/$(NEW_NUM)","$(DATE)","$(SHORT_SCEN)","r$$ENV{TMT_VERSION} $$ENV{DESCRIPTION}"),"\n" if /^NIST score = (.{6})  BLEU score = (.{6})/' >> $(ALL_RES)
	tail -n $(SHOW_RECENT) $(ALL_RES)
	@[[ -e $(BASE_TRY)/output.txt ]] && ./compare_stats.pl --no_color $(BASE_TRY)/output.txt $(NEW_TRY)/output.txt > $(NEW_TRY)/compared_with_$(notdir $(BASE_TRY)).txt || echo "Comparison skipped, since there is no previous baseline experiment to compare with."

print_uninitialized:
	grep -h 'uninitialized value' $(LAST_TRY)/output/*.stderr | sed 's/<GEN.*//; s/.*Use of uninitialized value//' | sort | uniq -c | sort -rn

print_warn:
	grep -h WARN $(LAST_TRY)/output/*.stderr | sed 's/\(TREEX\|TMT\)-WARN:.//;s/\(Two lex a-nodes\).*/\1/' | sort | uniq -c | sort -rn

print_fatal:
	grep -h FATAL $(LAST_TRY)/output/*.stderr | sed 's/\(TREEX\|TMT\)-FATAL:.//' | sort | uniq -c | sort -rn

c compare:
	./compare_stats.pl $(BASE_TRY)/output.txt $(LAST_TRY)/output.txt | less -R

compare-%:
	./compare_stats.pl $(RUNS_DIR)/`echo $* | cut -d: -f1`*/output.txt $(RUNS_DIR)/`echo $* | cut -d: -f2`*/output.txt | less -R

d:
	./compare_stats.pl --hide_zero $(BASE_TRY)/output.txt $(LAST_TRY)/output.txt | less -R

# make eval-042 evaluates experiment number 042
# make align-042 alignes experiment number 042 etc.
TARGETS := eval align substitutions
$(foreach TRG,$(TARGETS),$(TRG)-%):
	make $(@:-$*=) NEW_NUM=$* NEW_TRY=`ls -d $(RUNS_DIR)/$*_*`

clean:
	rm -rf $(LAST_TRY)
	# To delete all generated files (in directories input_* runs_*) run make realclean

realclean:
	rm -rf runs_* res_*.tsv

## Training of cs ref-tst substitutions
align: $(NEW_TRY)/alignment.tsv
$(NEW_TRY)/alignment.tsv:
	@echo Aligninig cs_ref and cs_tst
	mkdir -p $(NEW_TRY)/work_align
	time treex -p --workdir=$(NEW_TRY)/work_align --jobs=$(JOBS) scenarios/s5_refcs_alignment.scen -g "$(NEW_TRY)/treexfiles/*.treex" > $(NEW_TRY)/alignment.tsv

substitutions: $(NEW_TRY)/substitutions.tsv
$(NEW_TRY)/substitutions.tsv: $(NEW_TRY)/alignment.tsv
	cat $(NEW_TRY)/alignment.tsv | ./sum_alignment.pl > $@

available_datasets:
	@echo WMT_COLLECTION_DIR=$(WMT_COLLECTION_DIR)
	@cd $(WMT_COLLECTION_DIR) && for DS in nc-dev2007 nc-test2007 nc-test2008 newstest2008 news-dev2009 newstest2009 newstest2010 newstest2011; do\
	  echo -n "$$DS	"; ls -m */*/$${DS}-{src.en,ref.cs}.sgm;\
	done

available_alignments:
	ls -1 runs*/*/alignment.tsv

cs_wmt2007-2010.tsv:
	cat runs*/*/alignment.tsv | ./sum_alignment.pl > $@
	#cp $@ ${TMT_ROOT}/share/data/models/translation/substitutions/