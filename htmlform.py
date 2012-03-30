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
    main(sys.argv[1:])

