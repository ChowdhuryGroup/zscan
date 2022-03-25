# zscan
Script for performing a Z Scan measurement using a linear motorized stage and oscilloscope

# VISA Setup for Keysight Oscilloscope
**Windows**
Default library shared object location: C:\\Windows\\System32\\visa32.dll

Create .pyvisarc file in C:\\Users\\*username*\\ with the contents
```
[Paths]

dll_extra_paths: C:\Program Files\Keysight\IO Libraries Suite\bin;C:\Program Files (x86)\Keysight\IO Libraries Suite\bin
```

**Linux**
Default library shared object location: /opt/keysight/iolibs/libktvisa32.so