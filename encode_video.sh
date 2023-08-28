#!/usr/bin/env bash

filename=$(basename -- "$1")
extension="${filename##*.}"
filename="${filename%.*}"

ffmpeg -i "$1" -filter:v scale=800:-1 -an "$HOME/Downloads/$filename_reduced.$extension"
