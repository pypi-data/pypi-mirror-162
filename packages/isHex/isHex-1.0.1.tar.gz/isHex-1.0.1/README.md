# ✅ isHex

Simple Python package to check if string is valid hexadecimal.  

## 🚀 Usage

```python
from isHex import isHex, isHexUpper, isHexLower

# Check invalid hexadecimal
isHex('abcg7') # Returns False

# Check valid hexadecimal
isHex('aBcDeF1234567890') # Returns True

# Check valid hexidecimal, ensuring that it is in uppercase
isHexUpper('ABCDEF') # Returns True
isHexUpper('abcdef') # Returns False

# Check valid hexidecimal, ensuring that it is in lowercase
isHexLower('abcdef') # Returns True
isHexLower('ABCDEF') # Returns False
```

## 📦 Installation

Run the following to install:  

```bash
$ pip install isHex
```

## 👨‍💻 Developing isHex

To install isHex, along with the tools you will need to develop and run tests, run the following in your virtualenv:  

```bash
$ pip install -e .[dev]
```

## 🚦 Development Progress

Unstable Development