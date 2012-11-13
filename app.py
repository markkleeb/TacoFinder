# -*- coding: utf-8 -*-
import os, datetime
import re
from unidecode import unidecode

from flask import Flask, request, render_template, redirect, abort, jsonify
import requests

# Twilio
from twilio.rest import TwilioRestClient

# create Flask app
app = Flask(__name__)   # create our flask app


# --------- Routes ----------

@app.route("/", methods=['GET','POST'])
def main():
	if request.method == "GET":
		return render_template('fsq.html')

	elif request.method == "POST":

		user_latlng = request.form.get('user_latlng')

		# Foursquare API endpoint for Venues
		fsq_url = "https://api.foursquare.com/v2/venues/search"

		# prepare the foursquare query parameters for the Venues Search request
		# simple example includes lat,long search
		# we pass in our client id and secret along with 'v', a version date of API.
		fsq_query = {
			'll' : user_latlng,
			'query': tacos,
			'client_id' : os.environ.get('FOURSQUARE_CLIENT_ID'), # info from foursquare developer setting, placed inside .env
			'client_secret' : os.environ.get('FOURSQUARE_CLIENT_SECRET'),
			'v' : '20121113' # YYYYMMDD
		}

		# using Requests library, make a GET request to the fsq_url
		# pass in the fsq_query dictionary as 'params', this will build the full URL with encoding variables.
		results = requests.get(fsq_url, params=fsq_query)

		# log out the url that was request
		app.logger.info("Requested url : %s" % results.url)

		# if we receive a 200 HTTP status code, great! 
		if results.status_code == 200:

			# get the response, venue array 
			fsq_response = results.json # .json returns a python dictonary to us.
			nearby_venues = fsq_response['response']['venues']

			app.logger.info('nearby venues')
			app.logger.info(nearby_venues)

			# Return raw json for demonstration purposes. 
			# You would likely use this data in your templates or database in a real app
			return jsonify(results.json['response'])
	
		else:

			# Foursquare API request failed somehow
			return "uhoh, something went wrong %s" % results.json


@app.route('/twilio', methods=['GET','POST'])
def twilio():
	if request.method == "GET":
		return render_template('twilio.html')

	elif request.method == "POST":

		telephone = request.form.get('telephone')
		sms_text = request.form.get('sms_text')

		# prepare telephone number. regex, only numbers
		telephone_num = re.sub("\D", "", telephone)
		if len(telephone_num) != 11:
			return "your target phone number must be 11 digits. go back and try again."
		else:
			to_number = "+1" + str(telephone_num) #US country only now


		# trim message to 120
		if len(sms_text) > 120:
			sms_text = sms_text[0:119]

		account = os.environ.get('TWILIO_ACCOUNT_SID')
		token = os.environ.get('TWILIO_AUTH_TOKEN')

		client = TwilioRestClient(account, token)

		from_telephone = os.environ.get('TWILIO_PHONE_NUMBER') # format +19171234567

		message = client.sms.messages.create(to=to_number, from_=from_telephone,
	                                     body="DWD DEMO: " + sms_text)

		return "message '%s' sent" % sms_text


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404



# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)



	