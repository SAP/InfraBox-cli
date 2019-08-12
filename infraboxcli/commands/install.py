import base64
import json
import os
import random
import string
import subprocess

import appdirs
import click
import inquirer
import yaml

import infraboxcli

CLUSTER_PROVIDERS = [
    'Google Kubernetes Engine',
    'Use cluster from kubeconfig'
]

VERSIONS = ['1.1.4', '1.1.5']


@click.command()
@click.option("-n", "--name", "cluster_name", default=None,
              help="The cluster's name.")
@click.option("-c", "--kubeconfig", "kubeconfig", is_flag=True,
              help="Use cluster from kubeconfig as provider.")
@click.option("-e", "--email", "admin_email", default=None,
              help="The admin's email.")
@click.option("-p", "--password", "admin_password", default=None,
              help="The admin's password. If not specified, will be generated randomly.")
@click.option("-v", "--version", "infrabox_version", default=VERSIONS[-1], type=click.Choice(VERSIONS),
              help="The version of InfraBox which should get installed.")
# @click.option("-f", "--config-file", "config_file", type=click.File('r'), default=None,
#               help="The config file used to install InfraBox with helm.")
@click.option("--no-components", "no_components", is_flag=True,
              help="Whether we should install no components.")
@click.option("--no-confirmation", "no_confirmation", is_flag=True,
              help="Whether we should not ask the user for confirmation before launching the installation.")
def install(cluster_name, kubeconfig, admin_email, admin_password, infrabox_version, no_components,
            no_confirmation):
    """
    Installs InfraBox.
    \f
    :type cluster_name: str
    :param: cluster_name: The cluster's name
    :type kubeconfig: bool
    :param: kubeconfig: Whether we should use the cluster from kubeconfig
    :type admin_email: str
    :param: admin_email: The admin's email.
    :type admin_password: str
    :param: admin_password: The admin's password
    :type infrabox_version: str
    :param infrabox_version: the version of InfraBox which should get installed
    :type no_components: bool
    :param: no_components: Whether we should install no components
    :type no_confirmation: bool
    :param: no_confirmation: Whether we should not ask the user for confirmation before launching the installation
    """
    # :type config_file: str
    # :param config_file: the config file used to install InfraBox with helm
    preflight_checks()

    questions = []
    config = dict()

    # Cluster name option
    if cluster_name is None:
        questions.append(inquirer.Text('cluster-name', message="Name of the cluster"))
    else:
        config['cluster-name'] = cluster_name

    # Cluster provider option
    if not kubeconfig:
        questions.append(inquirer.List('cluster-provider',
                                       message="On which provider should we create the kubernetes cluster",
                                       choices=CLUSTER_PROVIDERS))
    else:
        config['cluster-provider'] = CLUSTER_PROVIDERS[1]

    # InfraBox version choice
    if infrabox_version is None:
        questions.append(inquirer.List('infrabox-version',
                                       message="Which version of InfraBox do you want to install",
                                       choices=VERSIONS))
    else:
        config['infrabox-version'] = infrabox_version

    # Admin email
    if admin_email is None:
        questions.append(inquirer.Text('admin-email', message="Admin email"))
    else:
        config['admin-email'] = admin_email

    # Components
    if not no_components:
        questions.append(inquirer.Checkbox('components',
                                           message="Which component would you like to configure",
                                           choices=['Github']))
    else:
        config['components'] = []

    if questions:
        config.update(inquirer.prompt(questions))

    # Github component
    if 'Github' in config['components']:
        questions = [
            inquirer.Text('github-client-id', message="Github Client ID"),
            inquirer.Text('github-client-secret', message="Github Client Secret"),
            inquirer.Text('github-allowed-orgs',
                          message="Comma separated list of Github Organizations allowed to login"),
        ]

        config.update(inquirer.prompt(questions))

    # Confirmation?
    if not no_confirmation:
        questions = [
            inquirer.List('start',
                          message="Select yes to start installation",
                          choices=['no', 'yes'],
                          ),
        ]

        answers = inquirer.prompt(questions)
        if answers['start'] != 'yes':
            return

    config['admin-password'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in
                                       range(10)) if admin_password is None else admin_password

    if config['cluster-provider'] == CLUSTER_PROVIDERS[0]:
        create_gke_cluster(config['cluster-name'])

    config['workdir'] = os.path.join(appdirs.user_cache_dir("InfraBoxCLI"), "install-infrabox",
                                     "%s" % config['cluster-name'])
    config["config_file"] = config_file

    create_namespaces()
    install_helm()
    install_postgres()
    install_minio()
    install_nginx_ingress()
    config['host'] = get_host()
    install_certificates(config)
    clone_repo(config)
    generate_keys(config)
    helm_install_infrabox(config)

    print("Your InfraBox is ready: https://%s" % config['host'])
    print()

    if 'Github' in config['components']:
        print("IMPORTANT: Update your Github callback url to: https://%s/github/auth/callback" % config['host'])
        print()

    print("The configuration has been stored here: %s" % config['workdir'])
    print("Please keep a backup of it at a secure place.")
    print("It contains secret data like the encryption key and your admin password.")


