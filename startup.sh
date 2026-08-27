cd ~/Thermal-Printer-Fax
source ~/Thermal-Printer-Fax/.venv/bin/activate
screen -dmS fax bash -c "while true; do ~/Thermal-Printer-Fax/.venv/bin/python3 ~/Thermal-Printer-Fax/client.py; done"
