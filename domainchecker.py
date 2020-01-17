#!/usr/bin/python3

import os
import argparse
import urllib, sys, re
from urllib.parse import urlparse
import urllib.request
import ssl
from multiprocessing.dummy import Pool as ThreadPool

def getFile(filename):
	try:
		with open(filename, "r") as f:
			return f.read().split("\n")
	except IOError as e:
		print("> "+e.strerror+" ["+e.filename+"]")
		parser.print_usage()


def parse_inline_domains(domainstr):
	return domainstr.split(",")
# help title
parser = argparse.ArgumentParser(
	prog='./domainchecker.py',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description='''\
	           _     _
	 ___ ___ _| |___| |_ _ _ ___ ___ ___
	|  _| . | . | -_| . | | |- _| -_|   |
	|___|___|___|___|___|_  |___|___|_|_|
	     https://dsda.ru|___|
 ''')
parser.add_argument('-l', dest="list", type=getFile, help='domain list file (each domain from new line)') 
parser.add_argument('-d', dest="domains", type=parse_inline_domains, help='domain list string (separates by ",")') 
parser.add_argument('-c', dest="codes", action='store_true', help='return [return code] domain name') 
parser.add_argument('-g', dest="good", action='store_true', help='return only good domains') 
parser.add_argument('-o', dest="output", type=argparse.FileType('w'), help='file to write result') 

if len(sys.argv)<=1:
    parser.print_usage(sys.stderr)
    sys.exit(1)
args = parser.parse_args()
print(args)

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
			ret = e.reason.errno
		elif hasattr(e, 'code'):
			ret = e.code
		else:
			ret = 'unknown error'
	except ConnectionResetError as e:
		ret = e
	ret_str = ''
	if args.codes==True:
		ret_str = str(ret) + "\t"
	ret_str = ret_str + url
	#TODO: check for return codes
	if (ret!=8 and ret!=500 and ret!=404):
		return ret_str
	else:
		if args.good!=True:
			return ret_str
	


# count the arguments
if (args.list == None):
	domains = args.domains
else:
	domains = args.list

domains = cleanlist(domains)


pool = ThreadPool(8)
results = pool.map(tryConnect, domains)


for i in results:
	if i!=None:
		if args.output:
			args.output.write(i+os.linesep)
		else:
			print(i)