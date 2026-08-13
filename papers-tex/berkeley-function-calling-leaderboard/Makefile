TEX=/Library/TeX/texbin/latexmk
SLUG=berkeley-function-calling-leaderboard

build:
	$(TEX) -xelatex -interaction=nonstopmode -outdir=build main.tex

publish: build
	cp build/main.pdf ../../static/papers/$(SLUG).pdf

clean:
	$(TEX) -C -outdir=build main.tex || true
