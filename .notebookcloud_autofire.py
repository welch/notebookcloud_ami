#!/usr/bin/python

# NotebookCloud: Our Script for the User's Server

# Uses Python2.7

# Author: Carl Smith, Piousoft
# MailTo: carl.input@gmail.com

import os, sys

try: # see if the server is configured yet

    test = open('/home/ubuntu/.ipython/profile_nbserver/cert.pem', 'r')
    test.close()

except: # if not, we'll try and configure it
    
    from urllib import urlopen
    from OpenSSL import crypto, SSL
    from socket import gethostname

    # get this instance's user data and convert it to a list
    user_data = urlopen('http://169.254.169.254/latest/user-data').read()
    user_data = user_data.split('|')

    # exit here if this instance was started without valid user data
    if len(user_data) != 6:
        sys.exit()

    # get the password, which is hashed before it is sent
    password = user_data.pop()

    # create the config file
    config_code = (
    "c = get_config()\n"
    "c.IPKernelApp.pylab = 'inline'\n"
    "c.NotebookApp.certfile = u'/home/ubuntu/.ipython/profile_nbserver/cert.pem'\n"
    "c.NotebookApp.ip = '*'\n"
    "c.NotebookApp.open_browser = False\n"
    "c.NotebookApp.password = u'{0}'\n"
    "c.NotebookApp.port = 8888\n"
    )
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
    open('/home/ubuntu/.ipython/profile_nbserver/cert.pem', 'w').write(key + cert)


# now fire it all up
os.chdir('/home/ubuntu/notebooks')
os.system('ipython notebook --profile=nbserver')
