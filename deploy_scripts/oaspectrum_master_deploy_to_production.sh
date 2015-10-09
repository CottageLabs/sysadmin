sudo apt-get update -q -y
sudo apt-get -q -y install libxml2-dev libxslt-dev python-dev lib32z1-dev
cd /opt/oaspectrum
. bin/activate
cd src/oaspectrum
git checkout master
git pull
git checkout $(git describe --abbrev=0 --tags)  # get latest tag on master
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

sudo supervisorctl restart oaspectrum-production
