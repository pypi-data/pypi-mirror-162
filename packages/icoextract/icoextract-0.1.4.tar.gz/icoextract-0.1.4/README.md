# icoextract

[![Build Status](https://drone.overdrivenetworks.com/api/badges/jlu5/icoextract/status.svg)](https://drone.overdrivenetworks.com/jlu5/icoextract)

**icoextract** is an icon extractor for Windows PE files (.exe/.dll), written in Python. It also includes a thumbnailer script (`exe-thumbnailer`) for Linux desktops.

This project is inspired by [extract-icon-py](https://github.com/firodj/extract-icon-py), [icoutils](https://www.nongnu.org/icoutils/), and others.

icoextract aims to be:

- Lightweight
- Portable (cross-platform)
- Fast on large files

## Installation

### Installing from source

You can install the project via pip: `pip3 install icoextract[thumbnailer]`

On Linux, you can activate the thumbnailer by copying [`exe-thumbnailer.thumbnailer`](/exe-thumbnailer.thumbnailer) into the thumbnailers directory:

- `/usr/local/share/thumbnailers/` if you installed `icoextract` globally
- `~/.local/share/thumbnailers` if you installed `icoextract` for your user only

The thumbnailer should work with any file manager that implements the [Freedesktop Thumbnails Standard](https://specifications.freedesktop.org/thumbnail-spec/thumbnail-spec-latest.html): this includes Nautilus, Caja, Nemo, Thunar (when Tumbler is installed), and PCManFM. KDE / Dolphin uses a different architecture and is not supported here.

### Distribution packages

icoextract is packaged in these repositories:

- Arch Linux AUR: [icoextract](https://aur.archlinux.org/packages/icoextract)
- Debian (11+): [icoextract](https://packages.debian.org/icoextract)
- Ubuntu (21.10+): [icoextract](https://packages.ubuntu.com/icoextract)

## Usage

icoextract ships `icoextract` and `icolist` scripts to extract and list icon resources in an executable:

```
usage: icoextract [-h] [-V] [-n NUM] [-v] input output

Windows PE EXE icon extractor.

positional arguments:
  input              input filename
  output             output filename

optional arguments:
  -h, --help         show this help message and exit
  -V, --version      show program's version number and exit
  -n NUM, --num NUM  index of icon to extract
  -v, --verbose      enables debug logging
```

```
usage: icolist [-h] [-V] [-v] input

Lists group icons present in a program.

positional arguments:
  input          input filename

optional arguments:
  -h, --help     show this help message and exit
  -V, --version  show program's version number and exit
  -v, --verbose  enables debug logging
```
