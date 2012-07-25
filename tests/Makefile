#
# REMARK: Run `configure.py` in large-data directory.
#         And set LMPATH environment variable to that directory.
#
# LMPATH=../large-data

# -- Tools --
EMTRAIN=../src/python/trainLinterEM.py
SHELL=/bin/bash
TEST=../src/python/self-eval.py


# default configuration
CONFIG=lmconfig.ini

#
# set of files for testing
#SET=debug.*.txt
SET=test.*.txt

# data which the (test) set is from
#DATA=matka
DATA=wiki.cs

# data for domain adaptation
USERDATA=fykos


# default models set in default configuration file
DEF_LM=$(LMPATH)/$(DATA).train.lm3kni.bin
DEF_SEL=$(LMPATH)/$(DATA).train.lm3kni.sel.bin

#
# ----------------
#
ALL_TESTS=model_order cached_model smoothing_method training_size \
	selector_limit \
	suffix_aggregation prefix_condition suggestion_limit minimal_difference \
	domain_adaptation

.PHONY: $(ALL_TESTS) all

all: $(ALL_TESTS)


#
# -- Model order --

model_order: model_order_1.result model_order_3.result

model_order_1.result: $(LMPATH)/$(DATA).train.lm1kni.bin $(LMPATH)/$(DATA).train.lm1kni.sel.bin $(LMPATH)/$(DATA).$(SET) $(CONFIG)
	$(TEST) -c n -i $(CONFIG) -mlm $(DATA).train.lm1kni.bin -msel $(DATA).train.lm1kni.sel.bin -f $(LMPATH)/$(DATA).$(SET) > $@

model_order_3.result: $(LMPATH)/$(DATA).train.lm3kni.bin $(LMPATH)/$(DATA).train.lm3kni.sel.bin $(LMPATH)/$(DATA).$(SET) $(CONFIG)
	$(TEST) -c n -i $(CONFIG) -mlm $(DATA).train.lm3kni.bin -msel $(DATA).train.lm3kni.sel.bin -f $(LMPATH)/$(DATA).$(SET) > $@

#
# -- Cached model --

cached_model:\
	cached_model_050.result cached_model_0100.result cached_model_0200.result\
	cached_model_n50.result cached_model_n100.result cached_model_n200.result

cached_model_050.result: $(LMPATH)/$(DATA).$(SET) $(CONFIG) cache50.ini
	$(TEST) -c 0c -i $(CONFIG) cache50.ini -f $(LMPATH)/$(DATA).$(SET) > $@

cached_model_0100.result: $(LMPATH)/$(DATA).$(SET) $(CONFIG) cache100.ini
	$(TEST) -c 0c -i $(CONFIG) cache100.ini -f $(LMPATH)/$(DATA).$(SET) > $@

cached_model_0200.result: $(LMPATH)/$(DATA).$(SET) $(CONFIG) cache200.ini
	$(TEST) -c 0c -i $(CONFIG) cache200.ini -f $(LMPATH)/$(DATA).$(SET) > $@

cached_model_n50.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) cache50.ini weights.n50 $(DEF_LM) $(DEF_SEL)
	$(TEST)    -c nc -i $(CONFIG) cache50.ini -f $(LMPATH)/$(DATA).$(SET) `cat weights.n50` > $@

cached_model_n100.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) cache100.ini weights.n100 $(DEF_LM) $(DEF_SEL)
	$(TEST)    -c nc -i $(CONFIG) cache100.ini -f $(LMPATH)/$(DATA).$(SET) `cat weights.n100` > $@

cached_model_n200.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) cache200.ini weights.n200 $(DEF_LM) $(DEF_SEL)
	$(TEST)    -c nc -i $(CONFIG) cache200.ini -f $(LMPATH)/$(DATA).$(SET) `cat weights.n200` > $@

# precalculate weights
weights.n50: $(LMPATH)/$(DATA).em.txt $(CONFIG) cache50.ini $(DEF_LM) $(DEF_SEL)
	$(EMTRAIN) -c nc -i $(CONFIG) cache50.ini -f $< 1>$@ 2>$@.EM

weights.n100: $(LMPATH)/$(DATA).em.txt $(CONFIG) cache100.ini $(DEF_LM) $(DEF_SEL)
	$(EMTRAIN) -c nc -i $(CONFIG) cache100.ini -f $< 1>$@ 2>$@.EM

