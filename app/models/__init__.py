class Model:
    def __init__(self, *args, **kwargs):
        pass

    def fetch_related_models(self, db):
        return

    async def save(self, db):
        raise NotImplementedError()

    @staticmethod
    async def get_by_id(db, object_id):
        raise NotImplementedError()

    @staticmethod
    async def get_list(db, **kwargs):
        raise NotImplementedError()

    @staticmethod
    async def get_count(db, **kwargs):
        raise NotImplementedError()
