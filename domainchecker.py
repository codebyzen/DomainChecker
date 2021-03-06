#!/usr/bin/python3

from http.client import RemoteDisconnected
import argparse
import json
import multiprocessing
import os
import socket
import re
import ssl
import sys
import urllib
import urllib.request
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse


def progressbar(width, _min, _max, current, text=""):
	hashes = int(current / ((_max - _min) / width))
	fmt = "[%-" + str(width) + "s]"
	sys.stdout.write("\r")
	sys.stdout.write("\033[K")
	sys.stdout.write(fmt % ('#' * hashes))
	sys.stdout.write("\n")
	sys.stdout.write("\033[K")
	sys.stdout.write(text)
	sys.stdout.write("\033[1A")
	sys.stdout.write("\r")
	sys.stdout.flush()


def get_file(filename):
	try:
		with open(filename, "r") as f:
			return f.read().split("\n")
	except IOError as e:
		print("> " + e.strerror + " [" + e.filename + "]")
		parser.print_usage()


def parse_inline_domains(urls):
	return urls.split(",")


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
parser.add_argument('-l', dest="list", type=get_file, help='domain list file (each domain from new line)')
parser.add_argument('-d', dest="domains", type=parse_inline_domains, help='domain list string (separates by ",")')
parser.add_argument('-crt', dest="crt", action='store_true', help='get additional domains from crt.sh')
parser.add_argument('-crto', dest="crt_log_file", type=argparse.FileType('w'), help='save all domains from crt.sh')
parser.add_argument('-c', dest="codes", action='store_true', help='return [return code] domain name')
parser.add_argument('-g', dest="good", action='store_true', help='return only good domains')
parser.add_argument('-o', dest="log_file", type=argparse.FileType('w'), help='file to write result')

if len(sys.argv) <= 1:
	parser.print_usage(sys.stderr)
	sys.exit(1)
args = parser.parse_args()


def get_data_from_crt(_domain):
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	ctx.ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'

	domain_name = _domain.strip()
	matches = re.search("http[s]?:\/\/", domain_name)
	if matches is not None:
		purl = urlparse(domain_name)
		domain_name = purl.netloc

	data = urllib.parse.urlencode({'q': domain_name, 'output': 'json'})
	data = data.encode('ascii')

	ret = False
	try:
		print("Fetch domains from crt.sh...")
		with urllib.request.urlopen("https://crt.sh", data, context=ctx) as f:
			raw = f.read().decode('utf-8')
	except HTTPError as e:
		ret = "HTTPError >> " + e.reason
	except URLError as e:
		if isinstance(e.reason, socket.gaierror):
			ret = "GAIError >> " + str(e.reason.errno) + " " + e.reason.strerror
		else:
			ret = "URLError >> " + e.reason
	except socket.timeout:
		ret = "TIMEOUT"

	if ret:
		print("Sorry crt.sh return " + str(ret) + " try use proxy or try later...")
		exit(-1)

	json_data = json.loads(raw)
	urls_array = []
	for i in json_data:
		if i['name_value']:
			url = i['name_value'].split("\n")
			urls_array = urls_array + url

	clean_domains = []
	for i in urls_array:
		if not re.match(".*@.*|\*\.", i):
			clean_domains.append(i)

	# insert the list to the set
	list_set = set(clean_domains)
	# convert the set to the list
	clean_domains = (list(list_set))

	if args.crt_log_file:
		for clean_domains_item in clean_domains:
			args.crt_log_file.write('%s\n' % clean_domains_item)

	return clean_domains


def clean_list(domains_list):
	dp_list = []
	for _i in domains_list:
		url = _i.strip()
		if not url:
			continue
		matches = re.search("http[s]?:\/\/", url)
		if matches is None:
			dp_list.append("http://" + url)
			dp_list.append("https://" + url)
		else:
			purl = urlparse(url)
			dp_list.append(purl.scheme + "://" + purl.netloc)
	my_set = set(dp_list)
	dp_list = list(my_set)
	# ret_list = []
	# items_counter = 1
	# for item in dp_list:
	# 	ret_list.append([items_counter, item])
	# 	items_counter = items_counter + 1
	return dp_list


def try_connect(url, number):
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	domain_flag = False
	try:
		with urllib.request.urlopen(url, timeout=3, context=ctx) as f:
			ret = f.code
			domain_flag = True
	except UnicodeError as e:
		ret = "TooLong Domain >> " + url
	except HTTPError as e:
		ret = "HTTPError >> " + e.reason
	except RemoteDisconnected as e:
		ret = "RemoteDisconnected >> "
	except URLError as e:
		if isinstance(e.reason, socket.timeout):
			ret = "TIMEOUT >> "
		# elif isinstance(e.reason, socket.ConnectionRefusedError):
		# 	ret = "ConnectionRefusedError >> "
		elif isinstance(e.reason, socket.gaierror):
			ret = "GAIError >> " + str(e.reason.errno) + " " + e.reason.strerror
		else:
			ret = "URLError >> " + e.reason
	except socket.timeout:
		ret = "TIMEOUT >>"

	ret_str = url

	if args.codes and not args.good:
		ret_str = str(ret) + "\t" + ret_str

	if args.good:
		if domain_flag:
			return number, ret_str
		else:
			return number, False

	return number, ret_str


# count the arguments
if args.list is None:
	domains = args.domains
else:
	domains = args.list

if args.crt:
	all_domains = []
	for i in domains:
		all_domains = all_domains + get_data_from_crt(i)
	domains = all_domains

print("CPU count: " + str(multiprocessing.cpu_count()))
domains = clean_list(domains)
print("Total %d domain(s)" % len(domains))


def update(i):
	progressbar(40, 0, len(domains), i[0], text=str(i))
	# note: input comes from async `try_connect`
	res[i[0]] = i[1]  # put answer into correct index of result list


res = [None] * len(domains)
pool = multiprocessing.Pool(multiprocessing.cpu_count() + 1)
for domain, iter in zip(domains, range(len(domains))):
	pool.apply_async(try_connect, args=(domain, iter,), callback=update)
pool.close()
pool.join()

for i in res:
	if i is not None and i is not False:
		if args.log_file:
			args.log_file.write(i + os.linesep)
		else:
			print(i)