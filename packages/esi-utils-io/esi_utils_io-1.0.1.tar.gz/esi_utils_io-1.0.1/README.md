# esi-utils-io

## Introduction

This is a utility package with some common IO functions used by USGS earthquake 
hazard products such as ShakeMap, ground failure, and PAGER.

## Installation

From repository base, run
```
conda create --name io pip
conda activate io
pip install -r requirements.txt .
```

## Tests

```
pip install pytest
pytest .
```