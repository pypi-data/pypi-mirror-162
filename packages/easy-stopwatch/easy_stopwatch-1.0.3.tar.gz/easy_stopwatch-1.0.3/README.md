# Stopwatch

Homely stopwatch that can do everything that you want

### Installation

```
pip install easy-stopwatch
```

### Documentation

1. Stopwatch(flags_limit:int = 10, ticks:int = 1)
   - _This class creates a stopwatch_
   - _ticks in seconds_
2. start() --> None
   - _This function start a stopwatch_
3. stop() --> None
   - _This function stop a stopwatch_
4. turn_off() --> None
   - _This function turn off a stopwatch_
5. time() --> float
   - _This function return time_
6. put_flag() --> list
   - _This function save a time in **flags**_
   - _When you put up a flag_
   - _**flags**[0] - first flag_
   - _**flags**[1] - second flag_

### Usage

1. Import class _Stopwatch_:
   ```
   from easy_stopwatch import Stopwatch
   ```
2. Create object _stopwatch_:
   ```
   stopwatch = Stopwatch()
   ```
3. Start stopwatch:
   ```
   stopwatch.start()
   ```
4. Print time:
   ```
   print(stopwatch.time())
   ```

### Example code

```
from easy_stopwatch import Stopwatch

stopwatch = Stopwatch()
stopwatch.start()

while 1:
   print(int(stopwatch.time()))
```
