class BaseAuthentication(object):
    def __init__(self, request):
        self.request = request

    async def authenticate(self):
        raise NotImplementedError
