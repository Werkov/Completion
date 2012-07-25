SHELL=/bin/bash

# should be set in the environment
#LMPATH=../large-data

TEST=../src/python/self-eval.py
CONFIG=lmconfig.ini # default configuration

.PHONY: model_order cached_model smoothing_method training_size \
	suffix_aggregation prefix_condition suggestion_limit minimal_difference \
	domain_adaptation


model_order: model_order_1.result model_order_3.result

model_order_1.result: $(LMPATH)/wiki.cs.train.lm1kni.{bin,sel.bin} $(LMPATH)/wiki.cs.test.*.txt $(CONFIG)
	$(TEST) -c n -i $(CONFIG) -mlm wiki.cs.train.lm1kni.bin -msel wiki.cs.train.lm1kni.sel.bin -f $(LMPATH)/wiki.cs.test.*.txt > $@

model_order_3.result: $(LMPATH)/wiki.cs.train.lm3kni.{bin,sel.bin} $(LMPATH)/wiki.cs.test.*.txt $(CONFIG)
	$(TEST) -c n -i $(CONFIG) -mlm wiki.cs.train.lm3kni.bin -msel wiki.cs.train.lm3kni.sel.bin -f $(LMPATH)/wiki.cs.test.*.txt > $@



ax: $(LMPATH)/matka.train.lm3kn.bin
	touch ax

$(LMPATH)/%:
	make -C $(@D) $(@F)


