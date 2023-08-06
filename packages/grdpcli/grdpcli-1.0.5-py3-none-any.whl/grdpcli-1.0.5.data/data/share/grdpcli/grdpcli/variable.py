import os
import signal
import subprocess
import sys

from os.path import expanduser
from time import sleep

hostName = '127.0.0.1'
serverPort = 65510
GITLAB_URL = 'https://gitlab.onix.ua'
AUTH_ADDRESS = 'https://grdp-cli-auth.staging.onix.ua'
GRDPCLI_HOME_DIR = os.path.join(expanduser("~"), '.kube')
GRDPCLI_PROJECT_JSON = 'projects.json'
GRDPCLI_CONFIG_JSON = 'config.json'
KUBECTL_CONFIG = os.path.join(GRDPCLI_HOME_DIR, 'config')

if not os.path.exists(GRDPCLI_HOME_DIR):
    os.mkdir(GRDPCLI_HOME_DIR)

kubectl_clusters_template = """apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {k8s_authority_data}
    server: {k8s_api_address}
  name: grdp-cluster
contexts:
- context:
    cluster: grdp-cluster
    namespace: {namespace_name}
    user: {namespace_name}
  name: {namespace_name}
current-context: {namespace_name}
kind: Config
preferences: {{}}
users:
- name: {namespace_name}
  user:
    token: {access_token}
"""
