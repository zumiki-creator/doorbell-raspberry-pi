#!/bin/bash
echo "starting doorbell..."
source /home/doorbell/app/venv/bin/activate
python /home/doorbell/app/app.py
echo "Done"
