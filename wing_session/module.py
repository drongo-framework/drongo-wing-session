from drongo.utils import dict2

import uuid


class Session(object):
    def __init__(self, app, **config):
        self.app = app

        config = dict2.from_dict(config)
        self.cookie_name = config.get('cookie_name', '_drongo_sessid')
        self.session_var = config.get('session_var', 'session')

        # Load and configure the session storage
        storage = config.get('storage', 'filesystem')
        self.storage = None

        if storage == 'filesystem':
            from .storage._filesystem import Filesystem
            path = config.get('session_path', './.sessions')
            self.storage = Filesystem(path=path)

        elif storage == 'mongo':
            from .storage._mongo import Mongo
            database_module = config.modules.database
            collection = config.get('collection', 'session')
            self.storage = Mongo(
                collection=database_module.instance.get_collection(collection))

        elif storage == 'redis':
            from .storage._redis import Redis
            database_module = config.modules.database
            db = database_module.instance.get()
            self.storage = Redis(db=db)

        app.add_middleware(self)

    def before(self, ctx):
        sessid = ctx.request.cookies.get(self.cookie_name)
        if sessid is None:
            sessid = uuid.uuid4().hex
        if self.storage:
            ctx[self.session_var] = self.storage.load(sessid)

    def after(self, ctx):
        if self.storage:
            self.storage.save(ctx[self.session_var])
            ctx.response.set_cookie(
                self.cookie_name, ctx[self.session_var]._sessid)
