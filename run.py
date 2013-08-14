from flask import Flask, render_template
from flask import redirect
from flask import request, url_for
from pyzipcode import ZipCodeDatabase
import requests
import urllib2  
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

@app.template_filter('format_currency')
def format_currency(value):
	value = float(value)
	return "${:,.2f}".format(value)


# Get Amount of Super Pac Expenditures from OpenSecrets widget
def superpac_money():	
	url = 'http://www.opensecrets.org/widgets/outsidespending2012.js'
	url = urllib2.urlopen(url).read()
	url_split = url.split()
	length = len(url_split)
	amount = url_split[length-1]
	# removes quotes and semicolon
	amount = amount[1:-2]
	return amount
   
   
def get_state_from_zip(zip): 
	z = ZipCodeDatabase()
	zipcode = z[zip]
	return zipcode.state
	

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
		location = '91101'
	state = get_state_from_zip(location)

	# Congress API doesn't have as many entries
	url = 'http://congress.api.sunlightfoundation.com/legislators/locate?apikey='+str(keys.sunlight_key)+'&zip='+str(location)
	r = requests.get(url)
	r = r.json()
	congress = r['results']
	
	# openstates
	legislators = openstates.legislators(state=state)
				
	return render_template('choose_politician.html', legislators=legislators, congress=congress)
	

@app.route('/lobbying')
def lobbying():
	#top_10 = ie.entities.top_n_lobbyist_bundlers(limit=10)
	top_orgs = ie.entities.top_n_organizations(limit=15, cycle='-1')
	top_industries = ie.entities.top_n_industries(limit=15)
	return render_template('lobbying.html', top_orgs=top_orgs, top_industries=top_industries)


@app.route('/organizations')
def organizations():
	return render_template('organizations.html')
	
	
@app.route('/super_pacs')
def super_pacs():
	# TODO - get dynamic data for 2014
	return render_template('super_pacs.html')
	
	
@app.route('/take_action')
def take_action():
	return render_template('take_action.html')


if __name__ == '__main__':
	app.run(debug=True)

