# Paper Frame

A image & slow movie player for epaper displays.

Inspired by [Very Slow Movie Player](https://github.com/TomWhitwell/SlowMovie)

## Creating Movie Files

		ffmpeg -i <inputfile> -filter:v scale=800:-1 -an <outfile>


