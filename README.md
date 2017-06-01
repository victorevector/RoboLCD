# Change Log 1.7.0
 - Print Tuning redesign
    - While printing print tuning will be shown, while not printing only fan controls will be shown
 - New Utilities Functions
    - Motors can be disengaged under Utilities >> Options >> Motors Off
    - You can now reset the connection to the printer at any time through the Utilities >> Option >> Connection tool 
    - Firmware Update has been moved to Options
 - Printer Status Redesign
    - New Non Blocking Error Messages
    - Temperature Controls and Motor Controls have been moved to the printer status screen
    - While Printing the screen will now show elapsed time and estimated time remaining
    - Added a progress bar
 - New Wizard Fine Tune Z Offset
 - New Wizard Bed Level Calibration (R2 Only)
 - fixed up and down buttons to have correctly sized elements
 - various language edits
 - Filament Load/Change will not mess with temperature while printing, it will also set the E-Steps back to where they were
 - Onboard sliced files will now be appended with meta data instead of saved directly with meta data


# Setup
If you want to install this repo:

### if you do not already have RoboLCD on the machine go ahead and clone it
```
git clone https://github.com/Robo3D/RoboLCD.git
```
### if you do have RoboLCD  on the machine pull the updates
```
# Make sure you are in the RoboLCD Folder
cd RoboLCD
git pull
```

### Switch to this branch
```
# Make sure you are in the RoboLCD Folder
cd RoboLCD
git checkout [branch name]
```

### install RoboLCD in develop mode
```
source ~/oprint/bin/activate
# Make sure you are in the RoboLCD Folder
cd ~/RoboLCD
python setup.py develop
```
### restart octoprint and pull up the log 
```
sudo service octoprint restart & tail -f ~/.octoprint/logs/octoprint.log
```



