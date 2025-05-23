# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXPROJ    = shenfun
SOURCEDIR     = source
BUILDDIR      = build
DEMO          = Poisson/poisson.ipynb \
                KleinGordon/kleingordon.ipynb \
                Poisson3D/poisson3d.ipynb \
				PolarHelmholtz/polarhelmholtz.ipynb \
				SphereHelmholtz/sphericalhelmholtz.ipynb \
				KuramatoSivashinsky/kuramatosivashinsky.ipynb \
				Stokes/stokes.ipynb \
				DrivenCavity/drivencavity.ipynb \
				RayleighBenard/rayleighbenard.ipynb \
				Functions/functions.ipynb \
				Integration/surfaceintegration.ipynb \
				Moebius/moebius.ipynb \
				MixingBases/mixingbases.ipynb \
				Tau/tau.ipynb \
				SparsityChebyshev/sparsity.ipynb
NDEMO         = Poisson/poisson.ipynb2 \
                KleinGordon/kleingordon.ipynb2 \
                Poisson3D/poisson3d.ipynb2 \
				PolarHelmholtz/polarhelmholtz.ipynb2 \
				SphereHelmholtz/sphericalhelmholtz.ipynb2 \
				KuramatoSivashinsky/kuramatosivashinsky.ipynb2 \
				Stokes/stokes.ipynb2 \
				DrivenCavity/drivencavity.ipynb2 \
				RayleighBenard/rayleighbenard.ipynb2 \
				Functions/functions.ipynb2 \
				Integration/surfaceintegration.ipynb2 \
				Moebius/moebius.ipynb2 \
				MixingBases/mixingbases.ipynb2 \
				Tau/tau.ipynb2 \
				SparsityChebyshev/sparsity.ipynb2

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%.rst:
	doconce format sphinx demos/$(basename $@).do.txt --sphinx_preserve_bib_keys
	doconce subst 'XXX' '   ' demos/$(basename $@).rst
	cp demos/$(basename $@).rst source/
	./recite.sh $(notdir $@)

%.ipynb:
	jupyter nbconvert --inplace --execute demos/${basename $@}.ipynb
	cp demos/$(basename $@).ipynb source/

%.ipynb2:
	jupyter nbconvert --inplace --clear-output demos/${basename $@}.ipynb
	cp demos/$(basename $@).ipynb ../../shenfun-demos/content/
	
publish:
	#cd demos && publish export papers.bib && cd ..
	cp demos/papers.bib source/

demos: $(DEMO)

#ipynb: $(NDEMO)
#	make -C ../../shenfun-demos book

pdf:
	@$(SPHINXBUILD) -b latex -d "$(BUILDDIR)"/doctrees $(SOURCEDIR) "$(BUILDDIR)"/latex
	$(MAKE) -C "$(BUILDDIR)"/latex all-pdf LATEXMKOPTS='-interaction=nonstopmode -f -shell-escape'

book: $(NDEMO)

html: publish $(DEMO)
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) -Q $(O)

ohtml:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

doctest:
	@$(SPHINXBUILD) -b doctest -v "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
#%: Makefile
#	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
