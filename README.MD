Domain Checker
==============

Simple multithreading Python script to check domain for working web server on it.

#### Install ####
- clone git repo
- python3 -m venv venv
- source ./venv/bin/activate

#### Usage ####
usage: `./domainchecker.py [-h] [-l LIST] [-d DOMAINS] [-crt] [-c] [-g] [-o OUTPUT]`
```
optional arguments:
  -h, --help  show this help message and exit
  -l LIST     domain list file (each domain from new line)
  -d DOMAINS  domain list string (separates by ",")
  -crt        get additional domains from crt.sh
  -c          return [return code] domain name
  -g          return only good domains
  -o OUTPUT   file to write result
```

To deactivate VirtualEnv type `deactivate`
