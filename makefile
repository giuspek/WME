PYTHON ?= python3

CB_DIR = wme_cb
NCB_DIR = wme_ncb
CB_BINARY = $(CB_DIR)/build/wme_cb
NCB_BINARY = $(NCB_DIR)/build/wme_ncb

all: cb ncb

$(CB_DIR)/makefile:
	cd $(CB_DIR) && ./configure

$(NCB_DIR)/makefile:
	cd $(NCB_DIR) && ./configure

cb: $(CB_DIR)/makefile
	$(MAKE) -C $(CB_DIR)

ncb: $(NCB_DIR)/makefile
	$(MAKE) -C $(NCB_DIR)

test: all
	$(MAKE) -C test PYTHON="$(PYTHON)" CB_BINARY="../$(CB_BINARY)" NCB_BINARY="../$(NCB_BINARY)" test

clean:
	@if [ -f "$(CB_DIR)/makefile" ]; then $(MAKE) -C $(CB_DIR) clean; fi
	@if [ -f "$(NCB_DIR)/makefile" ]; then $(MAKE) -C $(NCB_DIR) clean; fi

.PHONY: all cb ncb test clean
