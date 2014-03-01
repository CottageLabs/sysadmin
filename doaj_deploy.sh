#!/bin/bash
reqs_failed=false

die() { printf %s "${@+$@$'\n'}" ; exit 1; }

require_python_version_major=2
require_python_version_minor=6
# check the version of python available
printf "    Python $require_python_version_major.$require_python_version_minor required... "
if python -c "import sys; exit(1) if sys.version_info.major != $require_python_version_major else exit(1) if sys.version_info.minor != $require_python_version_minor else exit(0)"; then
    echo "OK, found it."
else
    echo "NOT FOUND! Install it and try again."
    reqs_failed=true
fi

# check that virtualenv is available
printf "    virtualenv required... "
if virtualenv --version > /dev/null; then
    echo "OK, found it."
else
    echo "NOT FOUND! Install it and try again."
    reqs_failed=true
fi

# check that elasticsearch is working
printf "    Elasticsearch needs to be running... "
if curl http://localhost:9200 > /dev/null 2>&1; then
    echo "OK, found it."
else
    echo "NOT FOUND! Install it, run it and try again."
    reqs_failed=true
fi

if $reqs_failed; then
    echo
    echo "Looks like some requirements weren't satisfied. Try these commands (tested on Ubuntu Linux 12.04):"
    echo
    echo "    sudo apt-get install python virtualenv"
    echo "    sudo service elasticsearch restart"
    echo
    echo "and re-run this script."
    echo "NOTE: you have to install elasticsearch manually if you don't have it! It's not in the Debian repos yet."
    die
fi

cd /opt || die "Er, your /opt directory does not exist. Set up your server first."
sudo ls > /dev/null || die "Can't sudo for some reason, do it yourself or fix sudo."
if [ -d /opt/doaj ]; then
    die "/opt/doaj already exists. If you want to set up DOAJ again, make sure there's nothing valuable in /opt/doaj and rm -rf it, then run this script again."
fi
sudo mkdir doaj
sudo chown cloo:cloo doaj
virtualenv doaj # will set up with the "python" executable, whatever that is according to current $PATH
                # also does --no-site-packages by default, so no need to specify explicitly here
cd doaj
. bin/activate
mkdir src
cd src/
git clone https://github.com/DOAJ/doaj.git
cd doaj/
git submodule init
git submodule update
cd /opt
sudo mkdir sysadmin
sudo chown cloo:cloo sysadmin/
git clone https://github.com/CottageLabs/sysadmin.git
cd sysadmin/
git pull
echo
echo
echo "Not replacing your main supervisord configuration file. However, check if it's set up the way you want it."
echo "Run this to see if there are any differences between the supervisord config in the sysadmin repo and the one on this machine:"
echo
echo "    diff -u /etc/supervisor/supervisord.conf /opt/sysadmin/config/supervisor/supervisord.conf"
echo
echo
printf "Copying all supervisord application configuration files... "
sudo cp -r config/supervisor/conf.d/doaj* /etc/supervisor/conf.d/
echo "done."
echo
cd /opt/doaj/src/doaj/
# install lxml
sudo apt-get update > /dev/null
echo "Installing lxml, handing off to apt-get now..."
echo
sudo apt-get install libxml2-dev libxslt-dev
echo
echo "Done trying to install lxml, proceeding with installing Python-based requirements."
echo
pip install -e .
pip install gunicorn
echo
echo
sudo supervisorctl reread || die "Couldn't reread the supervisord config. Do you have supervisord? Install it if not."
sudo supervisorctl update || die "Couldn't run the new process groups in supervisord. Sorry, no idea why. Run sudo supervisorctl update and see the errors."
echo
sudo supervisorctl status
cat << EOF

All done. The supervisord status command output you just saw should look
something like this:

doaj                              RUNNING    pid 5958, uptime 0:01:14

    You can test the app by requesting the homepage:
    curl localhost:5050
EOF
