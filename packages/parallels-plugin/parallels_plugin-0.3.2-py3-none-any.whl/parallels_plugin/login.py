import os
import sys
import getpass
import json
from urllib.parse import urlparse
import urllib
import requests
from requests.exceptions import HTTPError
import time

def tokfile_name():
    return os.path.join(os.path.expanduser("~"), ".mlflow-parallels", "token")

def write_token_file(tokfile, token_time, token, refresh_token, idToken, client_id):
    os.makedirs(os.path.dirname(tokfile), exist_ok=True)
    with open(tokfile, 'w') as wfile:
        wfile.write("Token=" + token + "\n")
        wfile.write("RefreshToken=" + refresh_token + "\n")
        wfile.write("TokenTimeEpochSeconds=" + str(token_time) + "\n")
        wfile.write("IdToken=" + idToken + "\n")
        wfile.write("ClientId=" + client_id + "\n")
        wfile.close()

def get_creds():
    if sys.stdin.isatty():
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    else:
        username = sys.stdin.readline().rstrip()
        password = sys.stdin.readline().rstrip()
    return username, password

def login_and_update_token_file(cognito_client_id, cognito_callback_url,
        cognito_domain, region, is_external_auth):
    tokfile = tokfile_name()
    if is_external_auth:
        oauth2_authorize_url = f"https://{cognito_domain}.auth.{region}.amazoncognito.com/oauth2/authorize?redirect_uri={urllib.parse.quote_plus(cognito_callback_url)}&response_type=code&state=uxZCvnJk33cDTIoFhT2yxo846Rdj7Q&access_type=offline&prompt=select_account&client_id={cognito_client_id}"

        auth_code = input(f"Enter this URL in a browser and obtain a code: {oauth2_authorize_url}\n  Enter the obtained code here: ")
        
        # get the auth2 access token url based on the service dasshboard url
        oauth2_token_url = f"https://{cognito_domain}.auth.{region}.amazoncognito.com/oauth2/token"
        # do not urlencode the redirect_uri using urllib.parse.quote_plus():  the post call automatically does this..
        response:requests.Response = requests.post(oauth2_token_url, data={"grant_type":"authorization_code", "client_id":cognito_client_id, "code":auth_code, 'redirect_uri': cognito_callback_url})
        
        authres = response.json()
        idToken = authres['id_token']
        accessToken = authres['access_token']
        refresh_token = authres['refresh_token']
        
        # refresh the token.
        response:requests.Response = requests.post(oauth2_token_url, data={"grant_type":"refresh_token", "client_id":cognito_client_id, "refresh_token":refresh_token})
        accessToken = authres['access_token']
        refresh_token = authres['refresh_token']
    else:
        username, password = get_creds()
        postdata = dict()
        auth_parameters = dict()
        auth_parameters['USERNAME'] = username
        auth_parameters['PASSWORD'] = password
        postdata['AuthParameters'] = auth_parameters
        postdata['AuthFlow'] = "USER_PASSWORD_AUTH"
        postdata['ClientId'] = cognito_client_id
        payload = json.dumps(postdata)
        url = 'https://cognito-idp.' +region +'.amazonaws.com:443/'
        headers = {
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
                }

        try:
            response:requests.Response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        
        authres = response.json()['AuthenticationResult']
        idToken = authres['IdToken']
        accessToken = authres['AccessToken']
        refresh_token = authres['RefreshToken']
        
        ##Refresh token once############################
        postdata = dict()
        auth_parameters = dict()
        auth_parameters['REFRESH_TOKEN'] = refresh_token
        postdata['AuthParameters'] = auth_parameters
        postdata['AuthFlow'] = "REFRESH_TOKEN_AUTH"
        postdata['ClientId'] = cognito_client_id

        payload = json.dumps(postdata)

        url = 'https://cognito-idp.' +region +'.amazonaws.com:443/'
        headers = {
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
                }

        try:
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

        authres = response.json()['AuthenticationResult']
        idToken = authres['IdToken']
        accessToken = authres['AccessToken']

    token_time = int(time.time())
    write_token_file(tokfile, token_time, accessToken, refresh_token, idToken, cognito_client_id)

