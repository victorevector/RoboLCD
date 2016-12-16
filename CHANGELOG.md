# RoboLCD Changelog

##1.2.0 (2016-12-15)

###Improvements

* Utilities are now displayed as icons

###Bug Fixes

* Incompatibilities with Octoprint 1.3.0 that caused screen to break are now fixed: manually moving the axises no longer freeze the screen

* USB dismounts no longer freeze the screen

##1.1.0 (2016-11-18)

###Improvements

* Flash the current z offset before printing and display a warning if the offset is 10.00

* Alert user when printer is disconnected due to a mainboard firmware flash

* Mintemp warning in Motor Control when you try to manually extrude or retract

###Bug Fixes

* no temperature is entered in temp control screen will no longer crash the screen

* max temp and decimal place limit on temp control screen

* keyboard no longer has two l's

* z offset wizard no longer needs to be run twice to read the correct offset

* back button in z offset wizard no longer jumps around wizard

* load filament wizard will stop extruding after you press the back button

* files list will no longer duplicate files loaded from usb stick

##1.0.2 (2016-11-09)

###Bug Fixes

* fixed update url

##1.0.1 (2016-11-09)

###Bug Fixes

* fixed plugin version issue where software update thought current version was 0.3.0

##1.0.0 (2016-11-09)

###Improvements

* New screen aesthetic

* Production ready application  


##0.3.0 (2016-08-24)

###Improvements

* File and Utilities List are not controlled with buttons for precision

* Wifi status is printed to screen under See my IP Address

* Printer status screen visually enhanced. New buttons, larger extruder temp text, larger tab text etc

* More user friendly keyboard for inputting wifi password

###Bug Fixes

* Incorrect static ip when in hotspot mode

* Changed AP mode to Hotspot (confusing for users who are not familiar with word AP)

* Start wifi hotspot button blends with background_normal

* Asynchronous behavior with Start/Pause button and other devices

* Non uniform filename format

* Crashes when trying to read stl file metadata


##0.2.1 (2016-08-9)

###Improvements

* Added plugin to Software Update check

##0.2.0 (2016-08-08)

###Improvements

* Updated aesthetic direction

##0.1.3 (2016-08-05)

### Bug Fixes

* Running python setup.py install would not copy over .kv files over to installation directory

##0.1.2 (2016-08-05)

### Bug Fixes

* proper version listed in setup.py

##0.1.1 (2016-08-05)

### Bug Fixes

* Kivy app dynamicaly becomes aware of /path/to/RoboLCD/lcd/ . Fixes issue of hardcoded directory paths for custom .kv and Icons files, and kivy app's inability to find these files on different installation paths.

##0.1.0 (2016-08-05)

### Improvements

* See local file list
* Start, pause, and cancel print file
* Connect to Wifi
* Start Hotspot
* Display IP Address and Hostname
* Display QR Code
