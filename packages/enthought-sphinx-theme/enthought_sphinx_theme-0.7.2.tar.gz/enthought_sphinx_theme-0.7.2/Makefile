.PHONY: all css

all: css

css: $(wildcard enthought_sphinx_theme/enthought/static/css/*.css)

enthought_sphinx_theme/enthought/static/css/%.css: less/%.less
	lessc $^ > $@.new
	mv -f $@.new $@
