from flask import Flask, render_template, request, jsonify, redirect, url_for
from json2html import *
import json
from database import session
from model import Websites


app = Flask(__name__)


@app.route('/')
def index():
    # user = {'username': 'Miguel'}
    all_servers = session.query(Websites.server).group_by(Websites.server).all()
    to_be_dumped = {}
    for server in all_servers:
        server_count = len(session.query(Websites).filter(Websites.server == server[0]).all())
        server_name = server[0]
        to_be_dumped.update({server_name: server_count})
    server_json = json.dumps(to_be_dumped, sort_keys=True, indent=4)
    # return server_json
    infoFromJson = json.loads(server_json)
    data = json2html.convert(json=infoFromJson)
    return data


