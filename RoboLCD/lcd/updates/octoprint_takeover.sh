#!/bin/bash
HOME_DIR="/home/pi"
VENV="oprint"
THIS_DIR=`dirname $0`
OCTO_DIR=$HOME_DIR/OctoPrint
USER_PI="sudo -u pi"



kill_octoprint () {
    service octoprint stop
}
#-------------------------------Kivy Update Screen-----------------------------------

python_run () {
    $USER_PI $HOME_DIR/$VENV/bin/python $1
}
#------------------------------ Main Update----------------------------------

#pull up a warning screen
python_run $THIS_DIR/Kivy_Popup_Updater/main.py &

#stop octo print
kill_octoprint

exit 0
