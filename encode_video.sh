#!/usr/local/bin/bash

INPUT="/Volumes/Media/Movies/Star Wars - Episode IV - A New Hope (1977)/Star Wars (1977) WEBDL-2160p.mkv"
OUTPUT="/Users/jonathan/Downloads/star_wars.mkv"

ffmpeg -i "$INPUT" -filter:v scale=800:-1 -an "$OUTPUT"

