#!/bin/bash

sudo apt-get update
sudo apt-get upgrade

sudo apt-get install -y git

sudo pip install python_Xlib
sudo pip install pynput

# Start on startup (insert before the last line of "exit 0") 
sudo sed -i '$i' "$(cat rc.local.line)" /etc/rc.local

# Pi 3 needs its bluetooth disabling, so it uses read UART for SBUS
echo "dtoverlay=pi3-disable-bt" >> /boot/config.txt

# Install convenience script
cp go.sh ~

