#!/usr/bin/env sh
set -e
npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/output.css --minify