def execute(cmd, cwd=None, shell=False, ignore_error=False):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, cwd=cwd, shell=shell)
    except subprocess.CalledProcessError as e:
        if ignore_error:
            raise
        else:
            infraboxcli.logger.error(e)


def create_gke_cluster(name):
    print('# Creating GKE Cluster')
    execute(['gcloud', 'container', 'clusters', 'create', name,
             '--zone', 'us-east1-b',
             '--machine-type', 'n1-standard-4'])


def create_namespace(name):
    try:
        execute(['kubectl', 'get', 'ns', name], ignore_error=True)
    except:
        execute(['kubectl', 'create', 'ns', name])


def create_namespaces():
    print('# Creating Namespaces')
    create_namespace('infrabox-system')
    create_namespace('infrabox-worker')


def install_helm():
    print('# Installing helm')
    try:
        execute(['kubectl', 'get', '-n', 'kube-system', 'sa', 'tiller'], ignore_error=True)
        return
    except:
        pass

    execute(['kubectl', '-n', 'kube-system', 'create', 'sa', 'tiller'])
    execute(['kubectl', 'create', 'clusterrolebinding', 'tiller',
             '--clusterrole', 'cluster-admin', '--serviceaccount=kube-system:tiller'])
    execute(['helm', 'init', '--service-account', 'tiller', '--wait'])


def install_postgres():
    print('# Installing PostgreSQL')
    try:
        execute(['kubectl', 'get', '-n', 'infrabox-system', 'deployments', 'postgres-postgresql'], ignore_error=True)
        return
    except:
        pass

    execute(['helm', 'install', '--name', 'postgres', 'stable/postgresql', '--version', '1.0.0',
             '--set', 'imageTag=9.6.2,postgresPassword=postgres,postgresUser=infrabox,probes.readiness.periodSeconds=5',
             '--namespace', 'infrabox-system'])


def install_minio():
    print('# Installing Minio')
    try:
        execute(['kubectl', 'get', '-n', 'infrabox-system', 'deployments', 'infrabox-minio'], ignore_error=True)
        return
    except:
        pass

    execute(['helm', 'install', '--set', 'serviceType=ClusterIP,replicas=1,persistence.enabled=false',
             '-n', 'infrabox-minio', '--wait', '--namespace', 'infrabox-system', 'stable/minio'])


def preflight_checks():
    def try_command(command):
        try:
            execute(command)
        except OSError:
            infraboxcli.logger.error("Please install the following app: " + command[0])

    print('# Preflight checks')
    try_command(['helm', 'version', '--client'])
    try_command(['kubectl', 'version', '--client'])
    try_command(['gcloud', '--version'])
    try_command(['git', 'version'])


def install_nginx_ingress():
    print('# Install nginx ingress')
    try:
        execute(['kubectl', 'get', '-n', 'kube-system', 'deployments', 'nic-nginx-ingress-controller'],
                ignore_error=True)
        return
    except:
        pass

    execute(['helm', 'install', '-n', 'nic', '--namespace', 'kube-system',
             '--wait', 'stable/nginx-ingress'])


