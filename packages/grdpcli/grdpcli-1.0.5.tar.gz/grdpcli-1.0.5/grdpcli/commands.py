import subprocess
import os

from grdpcli import *
from grdpcli.logger import logger

def command_update():
    """
        Updating configurations
    """
    logger.info("Updating GRDPCLI config")
    os.remove(os.path.join(GRDPCLI_HOME_DIR, GRDPCLI_CONFIG_JSON))
    os.remove(os.path.join(GRDPCLI_HOME_DIR, GRDPCLI_PROJECT_JSON))
    logger.info("Authorization is required, please ENTER to open up the browser to login or CTRL+C to cancel:")
    WEBSERVER = HTTPServer((hostName, serverPort), callbackServer)
    webbrowser.open(AUTH_ADDRESS, new=0, autoraise=True)
    logger.info("Waiting for authorization is compleate ...")
    try:
        WEBSERVER.serve_forever()
    except KeyboardInterrupt:
        pass

def command_projects():
    """
        Getting list of projects.
        Prints a table with list of projects and generates config file.
    """
    projects = getProjectsJson()
    IDS_LIST = projects.keys()
    active_project_id = getGRCPcliConfig()['active_project']
    result = subprocess.Popen(
        ["git", "rev-parse", "--show-toplevel"], 
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE)
    output, error = result.communicate()
    output = os.path.basename(output.decode().replace("\n", ""))
    if output:
        for key, val in projects.items():
            keys = [key.lower() for key in val.keys()]
            if output in keys:
                logger.info("Found active project id using git repository")
                setActiveProject(key)
                active_project_id = getGRCPcliConfig()['active_project']
    active_project_id = None if active_project_id == 'None' else active_project_id

    while True:
        if active_project_id:
            id = getGRCPcliConfig()['active_project']
            break

        id = input("Please provide id of your project, current active project is `{}: {}`: ".format(active_project_id, getProjectName(active_project_id)))

        if id not in IDS_LIST:
            logger.error("Project id is incorrect, please provide correct value")
        else:
            setActiveProject(id)
            break
    logger.info("Current active project is `{}`".format(getProjectName(id)))
    generateKubectlConfig()

def command_help():
    """
        Help command.
    """
    raise NotImplemented

def commandHandler(commands):
    """
        Handler for cli commands.
    """
    SUBCOMMANDS = ['update','projects']
    if len(commands) > 1:
        if commands[1] in SUBCOMMANDS:
            if commands[1] == 'update':
                command_update()
            if commands[1] == 'help':
                command_help()
            if commands[1] == 'projects':
                command_projects()
        else:
            del commands[0]
            options = " ".join(commands)

            active_project_id = getGRCPcliConfig()['active_project']
            active_project_id = None if active_project_id == 'None' else active_project_id

            if not active_project_id:
                command_projects()

            context = getNamespaceName(getGRCPcliConfig()['active_project'])
            exit(os.WEXITSTATUS(os.system('KUBECONFIG={} kubectl --context {} {}'.format(KUBECTL_CONFIG, context, options))))
    else:
        command_projects()
