#!/bin/bash

echo ""
echo "Open ports 5900 - 5950"
echo "Connect to port 5901"
echo ""

#sudo apt-get install kubuntu-desktop 

sudo apt-get install tightvncserver

vncserver

echo "vncserver &" >> ~/.bashrc

# DISPLAY=:1
# startkde
