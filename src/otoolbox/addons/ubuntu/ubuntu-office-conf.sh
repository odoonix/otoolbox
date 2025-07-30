#!/bin/bash

############################################################
# APT
############################################################
echo "Installing APT and APT-GET proxy"
echo '' > /etc/apt/apt.conf.d/30proxy
echo 'Acquire::http::Proxy "http://192.168.88.111:3128";' > /etc/apt/apt.conf.d/proxy

apt update -y
apt install -y

############################################################
# Python
############################################################
echo "Configure pip proxy"
echo << EOF
[global]
proxy = http://192.168.88.111:3128

EOF
> /etc/pip.conf




############################################################
# Cockpit
############################################################
echo "Installing cockpit"
. /etc/os-release
apt install -y -t ${VERSION_CODENAME}-backports \
    cockpit \
    cockpit-pcp \
    cockpit-bridge \
    cockpit-storaged


systemctl enable cockpit


############################################################
# Cokpit
############################################################
apt install -y \
    openssh-server \
    openssh-client

mkdir -p /root/.ssh
touch /root/.ssh/authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDgkKnDH/\
ruQAquOB1FgQW0glN7vVnTJnNoiESNbrgPI46od4dwVoR+Xc4wVU\
qP3eRhbOCgqlilxdos6XgG8y7fuDgA3MVEIyvO3pUF3jRhTw7uJm\
3JOMFyfxBAszlQsOROU24HdaUEAWNi4z1Ks6P+oTywa76A0NbHGU\
kydDnCirEVtP+lSR715s3GP0E5SKrlIYoSiI0v4EFItWdU8oIYr9\
pa7s0G1tm1XZ8CLHTGUZKxeo8bQRYEbn8DtRReL5R5val3DBWxdj\
ybRuQGnT05xvn687AjeOdrC8p95bLlaV+/H+C5umHYmKottlPYGd\
YUoZVXWgM4WAJ2GLUYMcFdZRiCvzChocp8e3PGbsdquyESsEvMAq\
j9KFfDAejiV3i32IN4eJcOp3uW3Fx9nI+fbSit0qWwoS4RSz440L\
5+PNZ+AdAXs9/7wxkMjXWkr8naJXbg1oTG3M8XtjMZkfpYRuJ2P5\
2/fXpSXIrSHkPjUXc9j8i+vj+VFE+QJxhxB/E= \
maso@localhost.localdomain" >> "/root/.ssh/authorized_keys"



############################################################
# Storage
############################################################
apt install -y \
    nfs-common
mkdir -p /mnt/storage_share