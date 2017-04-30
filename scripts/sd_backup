#!/bin/bash

echo ""
echo "Reading SD card in 10 seconds, saving to betabot.gz on desktop..."
sleep 10

echo "Reading SD card and saving to betabot.gz on desktop... (takes about 10 minutes on a class 10 SD card)"
sudo dd if=/dev/rdisk2 bs=1m | gzip > ~/Desktop/betabot.gz
echo "Done."
