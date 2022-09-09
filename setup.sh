#!/usr/bin/env bash

set -e

cd "$(dirname -- "$0";)" || exit 1

if [[ "$(python3 --version)" != "Python 3.10.6" ]]; then
  echo "Python version must be 3.10.6"
  exit 1
fi

if ! pip --version; then
  echo "Install pip"
  exit 1
fi

pip install -r requirements.txt
pre-commit install
pre-commit run &> /dev/null # Run once to initialize environments
