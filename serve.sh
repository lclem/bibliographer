#!/bin/bash

pushd docs
python3 -m http.server
popd
