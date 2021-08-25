import urllib.request
import json
import os
import ssl
import argparse
from azureml.core import Workspace
from azureml.core.webservice import AciWebservice
from ml_service.util.env_variables import Env


def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') \
            and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context


allowSelfSignedHttps(True)

parser = argparse.ArgumentParser("test_scoring")

parser.add_argument(
    "--service",
    type=str,
    required=True,
    help="Name of the image to test"
)
args = parser.parse_args()

e = Env()

aml_workspace = Workspace.get(
    name=e.workspace_name,
    subscription_id=e.subscription_id,
    resource_group=e.resource_group
)

service = AciWebservice(aml_workspace, args.service)

service_keys = service.get_keys()

# Request data goes here
data = {"data":
         [
           {
             "age": "17",
             "aneamia": '1'
           }
       ]
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
