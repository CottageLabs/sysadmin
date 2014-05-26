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
SERVER_IP=$1
# Flushing all rules
iptables -F
iptables -X
# Setting default filter policy
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -P FORWARD DROP
# Allow unlimited traffic on loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
 
# Allow incoming ssh only
iptables -A INPUT -p tcp -s 0/0 -d $SERVER_IP --sport 513:65535 --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -p tcp -s $SERVER_IP -d 0/0 --sport 22 --dport 513:65535 -m state --state ESTABLISHED -j ACCEPT
# make sure nothing comes or goes out of this box
iptables -A INPUT -j DROP
iptables -A OUTPUT -j DROP
