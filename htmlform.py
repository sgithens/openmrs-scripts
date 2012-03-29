import httplib2
import sys
import urllib

#serverprefix="http://localhost:8081/openmrs-standalone"
serveruname=""
serverpasswd=""

disable_ssl_certificate_validation = True
def main(args):
    formid = args[0]
    file = args[1]
    f = open(file)
    h = httplib2.Http(disable_ssl_certificate_validation=disable_ssl_certificate_validation)
    data = {'uname':serveruname,'pw':serverpasswd}
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