weights.n200: $(LMPATH)/$(DATA).em.txt $(CONFIG) cache200.ini $(DEF_LM) $(DEF_SEL)
	$(EMTRAIN) -c nc -i $(CONFIG) cache200.ini -f $< 1>$@ 2>$@.EM


#
# -- Smoothing method --
smoothing_method:\
	smoothing_method_no.result smoothing_method_gt.result smoothing_method_kn.result smoothing_method_kni.result\
	# mkni omitted intentionally

smoothing_method_no.result: $(LMPATH)/$(DATA).train.lm3no.bin $(LMPATH)/$(DATA).train.lm3no.sel.bin $(LMPATH)/$(DATA).$(SET) $(CONFIG)
	$(TEST) -c n -i $(CONFIG) -mlm $(DATA).train.lm3no.bin -msel $(DATA).train.lm3no.sel.bin -f $(LMPATH)/$(DATA).$(SET) > $@

smoothing_method_gt.result: $(LMPATH)/$(DATA).train.lm3gt.bin $(LMPATH)/$(DATA).train.lm3gt.sel.bin $(LMPATH)/$(DATA).$(SET) $(CONFIG)
	$(TEST) -c n -i $(CONFIG) -mlm $(DATA).train.lm3gt.bin -msel $(DATA).train.lm3gt.sel.bin -f $(LMPATH)/$(DATA).$(SET) > $@

smoothing_method_kn.result: $(LMPATH)/$(DATA).train.lm3kn.bin $(LMPATH)/$(DATA).train.lm3kn.sel.bin $(LMPATH)/$(DATA).$(SET) $(CONFIG)
	$(TEST) -c n -i $(CONFIG) -mlm $(DATA).train.lm3kn.bin -msel $(DATA).train.lm3kn.sel.bin -f $(LMPATH)/$(DATA).$(SET) > $@

smoothing_method_kni.result: $(LMPATH)/$(DATA).train.lm3kni.bin $(LMPATH)/$(DATA).train.lm3kni.sel.bin $(LMPATH)/$(DATA).$(SET) $(CONFIG)
	$(TEST) -c n -i $(CONFIG) -mlm $(DATA).train.lm3kni.bin -msel $(DATA).train.lm3kni.sel.bin -f $(LMPATH)/$(DATA).$(SET) > $@

smoothing_method_mkni.result: $(LMPATH)/$(DATA).train.lm3mkni.bin $(LMPATH)/$(DATA).train.lm3mkni.sel.bin $(LMPATH)/$(DATA).$(SET) $(CONFIG)
	$(TEST) -c n -i $(CONFIG) -mlm $(DATA).train.lm3mkni.bin -msel $(DATA).train.lm3mkni.sel.bin -f $(LMPATH)/$(DATA).$(SET) > $@

suffix_aggregation: suffix_aggregation_yes.result suffix_aggregation_no.result

#
# -- Training size --
training_size:\
	training_size_big.result training_size_normal.result\
	training_size_small3.result training_size_small2.result training_size_small1.result


training_size_big.result: $(LMPATH)/wiki.en.train.lm3kni.bin $(LMPATH)/wiki.en.train.lm3kni.sel.bin $(LMPATH)/wiki.en.$(SET) $(CONFIG) en.ini weights.size.big.nc
	$(TEST) -c nc -i $(CONFIG) en.ini \
	-mlm wiki.en.train.lm3kni.bin -msel wiki.en.train.lm3kni.sel.bin \
	`cat weights.size.big.nc` \
	-f $(LMPATH)/wiki.en.$(SET) > $@

training_size_normal.result: $(LMPATH)/wiki.cs.train.lm3kni.bin $(LMPATH)/wiki.cs.train.lm3kni.sel.bin $(LMPATH)/wiki.cs.$(SET) $(CONFIG) weights.size.normal.nc
	$(TEST) -c nc -i $(CONFIG) \
	-mlm wiki.cs.train.lm3kni.bin -msel wiki.cs.train.lm3kni.sel.bin \
	`cat weights.size.normal.nc` \
	-f $(LMPATH)/wiki.cs.$(SET) > $@

