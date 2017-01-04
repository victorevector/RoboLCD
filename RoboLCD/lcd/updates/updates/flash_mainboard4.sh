#!/bin/bash
THIS_DIR=`dirname $0`

#!/bin/bash
HOME_DIR="/home/pi"
VENV="oprint"
OCTO_DIR=$HOME_DIR/OctoPrint
USER_PI="sudo -u pi"

######octoprint plugins #######
install_plugin () {
    $USER_PI $HOME_DIR/$VENV/bin/pip install $1
}


# #AVRDUDE
SERIAL_PATH="/dev/ttyACM0"
flash_arduino () {
     avrdude -p m2560 -c wiring -P $SERIAL_PATH -b 115200 -F -v -U flash:w:$1 -D
}

# #get pyserial
sudo service octoprint stop
sudo pip  install pyserial

# #AVRDude
apt-get install -y avrdude
#flash the board
cd $THIS_DIR/../assets
flash_arduino Marlin.ino.hex
sudo python erase_eeprom.py


#complete the update
echo ${0##*/} >> /home/pi/.updates.txt
echo "Update Complete!"
exit 0