def get_host():
    o = execute(['kubectl', 'get', 'services', '-n', 'kube-system', 'nic-nginx-ingress-controller', '-o', 'json'])
    j = json.loads(o)
    ip = j['status']['loadBalancer']['ingress'][0]['ip']
    return "%s.nip.io" % ip


def clone_repo(a):
    print('# Clone InfraBox repository')
    execute(['mkdir', '-p', a['workdir']])
    repo_dir = os.path.join(a['workdir'], 'InfraBox')

    execute(['rm', '-rf', repo_dir])
    execute(['git', 'clone', 'https://github.com/SAP/InfraBox.git'], cwd=a['workdir'])
    execute(['git', 'checkout', a['infrabox-version']], cwd=repo_dir)


def generate_keys(a):
    print('# Generate keys')
    if not os.path.isfile(os.path.join(a['workdir'], 'jwtRS256.key')):
        execute(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-m', 'PEM', '-f', 'jwtRS256.key', '-q', '-N', ''], cwd=a['workdir'])
        execute(['openssl', 'rsa', '-in', 'jwtRS256.key', '-pubout', '-outform', 'PEM', '-out', 'jwtRS256.key.pub'],
                cwd=a['workdir'])


def helm_install_infrabox(a):
    print('# Install InfraBox')
    # if a["config_file"] is not None:
    #     config = yaml.load(a["config_file"], Loader=yaml.FullLoader)
    # else:
    config = {
        'image': {
            'tag': a['infrabox-version'],
        },
        'general': {
            'dont_check_certificates': True,
        },
        'admin': {
            'email': a['admin-email'],
            'password': a['admin-password'],
            'private_key': base64.b64encode(open(os.path.join(a['workdir'], 'jwtRS256.key'), "rb").read()),
            'public_key': base64.b64encode(open(os.path.join(a['workdir'], 'jwtRS256.key.pub'), "rb").read())
        },
        'host': str(a['host']),
        'database': {
            'postgres': {
                'enabled': True,
                'username': 'infrabox',
                'password': 'postgres',
                'db': 'postgres',
                'host': 'postgres-postgresql.infrabox-system'
            }
        },
        'storage': {
            's3': {
                'enabled': True,
                'endpoint': 'infrabox-minio.infrabox-system',
                'bucket': 'infrabox',
                'secure': False,
                'secret_access_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
                'access_key_id': 'AKIAIOSFODNN7EXAMPLE',
                'region': 'us-east1',
                'port': '9000',
            }
        },
        'job': {
            'docker_daemon_config': str('{"insecure-registries": ["%s"]}' % a['host'])
        }
    }

    if 'Github' in a['components']:
        config['github'] = {
            'enabled': True,
            'client_id': a['github-client-id'],
            'client_secret': a['github-client-secret'],
            'webhook_secret': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)),
            'login': {
                'enabled': True,
                'allowed_organizations': a['github-allowed-orgs']
            }
        }

    with open(os.path.join(a['workdir'], 'values.yaml'), 'w+') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)

    execute(['helm', 'install', '-n', 'infrabox',
             os.path.join(a['workdir'], 'InfraBox', 'deploy', 'infrabox'),
             '-f', 'values.yaml', '--wait',
             ], cwd=a['workdir'])


def install_certificates(a):
    print('# Install certificates')
    try:
        execute(['kubectl', 'get', '-n', 'infrabox-system', 'secrets', 'infrabox-tls-certs'], ignore_error=True)
        return
    except:
        pass

    execute(['openssl', 'req', '-x509', '-nodes', '-days', '365', '-newkey', 'rsa:2048',
             '-keyout', '/tmp/tls.key', '-out', '/tmp/tls.crt', '-subj', '/CN=%s' % a['host']])
    execute(['kubectl', 'create', '-n', 'infrabox-system', 'secret', 'tls', 'infrabox-tls-certs',
             '--key', '/tmp/tls.key', '--cert', '/tmp/tls.crt'])