training_size_small3.result: $(LMPATH)/fykos.train.lm3kni.bin $(LMPATH)/fykos.train.lm3kni.sel.bin $(LMPATH)/fykos.$(SET) $(CONFIG) weights.size.small3.nc
	$(TEST) -c nc -i $(CONFIG) \
	-mlm fykos.train.lm3kni.bin -msel fykos.train.lm3kni.sel.bin \
	`cat weights.size.small3.nc` \
	-f $(LMPATH)/fykos.$(SET) > $@

training_size_small2.result: $(LMPATH)/fykos.train.lm2kni.bin $(LMPATH)/fykos.train.lm2kni.sel.bin $(LMPATH)/fykos.$(SET) $(CONFIG) weights.size.small2.nc
	$(TEST) -c nc -i $(CONFIG) \
	-mlm fykos.train.lm2kni.bin -msel fykos.train.lm2kni.sel.bin \
	`cat weights.size.small2.nc` \
	-f $(LMPATH)/fykos.$(SET) > $@

training_size_small1.result: $(LMPATH)/fykos.train.lm1kni.bin $(LMPATH)/fykos.train.lm1kni.sel.bin $(LMPATH)/fykos.$(SET) $(CONFIG) weights.size.small1.nc
	$(TEST) -c nc -i $(CONFIG) \
	-mlm fykos.train.lm1kni.bin -msel fykos.train.lm1kni.sel.bin \
	`cat weights.size.small1.nc` \
	-f $(LMPATH)/fykos.$(SET) > $@

# estimate weights
weights.size.big.nc: $(LMPATH)/wiki.en.em.txt $(CONFIG) $(LMPATH)/wiki.en.train.lm3kni.bin $(DEF_SEL)
	$(EMTRAIN) -c nc -i $(CONFIG) \
	-mlm wiki.en.train.lm3kni.bin \
	-f $< 1>$@ 2>$@.EM

weights.size.normal.nc: $(LMPATH)/wiki.cs.em.txt $(CONFIG) $(LMPATH)/wiki.cs.train.lm3kni.bin $(DEF_SEL)
	$(EMTRAIN) -c nc -i $(CONFIG) \
	-mlm wiki.cs.train.lm3kni.bin \
	-f $< 1>$@ 2>$@.EM

weights.size.small3.nc: $(LMPATH)/fykos.em.txt $(CONFIG) $(LMPATH)/fykos.train.lm3kni.bin $(DEF_SEL)
	$(EMTRAIN) -c nc -i $(CONFIG) \
	-mlm fykos.train.lm3kni.bin \
	-f $< 1>$@ 2>$@.EM

weights.size.small2.nc: $(LMPATH)/fykos.em.txt $(CONFIG) $(LMPATH)/fykos.train.lm2kni.bin $(DEF_SEL)
	$(EMTRAIN) -c nc -i $(CONFIG) \
	-mlm fykos.train.lm2kni.bin \
	-f $< 1>$@ 2>$@.EM

weights.size.small1.nc: $(LMPATH)/fykos.em.txt $(CONFIG) $(LMPATH)/fykos.train.lm1kni.bin $(DEF_SEL)
	$(EMTRAIN) -c nc -i $(CONFIG) \
	-mlm fykos.train.lm1kni.bin \
	-f $< 1>$@ 2>$@.EM

#
# -- Selector limit --
selector_limit: selector_limit_1000.result selector_limit_3000.result selector_limit_10000.result

selector_limit_1000.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) selector1000.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) selector1000.ini -f $(LMPATH)/$(DATA).$(SET) > $@

selector_limit_3000.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) selector3000.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) selector3000.ini -f $(LMPATH)/$(DATA).$(SET) > $@

selector_limit_10000.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) selector10000.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) selector10000.ini -f $(LMPATH)/$(DATA).$(SET) > $@
	


#
# -- Suffix aggregation --
suffix_aggregation: suffix_aggregation_no.result suffix_aggregation_yes.result

suffix_aggregation_no.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) suffixNo.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) suffixNo.ini -f $(LMPATH)/$(DATA).$(SET) > $@
	
suffix_aggregation_yes.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) suffixYes.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) suffixYes.ini -f $(LMPATH)/$(DATA).$(SET) > $@

#
# -- Prefix condition --
prefix_condition: prefix_condition_no.result prefix_condition_yes.result

