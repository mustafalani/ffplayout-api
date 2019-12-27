ffplayout api
=============

This app provide RESTful API for ffplayout https://github.com/ffplayout/ffplayout-engine

Key features
------------

 -
 -
 -
 -
 -
 -
 -

Folder Structure
----------------
The following folders must be placed in the root directory of ffplayout
```
 - api
    - __pycache__
    - flask
 - playlists
    - config
    - json
    - logos
    - logs
    - text
 - websocket
```

Installation
------------
```
sudo apt-get install python-dev

sudo apt-get install python-pip

sudo pip install uwsgi
```

Intsall logviewer websocket
---------------------------
```
cd /opt/ffplayout/websocket/logviewer
```

for python
```
sudo pip install -r requirements.txt
```
for python3
```
sudo pip3 install -r requirements.txt
```

for python
```
./ve python server.py --host 127.0.0.1 --port 8864 --prefix /opt/ffplayout/playlists/logs/
```

for python3
```
./ve python3 server.py --host 127.0.0.1 --port 8864 --prefix /opt/ffplayout/playlists/logs/
```

add ffplayout-api to system services
------------------------------------
```
nano /etc/systemd/system/ffplayout-api.service
```
in the service file write the following:

```
[Unit]
Description=uWSGI instance to serve ffplayout api
After=network.target

[Service]
WorkingDirectory=/opt/ffplayout/api/
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/ffplayout/api/flask/bin"
ExecStart=/opt/ffplayout/api/flask/bin/uwsgi --ini ffplayout_api.ini
User=root
Group=www-data

[Install]
WantedBy=multi-user.target
```
check the service
----------------------------

```
sudo systemctl daemon-reload

sudo systemctl enable ffplayout-api.service

sudo systemctl start ffplayout-api.service

sudo systemctl status ffplayout-api.service
```

add logviewer websocket to system services
------------------------------------------
```
nano /etc/systemd/system/ffplayout-api-websocket.service
```
in the service file write the following:

```
[Unit]
Description=websocket instance to serve ffplayout api
After=network.target

[Service]
WorkingDirectory=/opt/ffplayout/websocket/logviewer/
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/ffplayout/api/flask/bin"
ExecStart=/opt/ffplayout/websocket/logviewer/ve python3 server.py --host 127.0.0.1 --port 8864 --prefix /opt/ffplayout/playlists/logs/
User=root
Group=www-data

[Install]
WantedBy=multi-user.target
```

check the service
----------------------------

```
sudo systemctl daemon-reload

sudo systemctl enable ffplayout-api-websocket.service

sudo systemctl start ffplayout-api-websocket.service

sudo systemctl status ffplayout-api-websocket.service
```
