## Bank of Ghana Exchange Rate Python Library

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Support this Project](#support-these-projects)

## Overview
Current Version: 0.1.0

The unofficial Python API client library for Bank of Ghana allows individuals to pull historical and real-time exchange 
rates data using the Python programming language. 
Learn more by visiting [BOG](https://www.bog.gov.gh/treasury-and-the-markets/historical-interbank-fx-rates/)

## Requirements
```bash
python_requires='>=3.5' or later

install_requires=[
        'requests',
        'pandas',
        'urllib3',
        'bs4',
        'lxml',
        'click',
        'pyfiglet'
    ]
```
## Installation
```shell
$ pip install bank-of-ghana-fx-rates-1.0.1
```

## Usage
```python
>>> from bog.scraper import BankOfGhanaFX

>>> url1 = "https://www.bog.gov.gh/treasury-and-the-markets/treasury-bill-rates/"
>>> url2 = "https://www.bog.gov.gh/treasury-and-the-markets/historical-interbank-fx-rates/"

>>> bg = BankOfGhanaFX(url = url2)
## Run Application
>>> bg.run()
## Get More Information
>>> bg.info()
## OR
>>> BankOfGhanaFX.info()

## APP version
>>> BankOfGhanaFX.VERSION

```

## Support this Project
**YouTube:**
If you'd like to watch more of my content, feel free to visit my YouTube channel [Theophilus Siameh](https://www.youtube.com/channel/UC5tr3-suPn_Y6E9uDxRyKOA).


