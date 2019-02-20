# Vistars

Simple CERN vistars viewer.

## Install

```bash
pip install git+https://github.com/arnobaer/vistars.git
```

## Run

```bash
vistars
```

Specify an alternate image source using argument `url`.

```bash
vistars http://example.com/image.png
```

Set a custom update interval in seconds using option `-i <seconds>` (default is 25 seconds).

```bash
vistars -i 10
```
