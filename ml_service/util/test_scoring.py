import urllib.request
import json
import os
import ssl
# from azureml.core import Workspace
from azureml.core.webservice import AciWebservice
# from ml_service.util.env_variables import Env


def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') \
            and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context


allowSelfSignedHttps(True)

ACI_DEPLOYMENT_NAME = 'mlops-aci-test_scoring'

aml_workspace = 'Heart_fail_ML'

service = AciWebservice(aml_workspace, ACI_DEPLOYMENT_NAME)

service_keys = service.get_keys()

# Request data goes here
data = {
    'age': '30',
    'anaemia': 'Yes'
}

body = str.encode(json.dumps(data))

url = service.scoring_uri
api_key = service_keys[0]  # Replace this with the API key for the web service
headers = {
    'Content-Type': 'application/json',
    'Authorization': ('Bearer ' + api_key)}

req = urllib.request.Request(url, body, headers)

try:
    response = urllib.request.urlopen(req)

    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print(
        "The request failed with status code: "
        + str(error.code))

    # Print the headers
    print(error.info())
    print(json.loads(error.read().decode("utf8", 'ignore')))
