# polishify

## Setup

Simply

```sh
pip install polishify
```

## Usage

If you have some text that is in Polish but characters look weird it might not be encoded with `windows-1250` or `iso-8859-2` encoding. If your file is `sometext.txt` you may

```sh
polishify sometext.txt
```

and it will show you something like

```
detected encoding is:  windows-1250
```

If you wish to get this file converted to `utf-8` just do

```sh
polishify sometext.txt properly-encoded.txt
```

If you do it in bash script you might not want to see any outputs, the script supports silent mode as follows

```sh
polishify sometext.txt properly-encoded.txt --silent
```

This package contains words with polish letters, you might want to use your own dataset `dataset.json` file.

```sh
polishify sometext.txt properly-encoded.txt --silent --dataset dataset.json
```

We also provide a tool that generates it from a text

```sh
polishify-extract sometext.txt dataset.json --encoding windows-1250
```

## Author

Made by [Marek Narożniak](https://mareknarozniak.com/), for the world and especially people who have people in the family who needs subtitles in Polish and want to bulk convert their encodings. No warranty provided. Licensed under GPL-3.
