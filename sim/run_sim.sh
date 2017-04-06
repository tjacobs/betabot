#!/bin/bash

echo ""
echo "Running Betabot simulator..."

./App_ExampleBrowser &

sleep 1

# PyBullet only runs on Python 2 for now
/usr/bin/python2.7 sim.py

echo "Done."
