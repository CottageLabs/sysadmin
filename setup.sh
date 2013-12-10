
# this may be needed - not sure, seems to work without it
#export DEBIAN_FRONTEND=noninteractive

# create user - DO THIS MANUALLY, AND GIVE THE USER A PASSWORD
# REMEMBER TO UPLOAD SOME PUBLIC KEYS BEFORE CHANGING THE SSH SETTINGS
# adduser --gecos "" XXX-USERNAME-HERE-XXX
# and set the pw at the prompt
# (there is a usual CL username and password, but they are not stored here ...)
cd /home/cloo
mkdir /home/cloo/.ssh
chown cloo:cloo /home/cloo/.ssh
chmod 700 /home/cloo/.ssh
vim /home/cloo/.ssh/authorized_keys
# and copy required pubkeys into it
chown cloo:cloo /home/cloo/.ssh/authorized_keys
chmod 600 /home/cloo/.ssh/authorized_keys
# if version ubuntu 12.04 - previous to that the group was admin 
adduser cloo sudo
# visudo and set cloo ALL=(ALL) NOPASSWD: ALL at the end

# prevent "unknown host" message when doing sudo
# regular user version: sudo sh -c 'echo "127.0.1.1       "`cat /etc/hostname` >> /etc/hosts'
# but if you're root (should be at this point of script)
echo "127.0.1.1       "`cat /etc/hostname` >> /etc/hosts


# apt install useful stuff
apt-get update
apt-get -q -y install bpython screen htop nginx git-core curl anacron
apt-get -q -y install python-pip python-dev python-setuptools build-essential
apt-get -q -y install openjdk-6-jdk openjdk-6-jre-headless


# pip install useful python stuff
pip install --upgrade pip
ln -s /usr/local/bin/pip /usr/bin/pip
pip install --upgrade virtualenv
pip install gunicorn
pip install requests


# get latest version of supervisor via pip
pip install supervisor
curl https://gist.github.com/howthebodyworks/176149/raw/88d0d68c4af22a7474ad1d011659ea2d27e35b8d/supervisord.sh > ~/supervisord
mv ~/supervisord /etc/init.d/supervisord
chmod a+x /etc/init.d/supervisord
/usr/sbin/service supervisord stop
update-rc.d supervisord defaults
mv /etc/supervisor/supervisord.conf /etc
ln -s /etc/supervisord.conf /etc/supervisor/supervisord.conf
/usr/sbin/service supervisord start


# set up firewall - allow 22, 80, 443
apt-get -q -y install ufw
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable


# get elasticsearch
cd /opt
curl -L https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.5.tar.gz -o elasticsearch.tar.gz
tar -xzvf elasticsearch.tar.gz
ln -s elasticsearch-0.90.5 elasticsearch
rm elasticsearch.tar.gz
cd elasticsearch/bin
git clone git://github.com/elasticsearch/elasticsearch-servicewrapper.git
cd elasticsearch-servicewrapper
mv service ../
cd ../
rm -R elasticsearch-servicewrapper
ln -s /opt/elasticsearch/bin/service/elasticsearch /etc/init.d/elasticsearch
update-rc.d elasticsearch defaults
/etc/init.d/elasticsearch start
# elasticsearch settings
# vim config/elasticsearch.yml and uncomment bootstrap.mlockall: true
# and uncomment cluster.name: elasticsearch (and change cluster name if necessary)
# vim bin/service/elasticsearch.conf and set.default.ES_HEAP_SIZE=4096 or whatever value works for the machine
# then vim /etc/security/limits.conf and put this in:
# root  hard  nofile  1024000
# root  soft  nofile  1024000
# root  hard  memlock unlimited
# root  soft  memlock unlimited
# * hard  nofile  1024000
# * soft  nofile  1024000
# * hard  memlock unlimited
# * soft  memlock unlimited
# and then vim /etc/pam.d/common-session and /etc/pamd.d/common-session-noninteractive
# and put the following in it:
# session required      pam_limits.so


# edit the ssh settings
vim /etc/ssh/sshd_config
# change it as follows:
PermitRootLogin no
PasswordAuthentication no
/etc/init.d/ssh restart


# install node
#apt-get install python-software-properties
#apt-add-repository ppa:chris-lea/node.js
#apt-get update
#apt-get install nodejs npm
#npm install sqlite3


# install php stuff
#apt-get install php5 php5-cli php5-mysql php5-cgi
#add-apt-repository ppa:brianmercer/php
#apt-get update
#apt-get install php5-fpm


# install mysql stuff
#apt-get install mysql-server libmysqlclient-dev python-mysqldb
#pip install mysql-python


# installing etherpad lite
# http://mclear.co.uk/2011/08/01/install-etherpad-lite-on-ubuntu/
# https://github.com/Pita/etherpad-lite/wiki/How-to-deploy-Etherpad-Lite-as-a-service
#apt-get install build-essential python libssl-dev libsqlite3-dev gzip curl
#cd /opt
#git clone git://github.com/Pita/etherpad-lite.git
#useradd etherpad-lite
#mkdir /var/log/etherpad-lite
#chown -R etherpad-lite:etherpad-lite /var/log/etherpad-lite
#chown -R etherpad-lite:etherpad-lite /opt/etherpad-lite
#cd /etc/init.d
#vim etherpad-lite # and copy the script from the above linked page into it, and customise
# e.g. change the path to link to where node is on this install - /usr/bin/node/bin
# and the eplite dir - 
#chmod +x etherpad-lite
#update-rc.d etherpad-lite defaults
#cd /opt/etherpad-lite
# edit the settings.json - change db type to sqlite and db file to var/sqlite.db





