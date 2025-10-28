# remember to set env var FLASK_APP to cassiop3ia.py 
# nix: export FLASK_APP=cassiop3ia.py
# win: set FLASK_APP=cassiop3ia.py
# also included in .flaskenv

from app import app, db
from app.models import User, Post, Device, DeviceTypes, States, Environment

@app.shell_context_processor
def make_shell_context():
	return {'db':db, 'User':User, 'Post':Post, \
			'Device':Device, 'DeviceTypes':DeviceTypes, \
			'States':States, 'Environments':Environment}