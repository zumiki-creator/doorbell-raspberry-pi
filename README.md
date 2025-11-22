# doorbell-raspberry-pi
app on raspberry pi - Ubuntu

Install Ubuntu on Raspberry pi via Raspberry pi Imager (configure user: doorbell, host: iot, wifi and enable ssh)

# Run
curl -s https://raw.githubusercontent.com/zumiki-creator/doorbell-raspberry-pi/refs/heads/dev/bootstrap-ubuntu-pi.sh | bash

# See service logs live
journalctl -f -u doorbell
