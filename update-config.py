from yaml import load, dump, Loader, Dumper
from requests import get
import sys, os, re

# DEFINE
RESOURCE_URL = "jsdelivr"  # github
CONFIG_FILE = "AdGuardHome.yaml"
DNS_RULE_FILE = "xfzka_upstream_dns_file"
CHINA_DNS_SERVERS = [
    "tls://dns.alidns.com",
    "tls://dns.pub",
    "https://dns.pub/dns-query",
    "https://dns.alidns.com/dns-query",
]
OTHER_DNS_SERVERS = [
    "tls://1.1.1.1",
    "tls://9.9.9.9",
    "https://dns.cloudflare.com/dns-query",
    "https://doh.opendns.com/dns-query",
    "https://dns10.quad9.net/dns-query",
]

# file check
if not os.path.exists(CONFIG_FILE):
    print(f"{CONFIG_FILE} not found")
    print("please move this script to AdGuardHome directory")
    exit(1)

# build resource url
url = "https://cdn.jsdelivr.net/gh/felixonmars/dnsmasq-china-list/accelerated-domains.china.conf"
url_apple = (
    "https://cdn.jsdelivr.net/gh/felixonmars/dnsmasq-china-list/apple.china.conf"
)
if RESOURCE_URL == "github":
    url = "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/accelerated-domains.china.conf"
    url_apple = "https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/master/apple.china.conf"

# download resource file
china_list = ""
china_list_apple = ""
print("Downloading")
try:
    china_list = get(url).text
except Exception as e:
    print(f"Error downloading resource file {url}. {e}")
    exit(1)
try:
    china_list_apple = get(url_apple).text
except Exception as e:
    print(f"Error downloading resource file {url}. {e}")
    exit(1)

# generate AdGuardHome rule file and save
all_list = china_list_apple + "\n" + china_list
all_host = "/".join(re.findall(r"server=/(.*?)/", all_list))
all_rule = [f"{DNS}\n" for DNS in OTHER_DNS_SERVERS]
for dns in CHINA_DNS_SERVERS:
    all_rule.append(f"[/{all_host}/]{dns}\n")
open(DNS_RULE_FILE, "w").writelines(all_rule)

# edit configuration file
config = load(open(CONFIG_FILE), Loader=Loader)
config["dns"]["upstream_dns_file"] = DNS_RULE_FILE
config["dns"]["upstream_dns"] = OTHER_DNS_SERVERS

# save configuration file
open(CONFIG_FILE, "w").writelines(dump(config, Dumper=Dumper))
print(f"AdGuardHome configuration updated")
print(f"Please reload or restart AdGuardHome")
