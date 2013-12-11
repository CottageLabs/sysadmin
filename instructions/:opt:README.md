We're running supervisord on our server. Every time you push changes, do

    git pull  # or git clone https://github.com/DOAJ/doaj.git if deploying for the first time - replace URL as needed
    git submodule init  # if this is the first time you're deploying the app, but won't hurt if it's not
    git submodule update  # in case one of the repo's submodules are at a newer commit now
    sudo supervisorctl restart doaj  # replace doaj with the supervisor name of your app

If you want a list of what's under supervisor, do

    sudo supervisorctl status

All supervisord log files are under /var/log/supervisor/

Web apps often write their logs to the ERROR log (so e.g. doaj-error.log)
because ET hasn't had time to figure out why and fix it. So check the
error log if the access one is empty.
