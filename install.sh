#!/usr/bin/env bash

sudo apt install python-pyvirtualdisplay

wget [FIREFOX_46]
tar [FIREFOX_46]
mv [FIREFOX_46_BIN] /usr/local/bin
wget https://github.com/mozilla/geckodriver/releases/download/v0.22.0/geckodriver-v0.22.0-linux64.tar.gz
tar xzvf geckodriver-v0.22.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin && rm geckodriver-v0.22.0-linux64.tar.gz


pip install requeriments.txt