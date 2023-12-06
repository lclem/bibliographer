#!/bin/bash

pelican -l -r --ignore-cache --extra-settings RELATIVE_URLS=true STORK_INPUT_OPTIONS='{"html_selector": "nobr", "url_prefix" : ""}' BIND='"127.0.0.1"'