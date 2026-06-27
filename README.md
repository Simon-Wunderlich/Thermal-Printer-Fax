# Setup
1. Clone repo
2. Create venv
3. Install requirements
4. Setup cron
```sh
# startup.sh
cd <project dir>
git pull
source <project dir>/venv/bin/activate
python3 <project dir>/client.py
```

```cronexp
@reboot sleep 60 && screen -dmS bt bash ./startup.sh  
```
5. Set `JustWorksRepairing` to `always` in `/etc/bluetooth/main.conf`