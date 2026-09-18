PYTHON ?= python3

.PHONY: check report doctor preview
check:
	$(PYTHON) -m ais3_bench validate
	$(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) -m ais3_bench report --check
	$(PYTHON) scripts/check_docs.py

report:
	$(PYTHON) -m ais3_bench report

doctor:
	$(PYTHON) -m ais3_bench doctor

preview:
	$(PYTHON) -m ais3_bench run --arm all --model all
