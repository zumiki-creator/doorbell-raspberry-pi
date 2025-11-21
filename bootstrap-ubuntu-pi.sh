#!/bin/bash
echo "raspberry PI GPIO and Arduino-iot-cloud"

sudo apt -y update
sudo apt -y upgrade
sudo apt -y install python3-full
sudo apt -y install liblgpio-dev
sudo apt -y install swig

#ubuntu only
sudo apt-get install crossbuild-essential-arm64
sudo apt-get install python3-dev
# ---------------

mkdir ~/app
cd ~/app
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel

pip install gpiozero
pip install RPi-GPIO
pip install RPi-lgpio
pip install arduino-iot-cloud

# install ssh server
sudo apt -y install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
