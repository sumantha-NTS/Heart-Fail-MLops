import requests
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


def main():
    allowSelfSignedHttps(True)
    parser = argparse.ArgumentParser("smoke_test_scoring_service.py")

    parser.add_argument(
        "--type",
        type=str,
        choices=["AKS", "ACI", "Webapp"],
        required=True,
        help="type of service"
    )
    parser.add_argument(
        "--service",
        type=str,
        required=True,
        help="Name of the image to test"
    )
    args = parser.parse_args()
    print('success', args)

    e = Env()

    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )
    service = AciWebservice(aml_workspace, args.service)
    # URL for the web service
    scoring_uri = service.scoring_uri

    # If the service is authenticated, set the key or token
    service_keys = service.get_keys()
    key = service_keys[0]

    # Two sets of data to score, so we get two results back
    data = {"data":
            [
                [0.636, 0, 0.071, 0, 0.09, 1, 0.29, 0.157, 0.4857, 1, 0, 0]
            ]
            }
    # Convert to JSON string
    input_data = json.dumps(data)

    # Set the content type
    headers = {'Content-Type': 'application/json'}
    # If authentication is enabled, set the authorization header
    headers['Authorization'] = f'Bearer {key}'

    # Make the request and display the response
    resp = requests.post(scoring_uri, input_data, headers=headers)
    print(resp)
    print(resp.text)
