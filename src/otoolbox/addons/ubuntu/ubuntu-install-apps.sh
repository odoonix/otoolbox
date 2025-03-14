#!/bin/bash
apt update -y
apt upgrade -y
############################################################
# Python3
############################################################
echo "Installing Python"
apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    python3-wheel \
    python3-gevent \
    python-is-python3 \
    python3-ldap \
    python3-ldap3 \
    python3-pyldap \
    python3-cachetools \
    libldap2-dev \
    libsasl2-dev \
    pre-commit
    



############################################################
# Developer Tools
############################################################
snap install code --classic
snap install postman
snap install chromium
snap install skype
snap install audacity
apt install -y \
    git \
    inkscape \
    build-essential \
    default-jdk \
    libpq-dev

snap install node --classic
npm install -g rtlcss

apt install -y \
    vlc \
    vlc-plugin-base \
    vlc-plugin-access-extra \
    vlc-plugin-bittorrent \
    vlc-plugin-video-splitter


apt install -y \
    webp
############################################################
# Docker
############################################################
apt install -y \
    docker \
    docker-compose \
    docker-compose-v2

systemctl enable docker

############################################################
# Multimedia
############################################################
apt install -y \
    ubuntu-restricted-extras

