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

kill -HUP $(sudo supervisorctl pid lantern-test)
supervisorctl restart lantern-test-daemon
supervisorctl restart oagr-test-daemon
