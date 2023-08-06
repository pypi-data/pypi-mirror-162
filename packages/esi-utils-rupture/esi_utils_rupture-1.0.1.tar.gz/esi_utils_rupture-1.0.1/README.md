# esi-utils-rupture

## Introduction

Utility package with some helper functions for representing ruptures and computing
rupture distances used by USGS earthquake hazard products such as ShakeMap and 
gmprocess.

See tests directory for usage examples.

## Installation

From repository base, run
```
conda create --name rupture pip
conda activate rupture
pip install --upgrade --no-dependencies https://github.com/gem/oq-engine/archive/engine-3.12.zip
pip install -r requirements.txt .
```

## Tests

```
pip install pytest
pytest .
```