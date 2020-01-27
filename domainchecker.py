#!/usr/bin/python3

from pprint import pprint
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
from multiprocessing.dummy import Pool as ThreadPool
from urllib.parse import urlparse


def get_file(filename):
    try:
        with open(filename, "r") as f:
            return f.read().split("\n")
    except IOError as e:
        print("> " + e.strerror + " [" + e.filename + "]")
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
parser.add_argument('-l', dest="list", type=get_file, help='domain list file (each domain from new line)')
parser.add_argument('-d', dest="domains", type=parse_inline_domains, help='domain list string (separates by ",")')
parser.add_argument('-crt', dest="crt", action='store_true', help='get additional domains from crt.sh')
parser.add_argument('-c', dest="codes", action='store_true', help='return [return code] domain name')
parser.add_argument('-g', dest="good", action='store_true', help='return only good domains')
parser.add_argument('-o', dest="output", type=argparse.FileType('w'), help='file to write result')

if len(sys.argv) <= 1:
    parser.print_usage(sys.stderr)
    sys.exit(1)
args = parser.parse_args()

print(args)


def get_data_from_crt(domain):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'

    domain_name = domain.strip()
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

    if ret:
        print("Sorry crt.sh return %ds@ try use proxy or try later..." % ret)
        exit(-1)

    output = json.loads(raw)
    urls_array = []
    for i in output:
        if i['name_value']:
            url = i['name_value'].split("\n")
            # url = i['name_value']
            urls_array = urls_array + url

    clean_domains = []
    for i in urls_array:
        if not re.match(".*@.*|\*\.", i):
            clean_domains.append(i)

    # insert the list to the set
    list_set = set(clean_domains)
    # convert the set to the list
    clean_domains = (list(list_set))

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
    ret_list = []
    items_counter = 1
    for item in dp_list:
        ret_list.append([items_counter, item])
        items_counter = items_counter + 1
    return ret_list


def try_connect(item_arr):
    number = item_arr[0]
    url: str = item_arr[1]
    sys.stdout.write("\033[K")
    print("\r>> Now we get {}".format(number), end='')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    domain_flag = False
    try:
        with urllib.request.urlopen(url, timeout=3, context=ctx) as f:
            ret = f.code
            domain_flag = True
    except urllib.error.HTTPError as e:
        ret = "HTTPError >> " + e.reason
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.gaierror):
            ret = "GAIError >> " + e.reason.strerror
        else:
            ret = "URLError >> " + e.reason

    ret_str = url

    if args.codes and not args.good:
        ret_str = str(ret) + "\t" + ret_str

    if args.good:
        if domain_flag:
            return ret_str
        else:
            return False

    return ret_str


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

domains = clean_list(domains)
print("Total %d domain(s)" % len(domains))

pool = ThreadPool(multiprocessing.cpu_count())
results = pool.map(try_connect, domains)

print("")
for i in results:
    if i is not None and i is not False:
        if args.output:
            args.output.write(i + os.linesep)
        else:
            print(i)
