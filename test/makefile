PYTHON ?= python3
CB_BINARY ?= ../wme_cb/build/wme_cb
NCB_BINARY ?= ../wme_ncb/build/wme_ncb

all: test-wme

test: test-wme

test-wme:
	$(PYTHON) wme/run_wme_tests.py "$(CB_BINARY)" "$(NCB_BINARY)"

.PHONY: all test test-wme
