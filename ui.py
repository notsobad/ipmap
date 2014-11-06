#!/usr/bin/python
#coding=utf-8
import sys
import os
import datetime
import urlparse
import random
import hashlib
import re
import json
import tornado.ioloop
import tornado.web
import tornado
import tornado.httpclient
from tornado.options import define, options
from lib import save_ips_geo, load_ips_geo


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie('user')

class MainHandler(BaseHandler):
	def get(self):
		self.set_header('Cache-Control', 'max-age=3600')
		self.render('index.html')

class AddHandler(BaseHandler):
	@tornado.web.addslash
	def get(self):
		self.render("add.html", form={})

	def post(self):
		desc = self.get_argument('description', '')
		ips = self.get_argument('ipdata', '')
		ret = {'has_error':True}
		ret['description'] = desc
		ret['ipdata'] = ips
		clean_ips = []
		
		if not ips:
			ret.update(error_ipdata="ip data shuould not be empty!")
		else:
			for ip in ips.splitlines():
				ip = ip.strip()
				if not ip or not ipv4_re.match(ip):
					continue
				clean_ips.append(ip)

		if clean_ips:
			# OK
			key = save_ips_geo(clean_ips, desc)
			return self.redirect(self.reverse_url("map", key))

		ret.update(error_ipdata="Wrong ip data.")
		self.render('add.html', form=ret)

class MapHandler(BaseHandler):
	@tornado.web.addslash
	def get(self, key):
		json_data = load_ips_geo(key)
		self.render("map.html", json_data=json_data)


define("ip", default="0.0.0.0", help="ip to bind")
define("port", default=9527, help="port to listen")
define("debug", default=False, help="enable debug?")
tornado.options.parse_command_line()
settings = {
	'template_path' : os.path.join(os.path.dirname(__file__), 'templates'),
	'debug' : options.debug,
	'login_url' : '/login/',
	'cookie_secret' : 'dt4zRkC72CFnze8z3Jvmq7eif3XsWiyG',
}

app = tornado.web.Application([
	tornado.web.url(r'/', MainHandler, name="main"),
	tornado.web.url(r'/add/', AddHandler, name="add"),
	tornado.web.url(r'/map/([^/]+)/', MapHandler, name="map"),
	(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
], **settings)

if __name__ == '__main__':
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
