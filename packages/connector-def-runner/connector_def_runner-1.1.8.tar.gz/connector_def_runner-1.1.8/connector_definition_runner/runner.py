import os
import glob
import yaml
import json
import chevron
from requests import Session
from urllib.parse import urljoin
from .authenticate import Authenticate


class Runner(Authenticate):
    def __init__(self, action_name=None, context=None):
        self.asset_name = None
        self.action_name = action_name
        # Swimlane has context
        if context:
            self.asset = context.asset
            self.inputs = context.inputs
            self.endpoint = context.manifest['meta']['endpoint']
            self.method = context.manifest['meta']['method']
            self.security = context.manifest['meta']['security']
            self.asset_url_key = self.asset_manifest['meta'].get('asset_url_key', 'url')
        # Turbine
        else:
            # Data must load before the schemas, we need to determine which schema from the payload.
            self.asset, self.inputs = self._load_data()
            self.asset_manifest, self.action_manifest = self._load_schemas()
            self.security = self.asset_manifest.get('meta', {}).get('security', {})
            self.asset_url_key = self.asset_manifest.get('meta', {}).get('asset_url_key', 'url')

        # Build session
        self.session = WrappedSession()
        http_proxy = os.getenv('http_proxy') or self.asset.get('http_proxy')
        self.session.proxies = {
            'http_proxy': http_proxy,
            'https_proxy': http_proxy
        }
        self.session.verify = os.getenv('verify') or self.asset.get('verify', True)
        self.raise_for_status = os.getenv('raise_for_status') or self.asset.get('raise_for_status', True)
        self.session.headers.update(self.asset.get('headers', {}))

        super(Runner, self).__init__(
            session=self.session,
            asset=self.asset,
            security=self.security,
            asset_name=self.asset_name
        )

    def _get_asset_name(self):
        if {'username', 'password'} <= set(self.asset):
            return 'http_basic'
        elif {'token'} <= set(self.asset):
            return 'http_bearer'
        elif {'clientSecret', 'clientId', 'tokenUrl', 'scope'} <= set(self.asset):
            return 'oauth2_client_credentials'
        else:
            return 'apikey'

    def _load_schemas(self):

        self.asset_name = self._get_asset_name()

        manifests = glob.glob('./**/*.yaml', recursive=True)
        asset_manifest = None
        action_manifest = None
        for manifest in manifests:
            # All Swimlane connector schemas should have schema property.
            try:
                schema = yaml.safe_load(open(manifest).read())
                schema_type = schema['schema']
                if schema_type in ['asset/1'] and schema['name'] == self.asset_name:
                    asset_manifest = schema

                if schema_type in ['action/1'] and schema['name'] == self.action_name:
                    action_manifest = schema
            except:
                pass

        return asset_manifest, action_manifest

    @staticmethod
    def _load_data():
        inputs = json.loads(os.getenv('INPUTS', '{}'))
        asset = {}
        asset_keys = os.getenv('ASSET_KEYS', '').split(',')
        for k in inputs.keys():
            if k in asset_keys:
                asset[k] = inputs[k]
        for k in asset.keys():
            del inputs[k]

        return asset, inputs

    def _update_headers(self):
        self.session.headers.update(
            self.inputs.get('headers', {})
        )
        return

    def get_endpoint(self):
        # Mustache if available if not returns string as is.
        self.endpoint = chevron.render(self.action_manifest['meta']['endpoint'], self.inputs.get('path_parameters', {}))
        return self.endpoint

    def get_method(self):
        self.method = self.action_manifest['meta']['method']
        return self.method

    def get_kwargs(self):
        # todo can we handle files automatically.
        self.params.update(self.inputs.get('parameters', {}))
        return {
            'params': self.params,
            'data': self.inputs.get('data_body'),
            'json': self.inputs.get('json_body'),
        }

    def parse_response(self, response):
        try:
            json_body = response.json()
        except:
            json_body = {}

        # todo: can we handle files automatically?
        # todo: should we parse the raw http response? What format should we return. SPIKE

        return {
            'status_code': response.status_code,
            'response_headers': dict(response.headers),
            'data': json_body,
            'response_text': response.text,
            'reason': response.reason
        }

    def run(self):
        self._update_headers()
        response = self.session.request(
            method=self.get_method(),
            url=urljoin(self.asset[self.asset_url_key], self.get_endpoint()),
            **self.get_kwargs()
        )
        resp = self.parse_response(response)
        return resp


class WrappedSession(Session):
    """A wrapper for requests.Session to override 'verify' property, ignoring REQUESTS_CA_BUNDLE environment variable.
    This is a workaround for https://github.com/kennethreitz/requests/issues/3829 (will be fixed in requests 3.0.0)
    Code sourced from user intgr https://github.com/kennethreitz/requests/issues/3829
    """

    def merge_environment_settings(self, url, proxies, stream, verify, *args, **kwargs):
        if self.verify is False:
            verify = False

        return super(WrappedSession, self).merge_environment_settings(url, proxies, stream, verify, *args, **kwargs)