## Another CLI loading bar...

This is a simple classic CLI loading bar animation for all your CLI loading bar
animation needs, whatever they might be! with lots of customisation options such as displaying percentages, and colour support. This animation can be easily incorporated into any function you want and also makes your CLI look way more professional! - literally from 0 to 100 JUST LIKE THAT!
enjoy ;)

## Example Code
```python
import math
numbers = [x * 5 for x in range(1000, 3000)]
list = []
for x, i in enumerate(numbers):
    list.append(math.factorial(x))
    tcli_bar.bar(x + 1, 100) #Here
```