#!/usr/bin/env bash

# Dependencies
apt-get update
apt-get install -y  curl wget socat sudo git
pip install --upgrade pip

# Minikube
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
cp minikube /usr/local/bin
rm minikube

# KVM2
apt-get install -y  libvirt-clients libvirt-daemon-system qemu-kvm
curl -LO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2
chmod +x docker-machine-driver-kvm2
mv docker-machine-driver-kvm2 /usr/local/bin/

# Docker
apt-get install -y  docker.io

# Helm
wget https://get.helm.sh/helm-v2.14.2-linux-amd64.tar.gz
tar -zxvf helm-v2.14.2-linux-amd64.tar.gz
rm helm-v2.14.2-linux-amd64.tar.gz
cp linux-amd64/helm /usr/local/bin
cp linux-amd64/tiller /usr/local/bin
rm -rf linux-amd64


# Kubectl
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
chmod +x ./kubectl
mv ./kubectl /usr/local/bin/kubectl


# Gcloud
curl -sSL https://sdk.cloud.google.com | bash
ln -s /root/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud

# InfraBox CLI
apt-get install -y  python python-pip python-dev python3 python3-pip python3-dev libffi-dev gcc
GIT_SSL_NO_VERIFY=true git clone https://github.com/SAP/InfraBox-cli
cd v2infraboxapi
pip install --requirement=requirements_python2.txt
pip3 install --requirement=requirements_python3.txt
#python setup.py install
python3 setup.py install

# Minikube start
minikube start --vm-driver=kvm2
minikube tunnel > /dev/null 2> /dev/null &

infrabox install -n TestCluster --kubeconfig -e admin@admin.com -p admin --no-components --no-confirmation -v 1.1.5
