#
style=bootstrap
name=rayleighbenard

.PHONY: all clean

all: ${name}.html

${name}.pdf: ${name}.tex
	doconce format pdflatex ${name} --latex_code_style=pyg-yellowgray --movie_prefix=https://github.com/spectralDNS/spectralutilities/blob/master/movies/
	pdflatex -shell-escape ${name}
	bibtex ${name}
	pdflatex -shell-escape ${name}

${name}.html: ${name}.do.txt
	doconce format html ${name} --html_style=${style} --pygments_html_style=default --html_admon=bootstrap_alert --html_output=${name}_${style} --keep_pygments_html_bg —html_code_style=inherit --html_pre_style=inherit
	doconce subst 'class="col-xs-12"' 'class="col-xs-6"' ${name}_${style}.html
	doconce subst 'XXX' '   ' ${name}_${style}.html
	doconce split_html ${name}_${style}.html

${name}.rst: ${name}.do.txt
	doconce format sphinx ${name} --sphinx_preserve_bib_keys
	doconce subst 'XXX' '   ' $(basename $@).rst

${name}.ipynb: ${name}.do.txt
	doconce format ipynb $(basename $@).do.txt
	#python add_metadata.py $(basename $@).ipynb
	#jupyter nbconvert --inplace --execute ${basename $@}.ipynb

view:
	open ${name}.pdf &

##########################################################################3

clean:
	latexmk -C
