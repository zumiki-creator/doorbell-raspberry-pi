#!/bin/bash
echo "raspberry PI GPIO and Arduino-iot-cloud"

echo "Updating system and installing dependencies... ============================================================="
sudo apt -y update
sudo apt -y upgrade
sudo apt -y install python3-full
sudo apt -y install liblgpio-dev
sudo apt -y install swig
sudo apt -y install git

#git repo clone
echo "Cloning repository... ============================================================"
git config --global user.name "app"
git config --global user.email "app@localhost.com"
git clone https://github.com/zumiki-creator/doorbell-raspberry-pi.git ~/app

#ubuntu only
echo "Installing Ubuntu specific dependencies... ============================================================"
sudo apt-get -y install crossbuild-essential-arm64
sudo apt-get -y install python3-dev

#setup python environment
echo "Setting up Python environment... ============================================================" 
cd ~/app
python3 -m venv venv
source venv/bin/activate

# upgrade pip and install required python packages
echo "Installing Python packages... ============================================================"

pip install --upgrade pip setuptools wheel

pip install gpiozero
pip install RPi-GPIO
pip install RPi-lgpio
pip install arduino-iot-cloud

# create app service   
echo "Setting up application service... ============================================================"
chmod +x ~/app/run-app.sh
sudo cp ~/app/bootstrap/doorbell.service /etc/systemd/system/doorbell.service
sudo systemctl enable doorbell.service
sudo systemctl start doorbell.service 

# install ssh server
# sudo apt -y install openssh-server
# sudo systemctl enable ssh
# sudo systemctl start ssh
