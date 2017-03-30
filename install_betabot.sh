#!/bin/bash

sudo apt-get update
sudo apt-get upgrade

sudo apt-get install -y git

echo "sudo python /home/pi/betabot/bot.py" >> /etc/rc.local

cp go.sh ~

