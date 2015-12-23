import requests
import sys
import json
from MaltegoTransform import *


def main():
    mt = MaltegoTransform()
    ip = sys.argv[1]
    censys_uid = 'Enter_your_uid_here'
    censys_secret = 'Enter_your_censys_secret_here'
    auth = (censys_uid, censys_secret)
    query = {'query': 'ip: {ip}'.format(ip=ip), 'fields': ['443.https.tls.certificate.parsed.fingerprint_sha1',
                                                              '443.https.tls.certificate.parsed.issuer_dn',
                                                              '443.https.tls.certificate.parsed.subject_dn',
                                                              'updated_at']}
    try:
        request = requests.post('https://www.censys.io/api/v1/search/ipv4', data=json.dumps(query), auth=auth)
        if request.status_code == 200:
            results = request.json()
            if results['metadata']['count'] > 0:
                for result in results['results']:
                    sha1 = result['443.https.tls.certificate.parsed.fingerprint_sha1'][0]
                    issuer = result['443.https.tls.certificate.parsed.issuer_dn'][0]
                    subject = result['443.https.tls.certificate.parsed.subject_dn'][0]
                    updated = result['updated_at'][0]
                    sslcert = mt.addEntity("censys.sslcertificate", sha1)
                    sslcert.addAdditionalFields("property.issuer","Cert Issuer",True, issuer)
                    sslcert.addAdditionalFields("property.subject","Cert Subject",True, subject)
                    sslcert.addAdditionalFields("property.last_updated","Last updated time",True, updated)
                mt.returnOutput()
            else:
                mt.addUIMessage("No SSL certs were found on this ip: {ip}".format(ip=ip))
        if request.status_code == 400:
            results = request.json()
            mt.addUIMessage(str(results['error']))
        if request.status_code == 429:
            results = request.json()
            mt.addUIMessage(str(results['error']))
        if request.status_code == 404:
            mt.addUIMessage("No SSL certs were found on this ip: {ip}".format(ip=ip))
        if request.status_code == 500:
            mt.addUIMessage("There has been a server error!!!")

    except requests.exceptions.RequestException as e:
        mt.addUIMessage(str(e))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "User aborted."