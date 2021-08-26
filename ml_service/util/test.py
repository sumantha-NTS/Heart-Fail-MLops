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
            20, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
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
print(resp.text)
