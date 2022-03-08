#Strava authentication process
def strava_authentication(self):
    param = {
        'client_id': self.client_id,
        'redirect_uri': self.redirect_uri,
        'approval_prompt': 'auto',
        'response_type': 'code',
        'scope': 'activity:read_all'
    }
    # Make authentication url
    url = "https://www.strava.com/oauth/authorize?" + urlencode(param)
    # Open webbrowser
    webbrowser.get().open(url)
    # User needs to approve access and copy code
    #Example of code: 'd4ffc7c2c190d1b8db88037a5d25a2b63ece2ae8'
    code = str(input('Input the code here: '))
    payload = {
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }
    # Request for a new more "permanent" access token
    self.access_token = requests.post("https://www.strava.com/oauth/token", params = payload).json()['access_token']