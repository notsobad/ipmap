#coding: utf-8
import sys
import os
from os import path as osp
import geoip2.database
import traceback
import datetime
import json
import hashlib
BASEDIR = osp.dirname(osp.realpath(__file__))
sys.path.append(BASEDIR)

BASEDIR = '/Users/wangxh/myapp/ipmap'
reader = geoip2.database.Reader(osp.join(BASEDIR, 'GeoLite2-City.mmdb'))

def get_geo_info(ip):
	try:
		response = reader.city(ip)
	except geoip2.errors.AddressNotFoundError:
		return ret

	return [response.location.latitude, response.location.longitude]

def save_ips_geo(ips, description):
	'''
	Save to json file.
	
	data/0/cc/175b9c0f1b6a831c399e269772661.json

	'''

	m = hashlib.md5()
	m.update(''.join(sorted(ips)))
	key = m.hexdigest()

	ret = {'description': description, 'ips':{}}
	for ip in ips:
		geo = get_geo_info(ip)
		if not geo:
			continue
		ret['ips'][ip] = geo

	path = os.path.join(BASEDIR, 'data', key[0], key[1:3])
	if not os.path.isdir(path):
		os.makedirs(path)

	json.dump(ret, open("%s/%s" % (path, key), 'w+'), indent=None)
	return key

def load_ips_geo(key):
	path = os.path.join(BASEDIR, 'data', key[0], key[1:3])
	json_file = "%s/%s" % (path, key)
	if os.path.isfile(json_file):
		return open(json_file).read()
	return ''

if __name__ == '__main__':
	save_ips_geo(['8.8.8.8', '114.114.114.114'], "test")