prefix_condition_no.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) prefixConditionNo.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) prefixConditionNo.ini -f $(LMPATH)/$(DATA).$(SET) > $@
	
prefix_condition_yes.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) prefixConditionYes.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) prefixConditionYes.ini -f $(LMPATH)/$(DATA).$(SET) > $@

#
# -- Suggestion limit --
suggestion_limit:\
	suggestion_limit_count.result\
	suggestion_limit_prob7.result suggestion_limit_prob6.result suggestion_limit_prob5.result\
	suggestion_limit_both.result

suggestion_limit_count.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) suggestionLimitCount.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) suggestionLimitCount.ini -f $(LMPATH)/$(DATA).$(SET) > $@
	
suggestion_limit_prob7.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) suggestionLimitProb7.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) suggestionLimitProb7.ini -f $(LMPATH)/$(DATA).$(SET) > $@

suggestion_limit_prob6.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) suggestionLimitProb6.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) suggestionLimitProb6.ini -f $(LMPATH)/$(DATA).$(SET) > $@
	
suggestion_limit_prob5.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) suggestionLimitProb5.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) suggestionLimitProb5.ini -f $(LMPATH)/$(DATA).$(SET) > $@
	
suggestion_limit_both.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) suggestionLimitBoth.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) suggestionLimitBoth.ini -f $(LMPATH)/$(DATA).$(SET) > $@


#
# -- Minimal difference --
minimal_difference:\
	minimal_difference_0.result minimal_difference_1.result minimal_difference_2.result


minimal_difference_0.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) minimalDifference0.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) minimalDifference0.ini -f $(LMPATH)/$(DATA).$(SET) > $@

minimal_difference_1.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) minimalDifference1.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) minimalDifference1.ini -f $(LMPATH)/$(DATA).$(SET) > $@

minimal_difference_2.result: $(LMPATH)/$(DATA).$(SET)  $(CONFIG) minimalDifference2.ini $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) minimalDifference2.ini -f $(LMPATH)/$(DATA).$(SET) > $@

#
# -- Domain adaptation --
domain_adaptation: domain_adaptation_no.result domain_adaptation_cache.result domain_adaptation_data.result

domain_adaptation_no.result: $(LMPATH)/$(USERDATA).$(SET)  $(CONFIG) $(DEF_LM) $(DEF_SEL)
	$(TEST) -c n -i $(CONFIG) -f $(LMPATH)/$(USERDATA).$(SET) > $@

domain_adaptation_cache.result: $(LMPATH)/$(USERDATA).$(SET)  $(CONFIG) $(DEF_LM) $(DEF_SEL) weights.domain.nc
	$(TEST) -c nc -i $(CONFIG) \
	`cat weights.domain.nc` \
	-f $(LMPATH)/$(USERDATA).$(SET) > $@

domain_adaptation_data.result:\
 $(LMPATH)/$(USERDATA).$(SET)  $(CONFIG) $(DEF_LM) $(DEF_SEL) weights.domain.nuc\
 $(LMPATH)/$(USERDATA).train.lm3kni.bin $(LMPATH)/$(USERDATA).train.lm3kni.sel.bin
	$(TEST) -c nuc -i $(CONFIG) \
	-ulm $(USERDATA).train.lm3kni.bin -usel $(USERDATA).train.lm3kni.sel.bin \
	`cat weights.domain.nuc` \
	-f $(LMPATH)/$(USERDATA).$(SET) > $@

# weights estimation
weights.domain.nc: $(LMPATH)/$(USERDATA).em.txt $(CONFIG) $(DEF_LM) $(DEF_SEL)
	$(EMTRAIN) -c nc -i $(CONFIG) -f $< 1>$@ 2>$@.EM

weights.domain.nuc: $(LMPATH)/$(USERDATA).em.txt $(CONFIG) $(DEF_LM) $(LMPATH)/$(USERDATA).train.lm3kni.bin $(DEF_SEL)
	$(EMTRAIN) -c nuc -i $(CONFIG) \
	-f $< \
	-ulm $(USERDATA).train.lm3kni.bin 1>$@ 2>$@.EM


#  -- Prepare data & models --
$(LMPATH)/%:
	make -C $(@D) $(@F)

a: $(LMPATH)/wiki.cs.test.*.txt
	echo $<

"t*":
	echo $@
