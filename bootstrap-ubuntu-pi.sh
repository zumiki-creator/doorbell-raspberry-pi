#!/bin/bash
echo "raspberry PI GPIO and Arduino-iot-cloud"

sudo apt -y update
sudo apt -y upgrade
sudo apt -y install python3-full
sudo apt -y install liblgpio-dev
sudo apt -y install swig
sudo apt -y install git

#git repo clone
git config --global user.name "app"
git config --global user.email "app@localhost.com"
git clone https://github.com/zumiki-creator/doorbell-raspberry-pi.git /home/iot/app

#ubuntu only
sudo apt-get install crossbuild-essential-arm64
sudo apt-get install python3-dev
# ---------------

cd /home/iot/app
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel

pip install gpiozero
pip install RPi-GPIO
pip install RPi-lgpio
pip install arduino-iot-cloud

# create app service   
chmod +x /home/iot/app/run-app.sh
sudo cp /home/iot/app/bootstrap/doorbell.service /etc/systemd/system/doorbell.service
sudo systemctl enable doorbell.service
sudo systemctl start doorbell.service 

# install ssh server
sudo apt -y install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
