#!/usr/bin/env sh
python setup.py clean sdist bdist_wheel
python -m twine upload dist/*
