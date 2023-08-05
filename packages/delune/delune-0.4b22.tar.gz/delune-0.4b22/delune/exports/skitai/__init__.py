# 2017. 3. 13 by Hans Roh (hansroh@gmail.com)

import skitai
import os
from atila import Atila
import delune

def __config__ (pref):
	skitai.register_g (delune.SIG_UPD)
	assert pref.config.resource_dir
	pref.config.resource_dir = os.path.abspath (pref.config.resource_dir)

def __app__ ():
	return Atila (__name__)

def __setup__ (app, mntopt):
	from . import services
	app.mount ("/", services)

def __mount__ (app, mntopt):
	@app.route ("/")
	def index (was):
		return '<h1>Delune</h1>'

	@app.route ("/status")
	@app.permission_required (["index", "replica"])
	def status (was):
		return was.status ()
