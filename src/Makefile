.PHONY: dependency
dependency: data.plt
	gnuplot per.plt -p

data.plt:
	python3 test.py > $@
