import json, datetime
from flask import Flask
from flask import request
from databaseQuerys import databaseQuerys

db = databaseQuerys()
app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def main():
	return app.send_static_file('index.html')

#api's
@app.route('/api/upcheck')
def apiUpcheck():
	return str(db.dbCheck())

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5007)