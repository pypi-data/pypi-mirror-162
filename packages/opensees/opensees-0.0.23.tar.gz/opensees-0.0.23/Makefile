APIDOC = python3 tools/doc.py
APIDIR = docs/user/

docs:
	#make apidocs
	#elstir build
	#rm site/**/*.tex
	#rm site/**/*.fig
	/bin/cp plantuml-images/*.svg site/static/
	git add site && git commit -m'cmp - rebuild site' && git subtree push --prefix site/ brace gh-pages

test:
	pytest --nbmake notebooks/
	pytest \
		tests/test_uniaxial.py \
		tests/test_recorder.py \
		tests/Pushover.py

.PHONY: docs
