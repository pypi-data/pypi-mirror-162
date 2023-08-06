import json
import os
import pandas as pd
import requests
import sys
import urllib3
from requests.auth import HTTPBasicAuth

# disable warnings about self-signed ssl certificates for https requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# module variables
envs = {
    'qa-clone': {
        'host': 'https://author1euwest1-clone.qa.stmicro.adobecqms.net',
    },
    'qa': {
        'host': 'https://author1-65-eu.qa.stmicro.adobecqms.net',
    },
    'preprod': {
        'host': 'https://author1euwest1.preprod.stmicro.adobecqms.net',
    },
    'prod': {
        'host': 'https://author1euwest1.prod.stmicro.adobecqms.net',
    }
}

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]

# we can explicitly make assignments on it
this.env_name = None
this.host = None


def initialize_env(name):
    if (this.env_name is None):
        # also in local function scope. no scope specifier like global is needed
        this.env_name = name
    else:
        msg = "Database is already initialized to {0}."
        raise RuntimeError(msg.format(this.db_name))

    this.host = envs[name]['host']


cache_folder = f'cached/{this.env_name}'
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

login_url = f"{this.host}/libs/granite/core/content/login.html"


def convert_to_excel(csv_file, csv_delimiter):
    out_file = csv_file.replace(".csv", ".xlsx")
    read_file = pd.read_csv(csv_file, delimiter=csv_delimiter)
    read_file.to_excel(out_file, index=None, header=True)
    os.remove(csv_file)


def run_sql(aem_session, sql_str):
    sql_encoded = requests.utils.quote(sql_str)
    url = f'{this.host}/crx/de/query.jsp?_charset_=utf-8&type=JCR-SQL2&stmt={sql_encoded}&showResults=true'
    response = aem_session.get(url, verify=False)
    if response:
        return response.json().get('results')
    else:
        print(f"ruh_sql failed with{response}")

    return None


def get_netrc_credentials(host):
    res = urllib3.util.parse_url(host)
    if res:
        print(res.netloc)

        with open(f"{os.environ['HOME']}/.netrc") as f_in:
            lines = f_in.readlines()
            for line in lines:
                line = line.strip()
                columns = line.split(' ')
                if columns[1] == res.netloc and columns[2] == 'login' and columns[4] == 'password':
                    return columns[3], columns[5]
    return None, None


def get_https_session(s):
    # make sure we have an authenticated session
    username, password = get_netrc_credentials(this.host)
    if username is not None and password is not None:
        res = s.get(login_url, auth=HTTPBasicAuth(username, password), verify=False)
        if res.status_code == 200:
            return True
    return False


#
# take a fragment path, and extract the json object for that fragment from AEM
def write_json_to_cache(cached_file, result_json):
    with open(cached_file, 'w') as f_out:
        json.dump(result_json, f_out, indent=6)


def read_json_from_cache(cached_file):
    result_json = None
    with open(cached_file) as f_in:
        result_json = json.load(f_in)

    return result_json
