from BeautifulSoup import BeautifulSoup
from jinja2 import Template
from datetime import datetime
import urllib2
import urllib
import threading

class ConsolidatedSearch:
	
	# TODO: stop exposing api keys in git repo
	API = {
		'YP': "http://api.sandbox.yellowapi.com/FindBusiness/?pg=1&what=%s&lang=en&where=%s&pgLen=20&fmt=XML&UID=%s&apikey=fdgx2axqahubf4xsd2fxr58k"
	}
	
	render_template_file = "templates/template_search.xml"
	
	class Result:
		def __init__(self, name, address, latitude, longitude):
			self.name = name
			self.address = address
			self.lat = latitude
			self.long = longitude
	
	
	def __init__(self, debug=False):
		
		print "Initializing Search module"
	
	
	def process(self, function, params):
		
		output = {'error': None, 'response': None}
		
		yp_listings = self.yp_fetch(params['what'], params['where'], params['uid'])
		output['response'] = self.render(yp_listings)

		return output
            
	
	def render(self, listings):
		template = Template(open(self.render_template_file).read())
		return template.render(o=listings)
		
	def yp_fetch(self, what, where, uid):
		data = urllib2.urlopen(ConsolidatedSearch.API['YP'] % (what, where, uid)).read()

		listings_soup = BeautifulSoup(data).findAll('listing');
		
		listings = []
		
		if listings_soup == None:
			return listings
		
		try:
			for l in listings_soup:
				result = ConsolidatedSearch.Result(
					l.find('name').text,
					"%s, %s, %s" % (l.address.street.text, l.address.city.text, l.address.prov.text),
					l.geocode.latitude.text,
					l.geocode.longitude.text
				)
				listings.append(result)
		
		# TODO: not this
		except Exception, e:
			print e
		
		return listings
		
if __name__ == "__main__":
	cs = ConsolidatedSearch()
	soup = cs.perform_search('parks', 'regina')
	
	print soup.prettify()
	
	
