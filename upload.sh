#!/bin/bash

tox -e clean
tox -e build
tox -e publish -- --repository pypi