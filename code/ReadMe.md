
This file explains how to run four algorithms / traffic light controlling systems.


[Table 1: Files used.](readMeHelper/FilesUsed.md)

[Original record of how I implemented/coded.](readMeHelper/dayuan.grid.md)



If want to see how to generate all needed files, check out *"[HowToGenerateNeededFiles.md](readMeHelper/HowToGenerateNeededFiles.md)"*. This is helpful when you want to change the parameters to run another experiment with different parameters.

# 1. Static Traffic Lights Controlling System

```python
$ python3 dayuan.grid.staticTL.vTypeDist.simpla.runMe.py > output/runlog.staticTL.currentDateAndTime.md
```

# 2. Actuated Traffic Lights Controlling System

```python
$ python3 dayuan.grid.ATL.vTypeDist.simpla.runMe.py > output/runlog.ATL.currentDateAndTime.md
```

# 3. PALM, my Traffic Lights Controlling System

```python
$ python3 dayuan.grid.myTL.vTypeDist.simpla.runMe.py > output/runlog.myTL.currentDateAndTime.md
```


