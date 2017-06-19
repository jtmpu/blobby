#!/bin/bash 

echo "Installing dependencies."
sudo apt install python-flask
sudo apt install python-ws4py
echo "Done."

echo "Setting up bin links."
sudo ln -f -s $(pwd)/blobby.py /usr/bin/blobby

