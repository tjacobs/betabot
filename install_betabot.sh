#!/bin/bash

sudo apt-get update
sudo apt-get upgrade

sudo apt-get install -y git

echo "sudo python /home/pi/betabot/bot.py" >> /etc/rc.local

# Pi 3 needs its bluetooth disabling, so it uses read UART for SBUS
echo "dtoverlay=pi3-disable-bt" >> /boot/config.txt

cp go.sh ~

