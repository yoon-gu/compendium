PAPER     = main
SLUG      = pragma-revolut-foundation-model
BUILD_DIR = build
OUT_PDF   = ../../static/papers/$(SLUG).pdf

.PHONY: all clean publish

all: publish

$(BUILD_DIR)/$(PAPER).pdf: $(PAPER).tex chapters/*.tex references.bib
	mkdir -p $(BUILD_DIR)
	latexmk -xelatex -interaction=nonstopmode -halt-on-error \
	  -outdir=$(BUILD_DIR) $(PAPER).tex

publish: $(BUILD_DIR)/$(PAPER).pdf
	mkdir -p ../../static/papers
	cp $(BUILD_DIR)/$(PAPER).pdf $(OUT_PDF)
	@echo "Published to $(OUT_PDF)"

clean:
	rm -rf $(BUILD_DIR)
