# esi-utils-colors

## Introduction

Utility package to standardize some color palettes commonly used by USGS earthquake
hazard products such as ShakeMap, DYFI, and PAGER. 

See tests directory for usage examples.

## Installation

From repository base, run
```
conda create --name colors pip
conda activate colors
pip install -r requirements.txt .
```

## Tests

```
pip install pytest
pytest .
```