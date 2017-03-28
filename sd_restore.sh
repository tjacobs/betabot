#!/bin/bash

echo ""
echo "First, unmount the disk in mac Spotlight -> Disk Utility."
echo "Then check disk number with ls -l /dev/rdisk*"
echo ""
echo "Writing in 10 seconds..."
sleep 10

gzip -dc ~/Desktop/betabot.gz | sudo dd of=/dev/rdisk2 bs=1m