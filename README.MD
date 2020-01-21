Domain Checker
==============

A multi-threaded python script to determine site availability.

#### Install ####
- git clone [https://github.com/codebyzen/DomainChecker](https://github.com/codebyzen/DomainChecker)
- chmod +x ./domainchecker.py

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
