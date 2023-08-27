# Paper Frame

A image & slow movie player for epaper displays.

Inspired by [Very Slow Movie Player](https://github.com/TomWhitwell/SlowMovie)

## Creating Movie Files

	ffmpeg -i <inputfile> -filter:v scale=800:-1 -an <outfile>

## Setup

## Install system dependencies

Ensure that python3 and pipenv are installed/available on your system.

`ffmpeg` is a required dependency on all platforms.

On a Linux/Raspberry Pi system, you may need to install specific image library dependencies for Pillow to function.

	libwebp6 libtiff5 libjbig0 liblcms2-2 libwebpmux3 libopenjp2-7 libzstd1 libwebpdemux2 libjpeg-dev

Finally, install the python libraries using `pipenv`

	PIPENV_VENV_IN_PROJECT=1 pipenv install
