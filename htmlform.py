#!/usr/bin/python
"""
Utilities for developing with HTMLFormEntry including:

- Tooling to assemble HTML Forms from HTML, JS, and CSS split in to multiple
  files.
- Tooling to upload HTML Forms to an external server so you don't have to 
  cut and paste them in to your browser.
"""
import ConfigParser
import getpass
import httplib2
import keyring
import os
import sys
import urllib

disable_ssl_certificate_validation = True

def get_settings():
    config_file = os.path.expanduser('~/.openmrs-logins.cfg')
    config = ConfigParser.SafeConfigParser({
            'username':'',
            'serverprefix':'',
            })
    config.read(config_file)
    if not config.has_section('openmrs_form_server'):
        config.add_section('openmrs_form_server')

    username = config.get('openmrs_form_server','username')
    serverprefix = config.get('openmrs_form_server','serverprefix')
    password = None

    if username != '' and serverprefix != '':
        password = keyring.get_password('openmrs_form_server',username)
        
    if password == None: # or not auth(username,password) <- random auth test function
        serverprefix = raw_input("Forms Server Prefix:\n")
        username = raw_input("Username:\n")
        password = getpass.getpass("Password:\n")
        config.set('openmrs_form_server','username',username)
        config.set('openmrs_form_server','serverprefix',serverprefix)
        config.write(open(config_file,'w'))
        keyring.set_password('openmrs_form_server',username,password)

    return [username,password,serverprefix]

def assemble_form(markup,formfilename,css=[],js=[]):
    out = open(formfilename,'w')
    out.write("<htmlform>")
    for csspath in css:
        out.write('<style type="text/css" media="screen">')
        cssfile = open(csspath)
        out.write(cssfile.read())
        cssfile.close()
        out.write('</style>')
    alljs = ['/home/sgithens/code/openmrs-scripts/standard-htmlform.js']
    alljs.extend(js)
    for jspath in alljs:
        out.write('<script type="text/javascript">')
        jsfile = open(jspath)
        out.write(jsfile.read())
        jsfile.close()
        out.write('</script>')
    out.write(markup)
    out.write("</htmlform>")
    out.close()

def assemble_viaform():
    prefix = '/home/sgithens/code/via-form-dev/'
    mfile = open(prefix+"via-markup.html")
    markup = mfile.read()
    mfile.close()
    assemble_form(markup,prefix+"viaform.html",[prefix+"via-css.css"],[prefix+"via-js.js"])

def upload_viaform():
    prefix = '/home/sgithens/code/via-form-dev/'
    main(['19',prefix+"viaform.html"])

def main(args):
    uname,passwd,serverprefix = get_settings()
    formid = args[0]
    file = args[1]
    f = open(file)
    h = httplib2.Http(disable_ssl_certificate_validation=disable_ssl_certificate_validation)
    data = {'uname':uname,'pw':passwd}
    body = urllib.urlencode(data)
    resp, content = h.request(serverprefix+"/loginServlet", method="POST", body=body, headers={'Content-type': 'application/x-www-form-urlencoded'})
    print resp
    headers = {'Cookie': resp['set-cookie'], 'Content-type': 'application/x-www-form-urlencoded'}
    htmlFormData = {
        'xmlData': f.read()
    }
    f.close()
    resp, content = h.request(serverprefix+"/module/htmlformentry/htmlForm.form?id="+formid, headers=headers, method="POST", body=urllib.urlencode(htmlFormData))
    print content
    print resp


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "assemble":
        assemble_viaform()
        upload_viaform()
    else:
        main(sys.argv[1:])

