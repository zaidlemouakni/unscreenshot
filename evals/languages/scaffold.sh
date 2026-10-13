#!/usr/bin/env bash
# Stage the example slide image in the run's working folder.
set -e
cp "$(dirname "$0")/../../examples/languages/source.png" ./source.png
