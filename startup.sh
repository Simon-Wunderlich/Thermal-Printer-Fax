cd ~/Thermal-Printer-Fax
git pull
source ~/Thermal-Printer-Fax/.venv/bin/activate
pip install -r requirements.txt
screen -dmS fax bash -c "while true; do ~/Thermal-Printer-Fax/.venv/bin/python3 ~/Thermal-Printer-Fax/client.py; done"
