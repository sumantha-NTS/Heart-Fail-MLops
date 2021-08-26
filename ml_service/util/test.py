import requests
import json

# URL for the web service
scoring_uri = 'http://cef2dcc6-dd7d-4aad-9592-1af3241a6aad.'\
    'centralus.azurecontainer.io/score'
# If the service is authenticated, set the key or token
key = 'hXUbDlRKUzMh3e5RWLqEwKlQk2Y921WJ'

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
