from yaml import load, dump, Loader, Dumper
from requests import get
import sys, os, re

# DEFINE
RESOURCE_URL = "jsdelivr"  # github
CONFIG_FILE = "AdGuardHome.yaml"
DNS_RULE_FILE = "xfzka_upstream_dns_file"
ENABLE_GOOGLE = True
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


def download_file(author: str, respository: str, branch: str, file_name: str) -> str:
    """Download file from jsdelivr or github"""
    result = ""
    try:
        print(f"Downloading {file_name} from github")
        url = f"https://raw.githubusercontent.com/{author}/{respository}/{branch}/{file_name}"
        result = get(url).text
    except Exception as e:
        print(f"Error downloading resource file {url}. {e}")
        print(f"Downloading {file_name} from jsdelivr")
        try:
            result = get(url).text
            url = f"https://cdn.jsdelivr.net/gh/{author}/{respository}@{branch}/{file_name}"
        except Exception as e:
            print(f"Error downloading resource file {url}. {e}")
            print("All fail, please check your internet connection")
            exit(1)
    return result


# download resource file
china_list = download_file(
    "felixonmars", "dnsmasq-china-list", "master", "accelerated-domains.china.conf"
)
china_list_apple = download_file(
    "felixonmars", "dnsmasq-china-list", "master", "apple.china.conf"
)
china_list_google = download_file(
    "felixonmars", "dnsmasq-china-list", "master", "google.china.conf"
)
xfzka_list = download_file(
    "xfzka", "AdGuard-ChinaList-Rule", "main", "whitelist"
).splitlines()

# generate AdGuardHome rule file and save
all_list = china_list_apple + "\n" + china_list
if ENABLE_GOOGLE:
    all_list += "\n" + china_list_google
all_host = "/".join(list(set(re.findall(r"server=/(.*?)/", all_list) + xfzka_list)))
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
