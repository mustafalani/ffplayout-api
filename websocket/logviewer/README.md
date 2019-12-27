# logviewer

```
$ python -m venv .virtualenv
$ ./ve pip install -r requirements.txt
$ ./ve python server.py -h
usage: server.py [-h] [--host HOST] [--port PORT] --prefix PREFIX

optional arguments:
  -h, --help       show this help message and exit
  --host HOST
  --port PORT
  --prefix PREFIX  Allowed directories
$ ./ve python server.py --host 127.0.0.1 --port 8765 --prefix /tmp/dir1/ --prefix /tmp/dir2/
```
