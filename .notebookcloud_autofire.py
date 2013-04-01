#!/usr/bin/python

# NotebookCloud: Our Script for the User's Server

# Uses Python2.7

# Author: Carl Smith, Piousoft
# MailTo: carl.input@gmail.com

import os, sys, urlparse, urllib, server

PEM_PATH = '/home/ubuntu/.ipython/profile_nbserver/cert.pem'

# get this instance's user data and convert it to a list
user_data = urllib.urlopen('http://169.254.169.254/latest/user-data').read()
user_data = user_data.split('|')

nb_url = user_data.pop() if len(user_data) == 7 else None

# exit here if this instance was started without valid user data
if len(user_data) != 6: sys.exit()
    
try: # see if the server is configured yet

    test = open(PEM_PATH, 'r')
    test.close()

except: # if not, we'll try and configure it
    
    from OpenSSL import crypto, SSL
    from socket import gethostname
        
    # get the password, which is hashed before it is sent
    password = user_data.pop()

    # create the config file
    config_code = (
    "c = get_config()\n"
    "c.IPKernelApp.pylab = 'inline'\n"
    "c.NotebookApp.certfile = u'%s'\n"
    "c.NotebookApp.ip = '*'\n"
    "c.NotebookApp.open_browser = False\n"
    "c.NotebookApp.password = u'{0}'\n"
    "c.NotebookApp.port = 8888\n"
    )  % PEM_PATH
    config_file = '/home/ubuntu/.ipython/profile_nbserver/ipython_notebook_config.py'
    open(config_file, 'w').write(config_code.format(password))

    # create a key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 1024)

    # create a self-signed certificate using random data
    # provided in the userdata string
    cert = crypto.X509()
    cert.get_subject().C = user_data[0]
    cert.get_subject().ST = user_data[1]
    cert.get_subject().L = user_data[2]
    cert.get_subject().O = user_data[3]
    cert.get_subject().OU = user_data[4]
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha1')

    # turn key and cert into a couple of strings and flush it to a file
    key  = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
    cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
    open(PEM_PATH, 'w').write(key + cert)

# fetch notebook if we haven't already
if nb_url and not os.path.exists('/home/ubuntu/notebooks'):
    try:
        server.system('/usr/bin/git ls-remote %s' % nb_url)
        server.system('/usr/bin/git clone %s /home/ubuntu/notebooks' % nb_url)
    except Exception, err:
        server.serve_text(8888, err, 500, PEM_PATH)
        # never return

# now fire it all up
if not os.path.exists('/home/ubuntu/notebooks'):
    os.mkdir('/home/ubuntu/notebooks')
os.chdir('/home/ubuntu/notebooks')
os.system('ipython notebook --profile=nbserver')
