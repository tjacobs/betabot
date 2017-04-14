#!/bin/bash

# Install Betabot.
# Installs the things needed for Betabot to run on a Raspberry Pi 3.

# Update
sudo apt-get update
sudo apt-get upgrade

# Install git
sudo apt-get install -y git
git config --global push.default simple

# Install pynput for keyboard listening
sudo pip install -y python_Xlib
sudo pip install -y pynput

# Install the global Betabot script link
sudo ln /home/pi/betabot/betabot /bin/betabot -fs

# Install the global convenience script link
sudo ln /home/pi/betabot/install/go /bin/go -fs

# Start Betabot on system startup (overrides rc.local)
sudo cp rc.local /etc/rc.local 

# Disable Bluetooth. Raspberry Pi 3 needs its Bluetooth disabling, because Bluetooth uses the serial line and breaks it. 
echo "dtoverlay=pi3-disable-bt" >> /boot/config.txt

