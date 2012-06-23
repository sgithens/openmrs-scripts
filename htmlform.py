#!/usr/bin/python
"""
Utilities for developing with HTMLFormEntry including:

- Tooling to assemble HTML Forms from HTML, JS, and CSS split in to multiple
  files.
- Tooling to upload HTML Forms to an external server so you don't have to 
  cut and paste them in to your browser.
"""
import ConfigParser
import Cookie
import getpass
import httplib2
import keyring
import os
import sys
import urllib
import uuid

disable_ssl_certificate_validation = True


class OpenMRSConnection(object):
    """Class to model and hold session for OpenMRS HTTP calls"""
    
    def __init__(self, serverprefix, uname, passwd):
        """Connect and set up session information"""
        self.h = httplib2.Http(disable_ssl_certificate_validation=disable_ssl_certificate_validation)
        self.serverprefix = serverprefix
        data = {'uname':uname,'pw':passwd}
        body = urllib.urlencode(data)
        resp, content = self.h.request(serverprefix+"/loginServlet", method="POST", body=body, headers={'Content-type': 'application/x-www-form-urlencoded'})
        self.cookie = resp['set-cookie']
        c = Cookie.SimpleCookie()
        c.load(self.cookie)
        self.jsessionid = c['JSESSIONID'].value        

    def post_form(self, path, bodydict):
        """Make a POST request to the server that takes a standard Form encoded body."""
        headers = {'Cookie': self.cookie, 'Content-type': 'application/x-www-form-urlencoded'}        
        resp, content = self.h.request(self.serverprefix+path, headers=headers, method="POST", body=urllib.urlencode(bodydict))
        return resp,content

    def post_text(self, path, body):
        headers = {'Cookie': self.cookie, 'Content-type': 'text/plain'}        
        resp, content = self.h.request(self.serverprefix+path, headers=headers, method="POST", body=body)
        return resp,content


cur_settings_key = "openmrs_form_server"
def get_settings():
    config_file = os.path.expanduser('~/.openmrs-logins.cfg')
    config = ConfigParser.SafeConfigParser({
            'username':'',
            'serverprefix':'',
            })
    config.read(config_file)
    if not config.has_section(cur_settings_key):
        config.add_section(cur_settings_key)

    username = config.get(cur_settings_key,'username')
    serverprefix = config.get(cur_settings_key,'serverprefix')
    password = None

    if username != '' and serverprefix != '':
        password = keyring.get_password(cur_settings_key,username)
        
    if password == None: # or not auth(username,password) <- random auth test function
        serverprefix = raw_input("Forms Server Prefix:\n")
        username = raw_input("Username:\n")
        password = getpass.getpass("Password:\n")
        config.set(cur_settings_key,'username',username)
        config.set(cur_settings_key,'serverprefix',serverprefix)
        config.write(open(config_file,'w'))
        keyring.set_password(cur_settings_key,username,password)

    return [username,password,serverprefix]

def get_default_omrs():
    "Fetches an OpenMRSConnection based on the settings we have in our ini file."
    uname,passwd,serverprefix = get_settings()
    return OpenMRSConnection(serverprefix,uname,passwd)

entity_ordering = ["&","<",">"]
entity_mapping = {
    "&": "&#38;",
    "<": "&#60;",
    ">": "&#62;",
}

def assemble_form(markup,formfilename,css=[],js=[]):
    out = open(formfilename,'w')
    out.write("<htmlform>")
    for csspath in css:
        out.write('<style type="text/css" media="screen">')
        cssfile = open(csspath)
        out.write(cssfile.read())
        cssfile.close()
        out.write('</style>')
    alljs = ['/home/sgithens/code/openmrs-scripts/standard-htmlform.js','/home/sgithens/code/openmrs-scripts/obsdatetime.js']
    alljs.extend(js)
    for jspath in alljs:
        out.write('<script type="text/javascript">')
        jsfile = open(jspath)
        jscode = jsfile.read()
        for char in entity_ordering:
            ascii = entity_mapping[char]
            jscode = jscode.replace(char,ascii)
        out.write(jscode)
        jsfile.close()
        out.write('</script>')
    out.write(markup)
    out.write("</htmlform>")
    out.close()

