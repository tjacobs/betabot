#!/bin/bash

echo ""
echo "Running Betabot simulator..."

./App_ExampleBrowser &

sleep 1

/usr/bin/python2.7 sim.py

echo "Done."
