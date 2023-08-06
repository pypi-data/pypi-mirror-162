## MoveColumn
[![Downloads](https://pepy.tech/badge/movecolumn)](https://pepy.tech/project/movecolumn)
![PyPI - Status](https://img.shields.io/pypi/status/movecolumn)
[![GitHub issues](https://img.shields.io/github/issues/saadbinmunir/movecolumn)](https://github.com/saadbinmunir/movecolumn/issues)
[![GitHub stars](https://img.shields.io/github/stars/saadbinmunir/movecolumn)](https://github.com/saadbinmunir/movecolumn/stargazers)
[![GitHub license](https://img.shields.io/github/license/saadbinmunir/movecolumn)](https://github.com/saadbinmunir/movecolumn/blob/main/LICENSE)

##  About
A creative package to move columns in Python dataframes.

## Requirements

movecolumn requires python 3.6 or greater.

## Installation

Install with pip:

```
pip install movecolumn
```

If you are using the old version of movecolumn and want to update it:

```
pip install --upgrade movecolumn
```

## Examples

```python
import movecolumn as mc

# move column b of dataframe df to first position
df1 = mc.MoveTo1(df,'b')

# move column d to 2nd position
df2 = mc.MoveTo2(df,'d')

# move column d to 3rd position
df3 = mc.MoveTo3(df,'d')

# move column e to 4th position
df4 = mc.MoveTo4(df,'e')

# move column e to 5th position
df5 = mc.MoveTo5(df,'e')

# move column c to last position
df6 = mc.MoveToLast(df,'c')

# move column d to nth position, n = 1 for left most column, 2 for second column
df7 = mc.MoveToN(df,'f',3)

```
