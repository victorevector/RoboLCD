#setup
If you want to install the new HomeOffset Wizard follow these instructions:

if you do not already have RoboLCD on the machine go ahead and clone it
```
git clone https://github.com/Robo3D/RoboLCD.git
```
if you do have RoboLCD  on the machine pull the updates
```
#make sure you are in the RoboLCD Folder
cd RoboLCD
git pull
```

Switch to the zoffset_update branch
```
#make sure you are in the RoboLCD Folder
cd RoboLCD
git checkout zoffset_update
```

install RoboLCD in develop mode
```
source ~/oprint/bin/activate
#make sure you are in the RoboLCD Folder
cd ~/RoboLCD
python setup.py develop
```
restart octoprint and pull up the log 
```
sudo service octoprint restart & tail -f ~/.octoprint/logs/octoprint.log
```
