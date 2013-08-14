from flask import Flask, render_template
import shelve
from math import ceil
from flask import redirect
from flask import request, url_for
from collections import OrderedDict
import xmltodict
import requests
import keys

# opensecrets 
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

# Transparency Data
# ----------------
# python setup.py install - from python-transparencydata-master
from transparencydata import TransparencyData
td = TransparencyData(keys.sunlight_key)

# Influence Explorer
# ----------------
from influenceexplorer import InfluenceExplorer
ie = InfluenceExplorer(keys.sunlight_key)


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
		# congress
		# politician_info = congress.legislators(lastname=politician)[0]
		#td.contributions(recipient_ft=politician)
		
		# openstates
		# politician_info = sunlight.openstates.legislators(last_name=politician)
		
		# influence explorer
		politician_info = ie.entities.search(politician)[0]
		id = politician_info['id']
		top_industries = ie.pol.industries(id, limit=10)
		return render_template('campaign.html', politician=politician_info, top_industries=top_industries)
	
	
@app.route('/choose_politician')
def choose_politician():
	if 'location' in request.args:
		location = request.args.get('location', '')
	else:
		location = 'ca'
 	if location.isdigit():
 		# Congress API doesn't have as many entries
 		url = 'http://congress.api.sunlightfoundation.com/legislators/locate?apikey='+str(keys.sunlight_key)+'&zip='+str(location)
 		r = requests.get(url)
 		r = r.json()
 		legislators = r['results']
	else:
		# openstates
		legislators = openstates.legislators(state=location)
	return render_template('choose_politician.html', politicians=legislators)
	

@app.route('/lobbying')
def lobbying():
	top_10 = ie.entities.top_n_lobbyist_bundlers(limit=10)
	return render_template('lobbying.html', top_10=top_10)


@app.route('/organizations_industries')
def organizations():
	top_orgs = ie.entities.top_n_organizations(limit=15)
	top_industries = ie.entities.top_n_industries(limit=15)
	return render_template('organizations_industries.html', top_orgs=top_orgs, top_industries=top_industries)


if __name__ == '__main__':
	app.run(debug=True)

