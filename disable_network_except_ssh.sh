#!/bin/sh

die() { printf %s "${@+$@$'\n'}" ; exit 1; }

if [ $# -ne 1 ]
then
    echo "1 argument needed"
    echo "Usage: $0 <server external IP>"
    echo
    echo "Example: $0 93.93.131.168"
    echo "  will disable all network traffic except incoming ssh on that server"
    exit 1
fi

# My system IP/set ip address of server
PATH=$PATH:/sbin
SERVER_IP=$1
# Flushing all rules
sudo iptables -F
sudo iptables -X
# Setting default filter policy
sudo iptables -P INPUT DROP
sudo iptables -P OUTPUT DROP
sudo iptables -P FORWARD DROP
# Allow unlimited traffic on loopback
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT

# Allow incoming ssh only
sudo iptables -A INPUT -p tcp -s 0/0 -d $SERVER_IP --sport 513:65535 --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT
sudo iptables -A OUTPUT -p tcp -s $SERVER_IP -d 0/0 --sport 22 --dport 513:65535 -m state --state ESTABLISHED -j ACCEPT
# make sure nothing comes or goes out of this box
sudo iptables -A INPUT -j DROP
sudo iptables -A OUTPUT -j DROP
