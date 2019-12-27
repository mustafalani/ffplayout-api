#!flask/bin/python
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
# ffplayout api
# ------------------------------------------------------------------------------

import os, configparser, subprocess, json
from pathlib import Path
from shutil import copyfile
from flask import Flask, jsonify, request, abort, make_response

app = Flask(__name__)
app.run(host='0.0.0.0')

@app.route('/')
def index():
    return "ffplayout engine v1.0"

# ----------------------
# playlist configuration
# ----------------------

# Return Default playlist configuration
@app.route('/api/v1/config', methods=['GET'])
def getDefaultConfig():
        config = configparser.ConfigParser()
        config.read('../ffplayout.conf')
        log_path = config.get("LOGGING", "log_file")
        text = config.get("TEXT", "textfile")
        logo = config.get("PRE_COMPRESS", "logo")
        out = config.get("OUT","out_addr")
        return jsonify("default settings","log_path:",log_path,"output name:",out,"text file:",text,"logo:",logo)

# Return specific playlist configuration
@app.route('/api/v1/playlist/config', methods=['GET'])
def getPlaylistConfig():
        if not request.json or not 'playlistid' in request.json:
                abort(400)
        config = configparser.ConfigParser()
        playlist = request.json['playlistid']
        if not os.path.isfile('../playlists/config/' + playlist + '.conf'):
            return make_response(jsonify('Not Found'), 404)
        config.read('../playlists/config/' + playlist + '.conf')
        log_path = config.get("LOGGING", "log_file")
        text = config.get("TEXT", "textfile")
        logo = config.get("PRE_COMPRESS", "logo")
        logo_opacity = config.get("PRE_COMPRESS", "logo_opacity")
        out = config.get("OUT","out_addr")
        return jsonify("default settings","log_path:",log_path,"output name:",out,"text file:",text,"logo:",logo,"logo opacity",logo_opacity), 200

# Add new playlist configuration
@app.route('/api/v1/playlist/config', methods=['POST'])
def addPlaylistConfig():
        if not request.json or not 'playlistid' in request.json:
                abort(400)
        # check if all directories exist, if not create them
        playlist = request.json['playlistid']
        if not os.path.isdir('../playlists'):
                os.makedirs('../playlists')
        if not os.path.isdir('../playlists/config'):
                os.makedirs('../playlists/config')
        if not os.path.isdir('../playlists/text'):
                os.makedirs('../playlists/text')
        if not os.path.isdir('../playlists/logos'):
                os.makedirs('../playlists/logos')
        if not os.path.isdir('../playlists/logs'):
                os.makedirs('../playlists/logs')
        if not os.path.isdir('../playlists/json'):
                os.makedirs('../playlists/json')
        config = configparser.ConfigParser()
        config.read('../ffplayout.conf')
        # set variables
        config.set('LOGGING', 'log_file', '../playlists/logs/' + playlist + '.log')
        config.set('TEXT', 'textfile', '../playlists/text/' + playlist + '.txt')
        config.set('PRE_COMPRESS', 'logo', '../playlists/logos/' + playlist + '.png')
        config.set('OUT', 'out_addr', playlist)
        # save new config file
        with open('../playlists/config/' + playlist + '.conf', 'w') as configfile:
                config.write(configfile)
                configfile.close()
        Path('../playlists/text/' + playlist + '.txt').touch()
        Path('../playlists/logs/' + playlist + '.log').touch()
        Path('../playlists/json/' + playlist + '.json').touch()
        copyfile('../logo.png', '../playlists/logos/' + playlist + '.png')
        return jsonify('playlist configuration saved'), 201