def assemble_dysplasiaform():
    prefix = '/home/sgithens/code/via-form-dev/'
    mfile = open(prefix+"dysplasia-markup.html")
    markup = mfile.read()
    mfile.close()
    assemble_form(markup,prefix+"dysplasia-form.html",[prefix+"via-css.css"],[prefix+"via-js.js"])

def assemble_test():
    prefix = '/home/sgithens/code/via-form-dev/'
    mfile = open(prefix+"test-markup.html")
    markup = mfile.read()
    mfile.close()
    assemble_form(markup,prefix+"test-form.html",[prefix+"via-css.css"],[prefix+"via-js.js"])


def upload_dysplasiaform():
    prefix = '/home/sgithens/code/via-form-dev/'
    main(['21',prefix+"dysplasia-form.html"])


def assemble_viaform():
    prefix = '/home/sgithens/code/via-form-dev/'
    mfile = open(prefix+"via-markup.html")
    markup = mfile.read()
    mfile.close()
    assemble_form(markup,prefix+"viaform.html",[prefix+"via-css.css"],[prefix+"via-js.js"])

def run_groovy_file(filepath):
    f = open(filepath)
    script = f.read()
    f.close()
    return run_groovy_script(script)

def run_groovy_script(scripttext):
    """ POST Payload looks like:
    callCount=1
    page=/openmrs/module/groovy/groovy.form
    httpSessionId=323CD7286B3DC8601A7B8A08FE227524
    scriptSessionId=369BBB29FDD7E3ACC008C9CFF5AC0AAE615
    c0-scriptName=DWRGroovyService
    c0-methodName=eval
    c0-id=0
    c0-param0=string:println%20%22Hello%20wow%22%0Aprintln%20%22What%202%22%0A
    batchId=1
    """
    openmrsconn = get_default_omrs()
    data = """callCount=1
page=/openmrs/module/groovy/groovy.form
httpSessionId="""+openmrsconn.jsessionid+"""
scriptSessionId="""+str(uuid.uuid1())+"""
c0-scriptName=DWRGroovyService
c0-methodName=eval
c0-id=0
batchId=1
"""+urllib.urlencode([("c0-param0","string:"+scripttext)])

    resp, content = openmrsconn.post_text("/dwr/call/plaincall/DWRGroovyService.eval.dwr",data)
    stuff = content[content.find('[')+9:-8]
    stuff = stuff.replace("\\n","\n")
    print stuff
      
    

def upload_viaform():
    prefix = '/home/sgithens/code/via-form-dev/'
    main(['19',prefix+"viaform.html"])

def main(args):
    formid = args[0]
    file = args[1]
    f = open(file)
    htmlFormData = {
        'xmlData': f.read()
    }
    f.close()
    openmrsconn = get_default_omrs()
    resp, content = openmrsconn.post_form("/module/htmlformentry/htmlForm.form?id="+formid,htmlFormData)

    print content
    print resp
    print openmrsconn.cookie

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "assemble" and sys.argv[2] == "via":
        print("Building uploading VIA form")
        assemble_viaform()
        upload_viaform()
    elif len(sys.argv) > 2 and sys.argv[1] == "assemble" and sys.argv[2] == "dysplasia":
        print("Building and uploading dysplasia form.")
        assemble_dysplasiaform()
        upload_dysplasiaform()
    elif len(sys.argv) > 2 and sys.argv[1] == "assemble" and sys.argv[2] == "test":
        print("Building and uploading dysplasia form.")
        assemble_test()
    elif len(sys.argv) > 1 and sys.argv[1] == "groovy":
        print("Going to upload and run the groovy script 2")
        cur_settings_key = 'localhost'
        print(run_groovy_file('/home/sgithens/code/IeDEA/prototype.groovy'))
    else:
        print("Doing upload with switches")
        main(sys.argv[1:])

