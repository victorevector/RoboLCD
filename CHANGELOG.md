# RoboLCD Changelog

## 1.9.1 (2017-7-21)

### Bug Fixes

* Fixed touch screen support for HDMI-powered C2 screens. 

## 1.9.0 (2017-7-14)

### Improvements

* Motor control screen redesign.

* Custom preheat settings.

* Added 0.05mm increment to Z Offset Wizard.

* Z Offset Wizard measures z offset from corner for accuracy.

* Added confirmation screens to Reset Eeprom, shut down, reboot, reset connection, and delete files and folders

* Added more custom settings to Slicer Wizard: brim, build plate rafts, non-build plate rafts, temperature, and fans on.

### Bug Fixes

* Installing dual extruders do not crash the screen.

* Error message no longer displays "printing" when screen disconnects from motor contorls while printing. It will display real error message.

## 1.8.1 (2017-6-12)

### Bug Fixes

* Installation of RoboLCD does not ignore the new onboard webcam option created in 1.8.0.

## 1.8.0 (2017-6-9)

### Improvements

* New option: see the status of the onboard webcam: on or off; toggle its state (R2 only).

## 1.7.0 (2017-6-1)

### Improvements

* Print Tuning responsive redesign.

* Motors can be disengaged under Utilities>>Options>>Motors Offset.

* Reset connection to printer controls at any time through Utilities>>Options>>Connection.

* Firmware Update has been moved to Utilities>>Options.

* Printer Status screen responsive redesign.

* Support for Error Messages .

* Quick access to temperature controls and motor controls through printer status screen .

* Printing progress bar with elapsed time and remaining added to printer status screen.

* New Fine Tune Z offset wizard: calibrate your z offset to the hundredth of a mm. Can also be used to level your bed.

* New Bed Level Calibration wizard: guides you on how to level your R2's bed.(R2 only)

### Bug Fixes

* Various language edits.

* Filament Load/Change will not mess with temperature while printing, and will set the E-Steps back to normal.

* Onboard sliced files do not have missing meta data.



## 1.6.1 (2017-4-21)

### Bug Fixes

* Restarting octoprint no longer hangs when webcam is on.

* Hotspot mode retry button does not freeze screen.

* Removed connection delays between Octoprint and Mainboard.

* Adjust Z offset decimal styling error in wizard.

* Backing out of filament wizards does not freeze screen.

* QR code is bounded within blue boxes.


## 1.6.0 (2017-4-13)

### Improvements

* Update notification notifies users when OS updates are available

### Bug Fixes

* Screen styling is now compatible with R2 model

## 1.5.0 (2017-3-22)

### Improvements

* New file options available: add, move, traverse and delete folders; move and delete files.

* USB storage directory is mounted in the File's list. All new file options are available within the USB folder.

* Shortcut button added to Motor Control (top right): it will home all axes and move the bed up to the nozzle.

* Support for filament sensor


## 1.4.2 (2017-3-18)

### Bug Fixes

* R2 z offset wizard centers xy correctly

## 1.4.1 (2017-3-16)

### Bug Fixes

* R2 update screen no longer displays available C2 updates

## 1.4.0 (2017-3-15)

### Improvements

* Folder support  

* All usb files get dropped into a USB folder

* Scroll button can now be held down for faster scroll

* Slicing Wizard

* ZOffset is now a z-home offset instead of a z-probe offset. This generates more consistent and reliable z offsets.

### Bug Fixes

* Filament sensor no longer halts rendering of printer dashboard

* Fixed print error when printing from z offset warning popup

## 1.3.2 (2017-3-1)

### Bug Fixes

* Fixed issue where screen appears unresponsive when user pushes the update button: added a Popup that notifies user of background activity.  

##1.3.1 (2017-2-4)

###Bug Fixes

* Fixed issue with detecting R2 Bed

* Fixed issue where R2 bed disconnect freezes screen

* Added heated bed warning to avoid burns during z offset wizard

* Fans turn off after print is done


##1.3.0 (2017-2-3)

###Improvements

* Update Firmware from the Screen

* Display more gcode metadata: estimated time, z offset, infill, layer height, and layer count

* System Menu: Poweroff, Reboot and Restart Octoprint

* Options Menu: Unmount USB and Edit EEPROM settings

* Control temperature for dual extruders and heated bed (if applicable)

* Saves wifi password(s)

* Print tuning: fan speed, feed rate, and flow rate

* Z Offset wizard safeguard: turns off extruder before initiation to avoid melted beds

* Progress bar added for mounting usb files

###Bug Fixes

* Mounting USB can now handle 35+ gcode files

* Cannot update OS with no internet connection

* Mounting USB no longer causes loading delays

##1.2.3 (2017-1-13)

###Improvements

* Utilities-->Update is aware of any RoboOS updates without the need to upgrade RoboLCD source code

##1.2.2 (2017-1-4)

###Improvements

* RoboOS Update available through Utilities --> Update (RoboOS 1.0.4)

###Bug Fixes

* mainboard firmware (RoboOS 1.0.4)

* RoboOS does not time out when you unplug usb while printer is off (RoboOS 1.0.4)

* RoboTheme is updateable via webapp software update (RoboOS 1.0.4)


##1.2.1 (2016-12-23)

###Bug Fixes

* removed update screen's call to action button that would break the screen; replaced it with version number

* filament wizard now retracts after its finished

* filament loading wizard stops extruding after exiting it

* fixed z offset wizard misreading when using blue tape on bed


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
