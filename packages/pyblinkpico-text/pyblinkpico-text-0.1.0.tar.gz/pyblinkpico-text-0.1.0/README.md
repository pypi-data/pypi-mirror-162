# BlinkPico-Text

This library works in combination with the [BlinkPico](https://github.com/ID220/BlinkPico) library and it allows to show on the display either a single character or a scrolling string.

Available characters are the alphabet letters `a-z` / `A-Z`, digits `0-9`, space, `_`, `.`, `,`, and `⬜️` ("block").

Example:

```python
from pyblinkpico_text import *

character_disp = character()
# A single character
character_disp.show('a')
# Scroll
character_disp.scroll('Hello world')
```
