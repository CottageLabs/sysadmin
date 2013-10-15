#! /usr/bin/python

import smtplib, socket, requests
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate


# a script to GET a bunch of server IPs and domain names and send an email 
# about their status. Should be set to run, say, every 10 mins with anacron
# or similar, on multiple servers. Note that requests needs to be installed.


# edit the following two lists to add server IPs and domain names to the tests
# a status code of 200 OK is expected from each of these, so make sure they 
# are configured to return that in normal operation (e.g. make sure your nginx 
# config returns a valid response for the IPs / domains
servers = [
    'http://46.235.224.100', # our main CL server, cottage
    'http://93.93.131.120', # Marks test server, cottaget, test.cottagelabs.com
    'http://46.235.224.107', # prod server cottagep1, arttactic, leaps, swap
    'http://93.93.131.239' # prod server cottaget2, oag
]


domains = [
    'http://cottagelabs.com',
    'http://pads.cottagelabs.com',
    'http://oag.cottagelabs.com',
    'http://artforecaster.com',
    'http://leapssurvey.org',
    'http://swapsurvey.org',
    'http://ifthisistheanswer.com'
]

# use this ignore list if you want to temporarily ignore one of the above, 
# but you don't want to remove it from record
ignore = [
]

# set this to true if you always want a status email sent, regardless of state
# otherwise a status email will only come when there is an error
send_msg = False


# NO MORE CONFIG BEYOND HERE ================================================= #


# get the IP of the machine running this test
this_machine = False
try:
    f = open('this_machine','r')
    this_machine = f.read()
    f.close()
except:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    this_machine = s.getsockname()[0]
    s.close()
    try:
        f = open('this_machine','w')
        f.write(this_machine)
        f.close()
    except:
        pass


# defaults
no_response = []
subject = "all is well with servers and domains"
text = "Tested the following:\n\n"
if this_machine:
    text = "This test was run on machine " + this_machine + '\n\n' + text
    subject = this_machine + " says " + subject


# check each server / domain
for addr in servers + domains:
    if addr not in ignore:
        text += addr + '\n'

        # if no response, add it to the no_response list
        try:
            r = requests.get(addr)
            if r.status_code != 200:
                no_response.append(addr)
        except:
            no_response.append(addr)


# if one did not respond, update and trigger the message
if len(no_response) != 0:
    send_msg = True
    subject = "ALL IS NOT WELL WITH "
    if this_machine:
        subject = this_machine + " SAYS " + subject
    text += '\n\nAND THESE ONES FAILED TO RESPOND\n\n'    
    text += '\n'.join(no_response)
    subject += ', '.join(no_response)


# send the message
if send_msg:
    try:
        fro = "us@cottagelabs.com"
        to = ["us@cottagelabs.com"]

        msg = MIMEMultipart()
        msg['From'] = fro
        msg['To'] = COMMASPACE.join(to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach( MIMEText(text) )

        smtp = smtplib.SMTP("localhost")
        smtp.sendmail(fro, to, msg.as_string() )
        smtp.close()
    except:
        # TODO: could update this with a note in a local log file, 
        # if local logging is done
        print "mailing failed"
        print subject
        print text
else:
    # TODO: if local logging is done, could record that the tests were done
    # and what their outcome was, even if sending a message was unrequired
    print subject
    print text
        
        
# TODO: if local logging is required, add some sort of local logging here




