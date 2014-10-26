#!/usr/bin/env python2.7

from flask import Flask
from flask import request
from flask import render_template
import time
import threading
import traceback

import transitlive

app = Flask(__name__)
app.jinja_env.cache = {}

module_hash = {
  'transitlive':  transitlive.TransitLive(debug=False),
}

@app.route('/')
def root():

    return render_template('api-doc.html')
    

@app.route('/<module>/<function>', methods=['GET'])
@app.route('/<module>', methods=['GET'])
def api_request(module, function=None):


    response = None

    try:
        if (module in module_hash):
            response = module_hash[module].process(function, request.args)
            
    except Exception, e:
        print "\n", "-"*80, "\n"
        traceback.print_exc()
        print "\n", "-"*80, "\n"
        #raise e # TODO: Email/Log Error
        

    if response == None:
        return 'Unknown module', 404
    
    elif response.get('error') != None:
        return response['error'], 500

    elif response.get('response') == None:
	    return 'Bad request', 500

        
    return response.get('response')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)



