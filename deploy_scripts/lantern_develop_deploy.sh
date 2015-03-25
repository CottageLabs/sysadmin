sudo ln -sf /opt/sysadmin/config/supervisor/conf.d/lantern-test.conf /etc/supervisor/conf.d/lantern-test.conf
sudo ln -sf /opt/sysadmin/config/supervisor/conf.d/oagr-test-daemon.conf /etc/supervisor/conf.d/oagr-test-daemon.conf
sudo ln -sf /opt/sysadmin/config/supervisor/conf.d/lantern-test-daemon.conf /etc/supervisor/conf.d/lantern-test-daemon.conf

sudo ln -sf /opt/sysadmin/config/nginx/sites-available/lantern-test /etc/nginx/sites-available/lantern-test
sudo ln -sf /etc/nginx/sites-available/lantern-test /etc/nginx/sites-enabled/lantern-test

sudo apt-get update -q -y
sudo apt-get -q -y install libxml2-dev libxslt-dev python-dev lib32z1-dev
cd /opt/lantern
. bin/activate
cd src/lantern
git checkout develop
git pull
git submodule update --recursive --init
git submodule update --recursive

cd esprit
pip install -e .
cd ..

cd magnificent-octopus
pip install -e .
cd ..

pip install -e .

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart lantern-test
sudo supervisorctl restart lantern-test-daemon
sudo supervisorctl restart oagr-test-daemon
sudo nginx -t && sudo nginx -s reload
