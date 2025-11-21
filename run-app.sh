#!/bin/bash
echo "starting doorbell..."
source /home/iot/app/venv/bin/activate
python /home/iot/app/app.py
echo "Done"
