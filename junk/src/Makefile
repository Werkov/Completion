.PHONY: dependency
dependency: data.plt
	gnuplot -persist per.plt

data.plt:
	python3 test.py > $@
