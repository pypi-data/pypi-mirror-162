## Another CLI loading bar...

This is a simple classic CLI loading bar animation for all your CLI loading bar
animation needs, whatever they might be! with lots of customisation options such as displaying percentages, and colour support. This animation can be easily incorporated into any function you want and also makes your CLI look way more professional! - literally from 0 to 100 JUST LIKE THAT!
enjoy ;)

# Also note that the install requires colorama

## Example Code
```python
import math
numbers = [x * 5 for x in range(1000, 3000)]
list = []
for x, i in enumerate(numbers):
    list.append(math.factorial(x))
    tcli_bar.bar(x + 1, len(numbers)) #Here
print('\nDone')
```
## Another example but with colour and more
```python
import math
import tcli_bar
from colorama import *

numbers = [x * 5 for x in range(100, 1500)]
list = []
for i, a in enumerate(numbers):
    list.append(math.factorial(i))
    tcli_bar.bar(i + 1, len(numbers), colour=Fore.GREEN, icon='#', begin='Uploading...', show_percent=False)
print('\nHello')
```
## Results
![example result](/example.png "Output 1")
![example result](/example2.png "Output 2")
![example result](/example3.png "Output 2")

