import requests
import six
if six.PY2:
    import urlparse
else:
    import urllib
    urlparse = urllib.parse


class HTTPClient(object):
    def __init__(self, endpoint, auth_type=None, **kwargs):
        self.trailing_slash = kwargs.pop('trailing_slash', True)
        self.endpoint = endpoint
        self.auth_type = auth_type
        self._init_kwargs = kwargs

    def process_auth(self, kwargs):
        if self.auth_type is None:
            return
        if self.auth_type == 'basic':
            username = self._init_kwargs['auth_username']
            password = self._init_kwargs['auth_password']
            auth = (username, password)
            kwargs['auth'] = auth
            if 'auth' not in kwargs:
                kwargs['auth'] = auth
            return kwargs

        raise Exception('Not valid auth')

    def process_endpoint(self, kwargs):
        kwargs['url'] = urlparse.urljoin(self.endpoint, kwargs['url'])

    def request(self, method, url, **kwargs):
        if self.trailing_slash and url[-1] != '/':
            url = url + '/'
        kwargs.update({'method': method,
                       'url': url})
        self.process_auth(kwargs)
        self.process_endpoint(kwargs)
        req = requests.request(**kwargs)
        try:
            req.raise_for_status()
        except Exception as e:
            return self.handle_exception(e)
        if req.content:
            return req.json()

    def get(self, url, params=None, **kwargs):
        return self.request('get', url, params=params, **kwargs)

    def post(self, url, json=None, **kwargs):
        return self.request('post', url, json=json, **kwargs)

    def put(self, url, json=None, **kwargs):
        return self.request('put', url, json=json, **kwargs)

    def patch(self, url, json=None, **kwargs):
        return self.request('patch', url, json=json, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('delete', url, **kwargs)

    def handle_exception(self, exc):
        raise exc


class APIClient(object):
    client = None
    client_class = HTTPClient

    def __init__(self, **kwargs):
        self.client = self.client_class(**kwargs)

    def list(self, path, params, **kwargs):
        return self.client.get(path, params=params, **kwargs)

    def retrieve(self, path, key, **kwargs):
        url = '/'.join([path, str(key)])
        return self.client.get(url, **kwargs)

    def create(self, path, json, **kwargs):
        return self.client.post(path, json=json, **kwargs)

    def update(self, path, key, json, **kwargs):
        url = '/'.join([path, str(key)])
        return self.client.put(url, json=json, **kwargs)

    def partial_update(self, path, key, json, **kwargs):
        url = '/'.join([path, str(key)])
        return self.client.patch(url, json=json, **kwargs)

    def destroy(self, path, key, **kwargs):
        url = '/'.join([path, str(key)])
        return self.client.delete(url, **kwargs)

    def request(self, path, fun_path, key='', method='get', **kwargs):
        url = '/'.join([path, str(key), fun_path])
        return self.client.request(method, url, **kwargs)


class Resource(object):
    path = ''

    def __init__(self, apiclient, **kwargs):
        self.apiclient = apiclient

    def list(self, params={}, **kwargs):
        return self.apiclient.list(self.path, params, **kwargs)

    def retrieve(self, key, **kwargs):
        return self.apiclient.retrieve(self.path, key, **kwargs)

    def create(self, json, **kwargs):
        return self.apiclient.create(self.path, json, **kwargs)

    def destroy(self, key, **kwargs):
        return self.apiclient.destroy(self.path, key, **kwargs)

    def update(self, key, json, **kwargs):
        return self.apiclient.update(self.path, key, json, **kwargs)

    def partial_update(self, key, json, **kwargs):
        return self.apiclient.partial_update(self.path, key, json, **kwargs)
