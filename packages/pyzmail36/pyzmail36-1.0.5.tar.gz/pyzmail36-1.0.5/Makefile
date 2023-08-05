epydoc_target=docs/build/html/api
python3=/usr/bin/python3

epydoc:
	mkdir -p ${epydoc_target}
	#--google-analytics "UA-21029552-4"
	epydoc -v -c epydoc.css --google-analytics "UA-21029552-4" -u ../index.html -n "pyzmail homepage" --html pyzmail -o ${epydoc_target}

sphinx:
	cd docs ; make html man
	cp ./docs/build/man/* man
	cp ./docs/build/html/man/* man

test:
	python setup.py test

test3:
	sudo rm -rf build ; ${python3} setup.py test


all: epydoc sphinx upload

docs: epydoc sphinx

clean:
	rm -rf build
	rm -rf docs/build
	rm -rf pyzmail/__pycache__
	rm -rf pyzmail/tests/__pycache__
	find . -name "*.pyc" -exec rm {} \;

upload:
	cp ./docs/build/html/_static/favicon32.ico docs/build/html/favicon.ico
	lftp -f upload.lftp

sdist: sphinx
	python setup.py sdist

pypi: sphinx
	python setup.py sdist upload

