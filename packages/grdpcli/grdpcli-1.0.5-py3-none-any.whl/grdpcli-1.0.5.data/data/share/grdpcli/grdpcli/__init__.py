import webbrowser
import requests
import logging
import json

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from grdpcli.variable import *
from grdpcli.logger import logger


def checkKubectl():
    """
        Checking kubectl command.
    """
    APP_NAME = 'kubectl'
    try:
        devnull = open(os.devnull)
        subprocess.Popen([APP_NAME], stdout=devnull, stderr=devnull).communicate()
    except:
        return False
    return True

def getProjectsJson():
    return json.load(open(os.path.join(GRDPCLI_HOME_DIR, GRDPCLI_PROJECT_JSON)))

def getGRCPcliConfig():
    return json.load(open(os.path.join(GRDPCLI_HOME_DIR, GRDPCLI_CONFIG_JSON)))

def getProjectsId():
    return json.load(open(os.path.join(GRDPCLI_HOME_DIR, GRDPCLI_CONFIG_JSON)))['active_project']

def getProjectName(id):
    id = None if id == 'None' else id
    if not id:
        return None

    projects = getProjectsJson()
    for key in projects[id].keys():
        name = list(projects[id].keys())[0]
        if key == 'status':
            name = list(projects[id].keys())[1]
        break
    return name

def getNamespaceName(id):
    projects = getProjectsJson()
    id = str(id)
    for key in projects[id].keys():
        if key == 'status':
            key = list(projects[id].keys())[1]
        return projects[id][key]['K8S_NAMESPACE']

def checkToken(access_token):
    r = requests.get("{}/api/v4/projects".format(GITLAB_URL), headers={"Authorization": "Bearer {}".format(access_token)}).status_code
    if int(r) == 200:
        return True
    return False

def getAllProjects(access_token):
    PROJECT_LIST = []
    page = 0
    while True:
        page = page + 1
        projects_dict = requests.get("{}/api/v4/projects?page={}".format(GITLAB_URL, page), headers={"Authorization": "Bearer {}".format(access_token)}).json()
        if not len(projects_dict) > 0:
            break
        PROJECT_LIST = PROJECT_LIST + projects_dict
    return PROJECT_LIST

def getProjectVariables(access_token, project_id, project_name):
    REQUIRED_VARIABLES = ['K8S_NAMESPACE','K8S_HOSTNAME','K8S_ACCESS_TOKEN']
    VARIABLES_DICT, variables_json = {}, {}
    page = 0
    while True:
        page = page + 1
        variables_data = requests.get("{}/api/v4/projects/{}/variables?page={}".format(GITLAB_URL, project_id, page), headers={"Authorization": "Bearer {}".format(access_token)}).json()
        if 'message' in variables_data:
            logger.warn(f"Skipping project {project_name} due reason: {variables_data['message']}")
            return { project_name: {}, "status": "False" }
        if not len(variables_data):
            break
        for item in variables_data:
            variables_json[item['key']] = item['value']

    if 'message' in variables_json:
        return {project_name: {}, "status": "False"}

    for req_var in REQUIRED_VARIABLES:
        for gl_var in variables_json:
            if gl_var == req_var:
                variable_template = {
                    gl_var: variables_json[gl_var]
                  }
                VARIABLES_DICT.update(variable_template)
    required_variables = {
        project_name : VARIABLES_DICT,
            "status": "True"
        }
    f_var = [i for i in required_variables[project_name]]
    for p in REQUIRED_VARIABLES:
        if p not in f_var:
            logger.warn(f"Skipping project: {project_name} due reason: Didn't found required variables {','.join(REQUIRED_VARIABLES)}.")
            return {project_name: {}, "status": "False"}
    return required_variables

def cliConfigCreate(access_token):
    logger.info("Getting and generation projects configuration file, please wait ...")
    PROJECTS_LIST = getAllProjects(access_token)
    config_template = {}
    id = 0
    for project in PROJECTS_LIST:
        project_data = getProjectVariables(access_token, project['id'], project['path'])
        if json.loads(project_data['status'].lower()) == False:
            continue
        id = id + 1
        template = {
            id: project_data
        }
        config_template.update(template)

        with open(os.path.join(GRDPCLI_HOME_DIR, GRDPCLI_PROJECT_JSON), 'w') as f:
            json.dump(config_template, f, indent=4, sort_keys=True)

def createGRCPcliConfig(data):
    WASTE_KEYS = ['status', 'access_token']
    for k in WASTE_KEYS:
        try:
            del data[k]
        except:
            continue
    with open(os.path.join(GRDPCLI_HOME_DIR, GRDPCLI_CONFIG_JSON), 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)

def setActiveProject(id):
    config_data = getGRCPcliConfig()
    config_data['active_project'] = id
    createGRCPcliConfig(config_data)

def generateKubectlConfig():
    projects = json.load(open(os.path.join(GRDPCLI_HOME_DIR, GRDPCLI_PROJECT_JSON)))
    config = json.load(open(os.path.join(GRDPCLI_HOME_DIR, GRDPCLI_CONFIG_JSON)))

    id = getProjectsId()
    k8s_authority_data = config['k8s_authority_data']
    k8s_api_address = config['k8s_api_address']
    for key in projects[id].keys():
        if key == 'status':
            continue
        namespace_name = projects[id][key]['K8S_NAMESPACE']
        access_token = projects[id][key]['K8S_ACCESS_TOKEN']
        break

    kubectl_template = kubectl_clusters_template.format(namespace_name=namespace_name, k8s_authority_data=k8s_authority_data, k8s_api_address=k8s_api_address, access_token=access_token)
    with open(KUBECTL_CONFIG, "w") as config:
        config.write(kubectl_template.lstrip())

class callbackServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_POST(self):
        post_data = self.rfile.read(int(self.headers['Content-Length']))
        response_data = json.loads(post_data.decode('utf-8'))

        self._set_headers()
        self.wfile.write(bytes("", "utf-8"))

        if checkToken(response_data["access_token"]):
            cliConfigCreate(response_data["access_token"])
        createGRCPcliConfig(response_data)

        if os.path.exists(os.path.join(GRDPCLI_HOME_DIR,GRDPCLI_PROJECT_JSON)) and os.path.exists(os.path.join(GRDPCLI_HOME_DIR,GRDPCLI_CONFIG_JSON)):
            logger.info("Projects configuration file generated successfully")
            raise SystemExit
        else:
            raise ValueError('Projects configuration file not found or broken')

    def log_message(self, format, *args):
        return
