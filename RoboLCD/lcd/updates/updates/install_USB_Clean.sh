#! /bin/sh
THIS_DIR=`dirname $0`

echo "Installing!"
cd $THIS_DIR/../assets/USB_Cleaner

mkdir /usr/local/src/USB_Cleaner

cp usb_cleaner.py /usr/local/src/USB_Cleaner/

cp octoprint /etc/init.d/

echo "Finished Installing!"

#store that the update has occured
echo ${0##*/} >> /home/pi/.updates.txt
echo "Update Complete!"
exit 0
