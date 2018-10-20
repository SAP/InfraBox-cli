import json
import string
import random
import base64
import sys
import os
import subprocess
import yaml

import inquirer
from halo import Halo

CLUSTER_PROVIDERS = [
    'Google Kubernetes Engine',
    'Use cluster from kubeconfig'
]

def execute(cmd, cwd=None, shell=False, ignore_error=False):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, cwd=cwd, shell=shell)
    except subprocess.CalledProcessError as e:
        if ignore_error:
            raise
        else:
            print(e.output)
            sys.exit(1)

@Halo(text='Creating GKE Cluster', spinner='dots')
def create_gke_cluster(name):
    execute(['gcloud', 'container', 'clusters', 'create', name,
             '--zone', 'us-east1-b',
             '--machine-type', 'n1-standard-4'])

def create_namespace(name):
    try:
        execute(['kubectl', 'get', 'ns', name], ignore_error=True)
    except:
        execute(['kubectl', 'create', 'ns', name])

@Halo(text='Creating Namespaces', spinner='dots')
def create_namespaces():
    create_namespace('infrabox-system')
    create_namespace('infrabox-worker')

@Halo(text='Installing helm', spinner='dots')
def install_helm():
    try:
        execute(['kubectl', 'get', '-n', 'kube-system', 'sa', 'tiller'], ignore_error=True)
        return
    except:
        pass

    execute(['helm', 'repo', 'update'])
    execute(['kubectl', '-n', 'kube-system', 'create', 'sa', 'tiller'])
    execute(['kubectl', 'create', 'clusterrolebinding', 'tiller',
             '--clusterrole', 'cluster-admin', '--serviceaccount=kube-system:tiller'])
    execute(['helm', 'init', '--service-account', 'tiller', '--wait'])

@Halo(text='Installing PostgreSQL', spinner='dots')
def install_postgres():
    try:
        execute(['kubectl', 'get', '-n', 'infrabox-system', 'deployments', 'postgres-postgresql'], ignore_error=True)
        return
    except:
        pass

    execute(['helm', 'install', '--name', 'postgres', 'stable/postgresql',
             '--set', 'imageTag=9.6.2,postgresPassword=postgres,probes.readiness.periodSeconds=5',
             '--namespace', 'infrabox-system'])

@Halo(text='Installing Minio', spinner='dots')
def install_minio():
    try:
        execute(['kubectl', 'get', '-n', 'infrabox-system', 'deployments', 'infrabox-minio'], ignore_error=True)
        return
    except:
        pass

    execute(['helm', 'install', '--set', 'serviceType=ClusterIP,replicas=1,persistence.enabled=false',
             '-n', 'infrabox-minio', '--wait', '--namespace', 'infrabox-system', 'stable/minio'])

@Halo(text='Preflight checks', spinner='dots')
def preflight_checks():
    execute(['helm', 'version', '--client'])
    execute(['kubectl', 'version', '--client'])
    execute(['gcloud', '--version'])
    execute(['git', 'version'])

@Halo(text='Install nginx ingress', spinner='dots')
def install_nginx_ingress():
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


@Halo(text='Clone InfraBox repository', spinner='dots')
def clone_repo(a):
    execute(['mkdir', '-p', a['workdir']])
    repo_dir = os.path.join(a['workdir'], 'InfraBox')

    execute(['rm', '-rf', repo_dir])
    execute(['git', 'clone', 'https://github.com/SAP/InfraBox.git'], cwd=a['workdir'])
    execute(['git', 'checkout', a['infrabox-version']], cwd=repo_dir)

@Halo(text='Generate keys', spinner='dots')
def generate_keys(a):
    if os.path.exists(os.path.join(a['workdir'], 'id_rsa')):
        return

    execute(['ssh-keygen', '-N', '', '-t', 'rsa', '-f', 'id_rsa'], cwd=a['workdir'])
    execute('ssh-keygen -f id_rsa.pub -e -m pem > id_rsa.pem', shell=True, cwd=a['workdir'])


@Halo(text='Install InfraBox', spinner='dots')
def helm_install_infrabox(a):
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
            'private_key': base64.b64encode(open(os.path.join(a['workdir'], 'id_rsa')).read()),
            'public_key': base64.b64encode(open(os.path.join(a['workdir'], 'id_rsa.pub')).read())
        },
        'host': str(a['host']),
        'database': {
            'postgres': {
                'enabled': True,
                'username': 'postgres',
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


@Halo(text='Install certificates', spinner='dots')
def install_certificates(a):
    try:
        execute(['kubectl', 'get', '-n', 'infrabox-system', 'secrets', 'infrabox-tls-certs'], ignore_error=True)
        return
    except:
        pass

    execute(['openssl', 'req', '-x509', '-nodes', '-days', '365', '-newkey', 'rsa:2048',
             '-keyout', '/tmp/tls.key', '-out', '/tmp/tls.crt', '-subj', '/CN=%s' % a['host']])
    execute(['kubectl', 'create', '-n', 'infrabox-system', 'secret', 'tls', 'infrabox-tls-certs',
             '--key', '/tmp/tls.key', '--cert', '/tmp/tls.crt'])

def install():
    preflight_checks()

    questions = [
        inquirer.Text('cluster-name', message="Name of the cluster"),
        inquirer.List('cluster-provider',
                      message="On which provider should we create the kubernetes cluster",
                      choices=CLUSTER_PROVIDERS,
                     ),
        inquirer.List('infrabox-version',
                      message="Which version of InfraBox do you want to install",
                      choices=['1.1.0'],
                     ),
        inquirer.Text('admin-email', message="Admin email"),
        inquirer.Checkbox('components',
                          message="Which component would you like to configure",
                          choices=['Github'],
                         ),
    ]
    config = inquirer.prompt(questions)

    if 'Github' in config['components']:
        questions = [
            inquirer.Text('github-client-id', message="Github Client ID"),
            inquirer.Text('github-client-secret', message="Github Client Secret"),
            inquirer.Text('github-allowed-orgs',
                          message="Comma separated list of Github Organizations allowed to login"),
        ]

        answers = inquirer.prompt(questions)
        config.update(answers)

    questions = [
        inquirer.List('start',
                      message="Select yes to start installation",
                      choices=['no', 'yes'],
                     ),
    ]

    answers = inquirer.prompt(questions)
    if answers['start'] != 'yes':
        return


    config['admin-password'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

    if config['cluster-provider'] == CLUSTER_PROVIDERS[0]:
        create_gke_cluster(config['cluster-name'])

    config['workdir'] = '/tmp/install-infrabox/%s' % config['cluster-name']

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

def install_infrabox(_):
    install()
