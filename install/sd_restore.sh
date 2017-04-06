#!/bin/bash

echo ""
echo "First, unmount the disk in mac Spotlight -> Disk Utility."
echo "Then check disk number with ls -l /dev/rdisk*"
ls -l /dev/rdisk*
echo ""
echo "Writing in 10 seconds..."
sleep 10

echo "Writing... (takes about 10 minutes on a class 10 SD card)"
gzip -dc ~/Desktop/betabot.gz | sudo dd of=/dev/rdisk2 bs=1m
echo "Done."
