David


Table of Contents
_________________

1 Check Test
2 Pypi


Learning machine learning with scikit from Tests by David Arroyo
Menéndez


1 Check Test
============

  + In the path:

  ,----
  | $ cd damescikit
  `----

  + Execute all tests:
  ,----
  | $ nosetests3 tests
  `----

  + Execute one file:
  ,----
  | $ nosetests3 tests/test_models.py
  `----

  + Execute one test:
  ,----
  | nosetests3 tests/test_models.py:TddInPythonExample.test_vectorizer_method_returns_correct_result
  `----


2 Pypi
======

  + To install from local:
  $ pip install -e .

  + To install create tar.gz in dist directory:
  $ python3 setup.py register sdist

  + To upload to pypi:
  $ twine upload dist/damenltk-0.1.tar.gz

  + You can install from Internet in a python virtual environment to
    check:
  $ python3 -m venv /tmp/dn $ cd /tmp/dn $ source bin/activate $ pip3
  install damenltk