def read_token_file(tokfile):
    ftoken = None
    frefresh_token = None
    ftoken_time = None
    token_type = None
    id_token = None
    with (open(tokfile)) as fp:
        for count, line in enumerate(fp):
            if (line.startswith('Token=')):
                ftoken = line[len('Token='):].rstrip()
            if (line.startswith('RefreshToken=')):
                frefresh_token = line[len('RefreshToken='):].rstrip()
            if (line.startswith('TokenTimeEpochSeconds=')):
                ftoken_time = int(line[len('TokenTimeEpochSeconds='):].rstrip())
            if (line.startswith('TokenType=')):
                token_type = line[len('TokenType='):].rstrip()
            if (line.strip().lower().startswith('idtoken=')):
                id_token = line.split('=')[1].strip()
    if (token_type == None):
        if (ftoken != None and ftoken.startswith('Custom ')):
            token_type = 'Custom'
        else:
            token_type = 'Bearer'
    return ftoken, frefresh_token, ftoken_time, token_type, id_token

def renew_token(region, tokfile, refresh_token, client_id):
    payload = "{\n"
    payload += "    \"AuthParameters\" : {\n"
    payload += "        \"REFRESH_TOKEN\" : \"" + refresh_token + "\"\n"
    payload += "    },\n"
    payload += "    \"AuthFlow\" : \"REFRESH_TOKEN_AUTH\",\n"
    payload += "    \"ClientId\" : \"" + client_id + "\"\n"
    payload += "}\n"

    url = 'https://cognito-idp.' +region +'.amazonaws.com:443/'

    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
            }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred while trying to renew token: {http_err}')
        raise
    except Exception as err:
        print(f'Other non http error occurred while trying to renew token: {err}')
        raise
    else:
        authres = response.json()['AuthenticationResult']
        token = authres['AccessToken']
        idToken = authres['IdToken']        
        token_time = int(time.time())
        write_token_file(tokfile, token_time, token, refresh_token, idToken, client_id)

def get_token(client_id, region, force_renew):
    token = None
    refresh_token = None
    token_time = None
    tokfile = tokfile_name()

    token, refresh_token, token_time, token_type, id_token = read_token_file(tokfile)
    if (token_type == "Custom"):
        return token

    if (force_renew == True):
        print("Forcing renewal of parallels token")
        renew_token(region, tokfile, refresh_token, client_id)
        token, refresh_token, token_time, token_type, id_token = read_token_file(tokfile)
        return token

    time_now = int(time.time())
    if ((token_time + (30 * 60)) < time_now):
        print('Parallels token has expired. Calling renew')
        renew_token(region, tokfile, refresh_token, client_id)
        token, refresh_token, token_time, token_type, id_token = read_token_file(tokfile)
        return token
    else:
        return token

def get_env_var():
    muri = os.getenv('MLFLOW_PARALLELS_URI')
    if not muri:
        raise Exception('Please set environment variable MLFLOW_PARALLELS_URI and try again')
    pmuri = urlparse(muri)
    if (pmuri.scheme.lower() != 'https'):
        raise Exception("Error: MLFLOW_PARALLELS_URI must be set to https://<mlflow_parallels_server>:<mlflow_parallels_port>/")
    return muri

def get_conf():
    cognito_client_id = None
    is_external_auth = None
    cognito_callback_url = None
    cognito_domain = None
    region = None

    muri = get_env_var()
    url = muri.rstrip('/') + '/api/2.0/mlflow/parallels/getversion'
    headers = { 'Authorization': 'None' }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        resp = response.json()
        cognito_client_id = resp['cognitoClientId']
        is_external_auth = resp['isExternalAuth']
        cognito_callback_url = resp['cognitoCallbackUrl']
        cognito_domain =  resp['cognitoDomain']
        region = resp['region']
    except HTTPError as http_err:
        print('Caught ' + str(http_err) + ' getting cognito client id')
        raise Exception('Caught ' + str(http_err) + ' getting cognito client id')
    except Exception as err:
        print('Caught ' + str(err) + ' getting cognito client id')
        raise Exception('Caught ' + str(err) + ' getting cognito client id')
    return cognito_client_id, is_external_auth, cognito_callback_url, cognito_domain, region

def login():
    cognito_client_id, is_external_auth, cognito_callback_url, cognito_domain, region = get_conf()
    login_completed = False
    try:
        token = get_token(cognito_client_id, region, True)
        print('Login completed')
        login_completed = True
    except Exception as err:
        pass

    if not login_completed:
        login_and_update_token_file(cognito_client_id,
                cognito_callback_url, cognito_domain, region, is_external_auth)
        try:
            token = get_token(cognito_client_id, region, False)
            print('Login completed')
            login_completed = True
        except Exception as err:
            raise
    return 0

if __name__ == "__main__":
    exit(login())
