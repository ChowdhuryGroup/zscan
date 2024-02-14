# zscan
Script for performing a Z Scan measurement using a linear motorized stage and oscilloscope

# VISA Setup for Keysight Oscilloscope
**Windows**
Install VISA
Default library shared object location: C:\\Windows\\System32\\visa32.dll

Install [Keysight IO Libraries Suite](https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html)

Create .pyvisarc file in C:\\Users\\*username*\\ with the contents

```
[Paths]
dll_extra_paths: C:\Program Files\Keysight\IO Libraries Suite\bin;C:\Program Files (x86)\Keysight\IO Libraries Suite\bin
```

**Linux**

Install VISA

Default library shared object location: /opt/keysight/iolibs/libktvisa32.so
