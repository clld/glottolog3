import os
from paste.deploy import loadapp
from waitress import serve

if __name__ == "__main__":
	port_obj = os.environ.get('PORT')
	app = loadapp('config:development.ini', relative_to='.')
	if port_obj is not None:
		serve(app, port=int(port_obj))
	else:
		serve(app)
