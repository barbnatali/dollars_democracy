from flask import Flask, render_template
import shelve
from math import ceil
from flask import redirect
from flask import request, url_for
from collections import OrderedDict
import keys

# open secrets 
# ----------------
# download and install https://code.google.com/p/python-crpapi/downloads/list
# docs - https://www.opensecrets.org/resources/create/api_doc.php
from crpapi import CRP, CRPApiError
CRP.apikey = keys.opensecrets_key

# sunlight 
# ----------------
# install pip install sunlight
# docs - http://python-sunlight.readthedocs.org/en/latest/#usage
import sunlight
from sunlight import openstates
from sunlight import congress
sunlight.config.API_KEY = keys.sunlight_key

# Influence Explore/Transparency Data
# ----------------
# python setup.py install - from python-transparencydata-master
from transparencydata import TransparencyData
td = TransparencyData(keys.sunlight_key)




app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


#http://127.0.0.1:5000/campaign/pelosi
@app.route('/campaign/')
@app.route('/campaign/<politician>')
def campaign(politician=None):
	if politician == None:
		return render_template('choose_location.html')
	else:
		politician_info = congress.legislators(lastname=politician)[0]
		return render_template('campaign.html', politician=politician_info)
	
	
@app.route('/choose_politician')
def location():
	if 'location' in request.args:
		location = request.args.get('location', '')
	else:
		location = 'ca'
	legislators = congress.legislators(state=location)
	return render_template('choose_politician.html', politicians=legislators)
	

if __name__ == '__main__':
	app.run(debug=True)

