#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of ffplayout.
#
# ffplayout is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ffplayout is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ffplayout. If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------------

import configparser
import glob
import json
import logging
import math
import os
import random
import re
import signal
import smtplib
import socket
import ssl
import sys
import time
import subprocess
from argparse import ArgumentParser
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from logging.handlers import TimedRotatingFileHandler
from subprocess import PIPE, CalledProcessError, Popen, check_output
from threading import Thread
from types import SimpleNamespace
from urllib import request

try:
    if os.name != 'posix':
        import colorama
        colorama.init()

    from watchdog.events import PatternMatchingEventHandler
    from watchdog.observers import Observer
except ImportError:
    print('Some modules are not installed, ffplayout may or may not work')


# ------------------------------------------------------------------------------
# argument parsing
# ------------------------------------------------------------------------------

stdin_parser = ArgumentParser(
    description='python and ffmpeg based playout',
    epilog="don't use parameters if you want to use this settings from config")

stdin_parser.add_argument(
    '-p', '--playlist',
    help='playlist id'
)

stdin_args = stdin_parser.parse_args()


# ------------------------------------------------------------------------------
# clock
# ------------------------------------------------------------------------------

def get_time(time_format):
    """
    get different time formats:
        - full_sec > current time in seconds
        - stamp > current date time in seconds
        - else > current time in HH:MM:SS
    """
    t = datetime.today()

    if time_format == 'full_sec':
        return t.hour * 3600 + t.minute * 60 + t.second \
             + t.microsecond / 1000000
    elif time_format == 'stamp':
        return float(datetime.now().timestamp())
    else:
        return t.strftime('%H:%M:%S')


# ------------------------------------------------------------------------------
# default variables and values from config file
# ------------------------------------------------------------------------------
if stdin_args.playlist:
    preview_input = (stdin_args.playlist)
    preview_output = (stdin_args.playlist)
else:
    terminate_processes()
    sys.exit(1)

inout_type = 'libndi_newtek'
input_name = preview_input
output_settings = '-c:v libx264 -s hd480 -b:v 1000k -pix_fmt yuv420p -preset fast -deinterlace -c:a aac -b:a 96k -ar 48000 -ac 1'
output_type = 'flv'
output_name = preview_output

def load_config():
    """
    this function can reload most settings from configuration file,
    the change does not take effect immediately, but with the after next file,
    some settings cannot be changed - like resolution, aspect, or output
    """
    cfg = configparser.ConfigParser()

load_config()

def main():
    """
    preview using ffmpeg

    """
ffplayout_preview = 'ffmpeg -hide_banner -nostats -f ' + inout_type + ' -i ' + "'" + (socket.gethostname()).upper() + ' ('+ preview_input + ")' " + output_settings + ' -f ' + output_type + " 'rtmp://127.0.0.1:1935/rundowns/" + preview_output + "-preview'"
subprocess.Popen(ffplayout_preview, shell=True)
if __name__ == '__main__':
    main()
