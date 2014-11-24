sudo apt-get update -q -y
sudo apt-get -q -y install libxml2-dev libxslt-dev python-dev lib32z1-dev
cd /opt/doaj
. bin/activate
cd src/doaj
git checkout master
git pull
git submodule init
git submodule update
pip install -r requirements.txt
sudo supervisorctl restart doaj-staging
