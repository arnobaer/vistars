# Vistars

Simple [CERN vistars](https://op-webtools.web.cern.ch/vistar/vistars.php) viewer that displays LHC status in fullscreen.

## Install

Install using pip (depends on Python3 and PyQt5).

```bash
pip install git+https://github.com/arnobaer/vistars.git
```

## Usage

At default LHC beam status is displayed.

```bash
vistars
```

Specify an alternate image source using argument `url`. Have a look at [CERN vistars](https://op-webtools.web.cern.ch/vistar/vistars.php) for available screens.

```bash
# display LHC luminosity
vistars https://vistar-capture.web.cern.ch/vistar-capture/lhclumi.png
```

Set a custom update interval in seconds using option `-i <seconds>` (default is 25 seconds).

```bash
vistars -i 10
```

### View modes

The application starts in fullscreen mode. Double click on the vistars screen to toggle between fulscreen and windowed mode.
