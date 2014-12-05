sudo apt-get update -q -y
sudo apt-get -q -y install libxml2-dev libxslt-dev python-dev lib32z1-dev
cd /opt/oacwellcome
. bin/activate
cd src/oacwellcome
git checkout develop
git pull
git submodule update --init

cd esprit
git submodule update --init
pip install -e .
cd ..

cd magnificent-octopus
git submodule update --init
pip install -e .
cd ..

pip install -e .

sudo supervisorctl restart oacwellcome-test
