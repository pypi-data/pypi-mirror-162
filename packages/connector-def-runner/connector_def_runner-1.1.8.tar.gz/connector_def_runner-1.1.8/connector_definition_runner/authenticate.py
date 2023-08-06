class Authenticate:
    def __init__(self, session, asset, asset_name, security):
        self.session = session
        self.security = security
        self.asset = asset
        self.asset_name = asset_name
        self.params = {}

        self.auth_handler()

    def auth_handler(self):
        # The asset name is the name of the function which was set by the get_asset_name function.
        auth = getattr(self, self.asset_name)
        auth()

    def http_basic(self):
        self.session.auth = (self.asset['username'], self.asset['password'])
        return self.session

    def http_bearer(self):
        self.session.headers.update({
            'Authorization': f'Bearer {self.asset["token"]}'
        })
        return self.session

    def apikey(self):
        if self.security['in'] == 'header':
            self.session.headers.update({
                self.security['name']: self.asset[self.security['name']]
            })
        elif self.security['in'] == 'cookie':
            self.session.cookies.update({
                self.security['name']: self.asset[self.security['name']]
            })
        elif self.security['in'] == 'query':
            self.params.update({
                self.security['name']: self.asset[self.security['name']]
            })
        return self.session

    def oauth2_client_credentials(self):
        data = {
            'client_id': self.asset['client_id'],
            'client_secret': self.asset['client_secret'],
            'scope': self.asset.get('scopes', []).join(' '),
            'grant_type': 'client_credentials'
        }

        token_url = self.asset['token_url']
        access_token = self.session.request("POST", token_url, data=data).json()['access_token']

        self.session.headers.update({"Authorization": "Bearer {}".format(access_token)})
        return self.session
