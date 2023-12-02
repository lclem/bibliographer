#!/bin/bash

pelican -l -r --extra-settings RELATIVE_URLS=true STORK_INPUT_OPTIONS='{"html_selector": "nobr", "url_prefix" : ""}'
