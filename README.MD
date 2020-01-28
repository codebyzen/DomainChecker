Domain Checker
==============

A multi-threaded python3 script to determine site availability.
We can check http/https.

#### Install ####
- `git clone https://github.com/codebyzen/DomainChecker`
- `chmod +x ./domainchecker.py`

#### Usage ####
usage: `./domainchecker.py [-h] [-l LIST] [-d DOMAINS] [-crt] [-crto CRT_LOG_FILE] [-c] [-g] [-o LOG_FILE]`
```
optional arguments:
  -h, --help          show this help message and exit
  -l LIST             domain list file (each domain from new line)
  -d DOMAINS          domain list string (separates by ",")
  -crt                get additional domains from crt.sh
  -crto CRT_LOG_FILE  save all domains from crt.sh
  -c                  return [return code] domain name
  -g                  return only good domains
  -o LOG_FILE         file to write result
```

### TODO ###
Check ports different from 80 and 443