# Update existing playlist configuration
@app.route('/api/v1/playlist/config', methods=['PUT'])
def updatePlaylistConfig():
        if not request.json or not 'playlistid' in request.json:
                abort(400)
        current_playlist = request.json['playlistid']
        new_playlist = request.json['newplaylistid']
        config = configparser.ConfigParser()
        config.read('../playlists/config/' + current_playlist + '.conf')
        # set variables
        config.set('LOGGING', 'log_file', '../playlists/logs/'+ new_playlist + '.log')
        config.set('TEXT', 'textfile', '../playlists/text/'+ new_playlist + '.txt')
        config.set('PRE_COMPRESS', 'logo', '../playlists/logos/' + new_playlist + '.png')
        config.set('OUT', 'out_addr', new_playlist)
        # update config file
        with open('../playlists/config/' + new_playlist + '.conf', 'w') as configfile:
                config.write(configfile)
                configfile.close()
        Path('../playlists/logs/' + new_playlist + '.log').touch()
        Path('../playlists/text/' + new_playlist + '.txt').touch()
        os.remove('../playlists/config/' + current_playlist + '.conf')
        os.rename(r'../playlists/text/' + current_playlist + '.txt',r'../playlists/text/' + new_playlist + '.txt')
        os.rename(r'../playlists/logs/' + current_playlist + '.log',r'../playlists/logs/' + new_playlist + '.log')
        os.rename(r'../playlists/logos/' + current_playlist + '.png',r'../playlists/logos/' + new_playlist + '.png')
        os.rename(r'../playlists/json/' + current_playlist + '.json',r'../playlists/json/' + new_playlist + '.json')
        return jsonify('playlist configuration updated'), 201

# Delete playlist and its configuration
@app.route('/api/v1/playlist/config', methods=['DELETE'])
def deletePlaylistConfig():
        if not request.json or not 'playlistid' in request.json:
            abort(400)
        playlist = request.json['playlistid']
        os.remove('../playlists/config/' + playlist + '.conf')
        os.remove('../playlists/text/' + playlist + '.txt')
        os.remove('../playlists/logs/' + playlist + '.log')
        os.remove('../playlists/logos/' + playlist + '.png')
        os.remove('../playlists/json/' + playlist + '.json')
        return jsonify('playlist removed'), 200

# ----------------
# playlist runtime
# ----------------

# read playlist items
@app.route('/api/v1/playlist/items', methods=['GET'])
def ReadPlaylistItems():
        if not request.json or not 'playlistid' in request.json:
                abort(400)
        playlist = request.json['playlistid']
        if not os.path.isfile('../playlists/config/' + playlist + '.conf'):
            return make_response(jsonify('Not Found'), 404)
        with open('../playlists/json/' + playlist + '.json') as json_file:
            playlist_items = json.load(json_file)
            return jsonify(playlist_items), 200

# update playlist items
@app.route('/api/v1/playlist/items', methods=['PUT'])
def UpdatePlaylistItems():
        if not request.json or not 'playlistid' in request.json:
                abort(400)
        playlist = request.json['playlistid']
        if not os.path.isfile('../playlists/config/' + playlist + '.conf'):
            return make_response(jsonify('Not Found'), 404)
        playlist_items = request.json['items']
        with open('../playlists/json/' + playlist + '.json','w') as json_out_file:
            json.dump(playlist_items, json_out_file)
            return jsonify('playlist updated!'), 200

# start playlist
@app.route('/api/v1/playlist/actions/start', methods=['PUT'])
def StartPlaylist():
        if not request.json or not 'playlistid' in request.json:
                abort(400)
        playlist = request.json['playlistid']
        if not os.path.isfile('../playlists/config/' + playlist + '.conf'):
            return make_response(jsonify('Not Found'), 404)
        playlist_config = ' -c ' + '../playlists/config/' + playlist + '.conf'
        playlist_json = ' -p ' + '../playlists/json/' + playlist + '.json'
        ffplayout = '../ffplayout.py'
        playlist_run_cmd = ffplayout + playlist_config + playlist_json
        subprocess.Popen(playlist_run_cmd, shell=True)
        return jsonify('playlist started'), 200

# stop playlist

if __name__ == '__main__':
    app.run(debug=False)
    app.run(host='0.0.0.0')
