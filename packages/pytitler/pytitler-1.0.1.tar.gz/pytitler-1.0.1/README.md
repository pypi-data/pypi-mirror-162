# pytitler

Python package that allows you to easily make pretty title for your python program

Developed by Flowseal (c) 2022

## How To Use

Installing
```
pip3 install pytitler
```

Code example
```python
from pytitler import pytitler
from pytitler.pytitler import TitleFill, TitleColors

banner = pytitler.align_titles("My first calculator!", center_x=True, center_y=True)
pytitler.print_title(banner, (TitleColors.BLURPLE, (255, 255, 255)), TitleFill.HORIZONTAL)
```

## Gradient types
**Static**: color a text with a static color

**Vertical**: fade a text vertically

**Horizontal**: fade a text horizontally

**Diagonal**: fade a text diagonally

**DiagonalBackwards**: fade a text diagonally but backwards