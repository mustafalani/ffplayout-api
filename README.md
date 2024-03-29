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

configure nginx
----------------------------
sudo mkdir /var/www/ffplayout

sudo nano /var/www/ffplayout/http.conf


```
server {
    listen 8085;
    server_name localhost;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/opt/ffplayout/api/ffplayout_api.sock;
    }
}
server {
    listen                      8865 ssl;
    listen                      [::]:8865 ssl;

    ssl_certificate             /etc/letsencrypt/live/ott-pl-02.iohub.live/fullchain.pem;
    ssl_certificate_key         /etc/letsencrypt/live/ott-pl-02.iohub.live/privkey.pem;
    ssl_trusted_certificate     /etc/letsencrypt/live/ott-pl-02.iohub.live/chain.pem;

    location / {
      proxy_pass  http://127.0.0.1:8864;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";

         }
}
```

sudo nano /etc/nginx/nginx.conf
or copy from config folder

```
user                        www-data;
pid                         /run/nginx.pid;
worker_processes            8;

events {
    worker_connections      1024;
}

http {

    server {

        # HTTP can be used for accessing RTMP stats    
        listen      5050;

        # This URL provides RTMP statistics in XML
        location /stat {
            rtmp_stat all;

            # Use this stylesheet to view XML as web page
            # in browser
            rtmp_stat_stylesheet stat.xsl;
        }

        location /stat.xsl {
            # XML stylesheet to view RTMP stats.
            # Copy stat.xsl wherever you want
            # and put the full directory path here
            root /path/to/stat.xsl/;
        }

        location /hls {
            # Serve HLS fragments
            types {
                application/vnd.apple.mpegurl m3u8;
                video/mp2t ts;
            }
            root /tmp;
            add_header Cache-Control no-cache;
        }

        location /dash {
            # Serve DASH fragments
            root /tmp;
            add_header Cache-Control no-cache;
        }
    }

    include                 mime.types;
    default_type            application/octet-stream;

    sendfile                on;
    tcp_nopush              on;
    tcp_nodelay             on;
    server_tokens           off;
    keepalive_timeout       65;

    types_hash_max_size     2048;

    variables_hash_max_size     2048;
    variables_hash_bucket_size  64;

    gzip                    on;
    gzip_comp_level         2;
    gzip_min_length         1000;
    gzip_proxied            expired no-cache no-store private auth;
    gzip_types              text/plain application/javascript text/xml text/css image/svg+xml;


    # Logging Settings

    access_log              /var/log/nginx/access.log;
    error_log               /var/log/nginx/error.log;

    # Includes

    include                 ssl.conf;
    include                 cache.conf;
    include                 http.conf;
    include                 /var/www/*/http.conf;

} # END HTTP

#include                     rtmp.conf;

rtmp {

    server {

        listen 1935;

        chunk_size 4000;

        # rundown preview: one publisher, many subscribers
        application rundowns {

            # enable live streaming
            live on;


            # publish only from localhost
            allow publish 127.0.0.1;
            deny publish all;

            allow play all;
        }

        # TV mode: one publisher, many subscribers
        application mytv {

            # enable live streaming
            live on;

            # record first 1K of stream
            record all;
            record_path /tmp/av;
            record_max_size 1K;

            # append current timestamp to each flv
            record_unique on;

            # publish only from localhost
            allow publish 127.0.0.1;
            deny publish all;

            #allow play all;
        }

        # Transcoding (ffmpeg needed)
        application big {
            live on;

            # On every pusblished stream run this command (ffmpeg)
            # with substitutions: $app/${app}, $name/${name} for application & stream name.
            #
            # This ffmpeg call receives stream from this application &
            # reduces the resolution down to 32x32. The stream is the published to
            # 'small' application (see below) under the same name.
            #
            # ffmpeg can do anything with the stream like video/audio
            # transcoding, resizing, altering container/codec params etc
            #
            # Multiple exec lines can be specified.

            exec ffmpeg -re -i rtmp://localhost:1935/$app/$name -vcodec flv -acodec copy -s 32x32
                        -f flv rtmp://localhost:1935/small/${name};
        }

        application small {
            live on;
            # Video with reduced resolution comes here from ffmpeg
        }

        application webcam {
            live on;

            # Stream from local webcam
            exec_static ffmpeg -f video4linux2 -i /dev/video0 -c:v libx264 -an
                               -f flv rtmp://localhost:1935/webcam/mystream;
        }

        application mypush {
            live on;
            # Every stream published here
            # is automatically pushed to
            # these two machines
            #push rtmp1.example.com;
            #push rtmp2.example.com:1934;
        }

        application mypull {
            live on;

            # Pull all streams from remote machine
            # and play locally
            #pull rtmp://rtmp3.example.com pageUrl=www.example.com/index.html;
        }

        application mystaticpull {
            live on;

            # Static pull is started at nginx start
            #pull rtmp://rtmp4.example.com pageUrl=www.example.com/index.html name=mystream static;
        }

        # video on demand
        application vod {
            play /var/flvs;
        }

        application vod2 {
            play /var/mp4s;
        }

        # Many publishers, many subscribers
        # no checks, no recording
        application videochat {

            live on;

            # The following notifications receive all
            # the session variables as well as
            # particular call arguments in HTTP POST
            # request

            # Make HTTP request & use HTTP retcode
            # to decide whether to allow publishing
            # from this connection or not
            on_publish http://localhost:8080/publish;

            # Same with playing
            on_play http://localhost:8080/play;

            # Publish/play end (repeats on disconnect)
            on_done http://localhost:8080/done;

            # All above mentioned notifications receive
            # standard connect() arguments as well as
            # play/publish ones. If any arguments are sent
            # with GET-style syntax to play & publish
            # these are also included.
            # Example URL:
            #   rtmp://localhost/myapp/mystream?a=b&c=d

            # record 10 video keyframes (no audio) every 2 minutes
            record keyframes;
            record_path /tmp/vc;
            record_max_frames 10;
            record_interval 2m;

            # Async notify about an flv recorded
            on_record_done http://localhost:8080/record_done;

        }


        # HLS

        # For HLS to work please create a directory in tmpfs (/tmp/hls here)
        # for the fragments. The directory contents is served via HTTP (see
        # http{} section in config)
        #
        # Incoming stream must be in H264/AAC. For iPhones use baseline H264
        # profile (see ffmpeg example).
        # This example creates RTMP stream from movie ready for HLS:
        #
        # ffmpeg -loglevel verbose -re -i movie.avi  -vcodec libx264
        #    -vprofile baseline -acodec libmp3lame -ar 44100 -ac 1
        #    -f flv rtmp://localhost:1935/hls/movie
        #
        # If you need to transcode live stream use 'exec' feature.
        #
        application hls {
            live on;
            hls on;
            hls_path /tmp/hls;
        }

        # MPEG-DASH is similar to HLS

        application dash {
            live on;
            dash on;
            dash_path /tmp/dash;
        }
    }
}
```
