#!/usr/bin/python3

import urllib, sys, re
from urllib.parse import urlparse
import urllib.request
import ssl
from multiprocessing.dummy import Pool as ThreadPool


def getFile(filename):
	f = open(filename, "r")
	domains = f.read().split("\n")
	return domains


def cleanlist(dList):
	dpList = []
	for i in dList:
		url = i.strip()
		if not url:
			continue
		matches = re.search("http[s]?:\/\/", url)
		if matches==None:
			dpList.append("http://"+url)
			dpList.append("https://"+url)
		else:
			purl = urlparse(url)
			dpList.append(purl.scheme+"://"+purl.netloc)
	my_set = set(dpList)
	dpList = list(my_set)
	return dpList
		
def tryConnect(url):
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	try:
		with urllib.request.urlopen(url, context=ctx) as f:
			ret = f.code
	except urllib.error.HTTPError as e:
		ret = e.code
	except urllib.error.URLError as e:
		if hasattr(e, 'reason'):
			ret = e.reason
		elif hasattr(e, 'code'):
			ret = e.code
		else:
			ret = 'unknown error'
	except ConnectionResetError as e:
		ret = e
	return str(ret) + "\t" + url


# count the arguments
arguments = len(sys.argv)
if (arguments>=3 and sys.argv[1]=='-f'):
	domains = getFile(sys.argv[2])
else:
	domains = sys.argv[1:arguments]

domains = cleanlist(domains)


pool = ThreadPool(8)
results = pool.map(tryConnect, domains)

for i in results:
	print(i)