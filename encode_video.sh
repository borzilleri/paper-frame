#!/usr/bin/env bash

OUT_FILE=$(basename $1)

ffmpeg -i "$1" -filter:v scale=800:-1 -an "$HOME/Downloads/$OUT_FILE"
