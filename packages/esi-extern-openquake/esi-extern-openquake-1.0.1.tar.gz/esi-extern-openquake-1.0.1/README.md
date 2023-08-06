# esi-extern-openquake

## Introduction

Some useful extracts from openquake so that we don't have to install the whole
thing just for these simple but useful functions.

## Installation

From repository base, run
```
conda create --name oq pip
conda activate oq
pip install -r requirements.txt .
```

## Tests

```
pip install pytest
pytest .
```