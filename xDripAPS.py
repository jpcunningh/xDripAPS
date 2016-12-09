import json
import sqlite3
from flask import Flask, request, abort
#from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
from json import dumps

# Maximum number of rows to retain - older rows will be deleted to minimise disk usage
MAX_ROWS = 336

# Connect to databse
#conn = sqlite3.connect('entries.db')

app = Flask(__name__)
api = Api(app)

class Entries(Resource):

    def get(self):

	# Connect to database
	conn = sqlite3.connect('entries.db')

	# Housekeeping first
	qry =  "DELETE FROM entries WHERE ROWID IN " 
	qry += "(SELECT ROWID FROM entries ORDER BY ROWID DESC LIMIT -1 OFFSET " + str(MAX_ROWS) + ")"
	conn.execute(qry)
	conn.commit()

	# Get count parameter
	count = request.args.get('count')

	# Perform query and return JSON data
        qry  = "SELECT ROWID as _id, device, date, dateString, sgv, direction, type, filtered, "
        qry += "unfiltered, rssi, noise "
        qry += "FROM entries ORDER BY date DESC"	
	if count != None:
		qry += " LIMIT " + count

        results_as_dict = []

        cursor = conn.execute(qry)
	
        for row in cursor:
            result_as_dict = {
		'_id' : row[0],
                'device' : row[1],
                'date' : row[2],
                'dateString' : row[3],
                'sgv' : row[4],
                'direction' : row[5],
                'type' : row[6],
                'filtered' : row[7],
                'unfiltered' : row[8],
                'rssi' : row[9],
                'noise' : row[10]}
            results_as_dict.append(result_as_dict)

        conn.close()
	return results_as_dict

    def post(self):

	# TODO: implement security
	#password = request.authorization.password
	#print 'PWD :: ' + password

        # Get JSON data
        json_data = request.get_json(force=True)

        # Get column values (assuming exactly one record as data source is xDrip)
        device                          = json_data[0]['device']
        date                            = json_data[0]['date']
        dateString                      = json_data[0]['dateString']
        sgv                             = json_data[0]['sgv']
        direction                       = json_data[0]['direction']
        type                            = json_data[0]['type']
        filtered                        = json_data[0]['filtered']
        unfiltered                      = json_data[0]['unfiltered']
        rssi                            = json_data[0]['rssi']
        noise                           = json_data[0]['noise']
        #xDrip_filtered_calculated_value = json_data[0]['xDrip_filtered_calculated_value']
        #sysTime                         = json_data[0]['sysTime']
    
        # Perform insert
        qry  = "INSERT INTO entries (device, date, dateString, sgv, direction, type, "
        qry += "filtered, unfiltered, rssi, noise) "
        qry += "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
 
        conn = sqlite3.connect('entries.db') 
	conn.execute(qry, (device, date, dateString, sgv, direction, type, filtered, unfiltered, rssi, noise))
	conn.commit()
	conn.close()
        return '', 200

api.add_resource(Entries, '/api/v1/entries')

if __name__ == '__main__':
     app.run(host='0.0.0.0')