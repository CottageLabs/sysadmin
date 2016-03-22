sudo ln -sf /opt/sysadmin/config/supervisor/conf.d/oacwellcome-test.conf /etc/supervisor/conf.d/oacwellcome-test.conf
sudo ln -sf /opt/sysadmin/config/supervisor/conf.d/oagr-oacwellcome-test-daemon.conf /etc/supervisor/conf.d/oagr-oacwellcome-test-daemon.conf
sudo ln -sf /opt/sysadmin/config/supervisor/conf.d/oacwellcome-test-daemon.conf /etc/supervisor/conf.d/oacwellcome-test-daemon.conf

sudo ln -sf /opt/sysadmin/config/nginx/sites-available/oacwellcome-test /etc/nginx/sites-available/oacwellcome-test
sudo ln -sf /etc/nginx/sites-available/oacwellcome-test /etc/nginx/sites-enabled/oacwellcome-test

sudo apt-get update -q -y
sudo apt-get -q -y install libxml2-dev libxslt-dev python-dev lib32z1-dev

if [ ! -d /opt/oacwellcome ]; then
    cd /opt
    sudo mkdir oacwellcome
    sudo chown cloo:cloo oacwellcome
    virtualenv -p python2.7 oacwellcome
    cd oacwellcome
    mkdir src
    cd src
    git clone https://github.com/CottageLabs/oacwellcome.git oacwellcome
fi

cd /opt/oacwellcome
. bin/activate
cd src/oacwellcome
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
sudo supervisorctl restart oacwellcome-test
sudo supervisorctl restart oacwellcome-test-daemon
sudo supervisorctl restart oagr-oacwellcome-test-daemon
sudo nginx -t && sudo nginx -s reload
