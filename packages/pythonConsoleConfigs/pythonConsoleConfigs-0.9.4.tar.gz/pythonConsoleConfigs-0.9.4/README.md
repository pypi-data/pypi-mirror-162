# Python Console Configuration

Python Console Configuration is a Python library for customization the output of terminal by color, style and highlight. Also, can have loadings.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Python Console Configuration.

```bash
pip install pythonConsoleConfig
```

## Usage Font

```python
from pythonConsoleConfigs.Font import Color, Style, Highlight

# prints magenta
print(f'{Color.MAGENTA}{"This is a test of Python Console Configuration Library"}')

# prints blink
print(f'{Style.BLINK}{"This is a test of Python Console Configuration Library"}')

# prints highlight blue
print(f'{Highlight.BLUE}{"This is a test of Python Console Configuration Library"}')

# Reset all configuration
Style().reset()

# And so many others ...
```

## Available Configurations
* Colors, Highlights (+ LIGHT)
  * BLACK 
  * RED 
  * GREEN 
  * YELLOW 
  * BLUE 
  * MAGENTA 
  * CYAN 
  * WHITE 
  * GREY
* Styles
  * BOLD 
  * ITALIC 
  * URL 
  * BLINK 
  * BLINK2 
  * SELECTED

## Usage Loading

```python
from pythonConsoleConfigs.Font import Color
from pythonConsoleConfigs.Loading import Box, Percentage

# Boxes loading like: ■■■□□□□□□□
Box(duration=1, size=15, color=Color.BLUE, reverse=True).loading()

# Percentages like: 20%
Percentage(duration=1, rate=10, color=Color.RED).loading()
```

## Available Loading
* Boxes
  * Normal   (■■■□□□□□□□) 
  * Reversed (□□□□□□□■■■) 
  * Duration (seconds)
  * Number of boxes
  * Color

* Percentages
  * Duration (seconds)
  * Rate (by 5%, 10% etc.)
  * Color

## Contact
Contact me using [discord](https://discord.com) for support or requests.
```
GregoryStefanos#1048
```


## License
[Apache License 2.0](http://www.apache.org/licenses/)
