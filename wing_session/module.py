from wing_database import Database
from wing_module import Module

import uuid


class Session(Module):
    def init(self, config):
        self.cookie_name = config.get('cookie_name', '_drongo_sessid')
        self.session_var = config.get('session_var', 'session')

        # Load and configure the session storage
        database = config.modules.database

        if database.type == Database.MONGO:
            from .storage._mongo import Mongo

            collection = config.get('collection', 'session')
            self.storage = Mongo(
                collection=database.instance.get_collection(collection))

        elif database.type == Database.REDIS:
            from .storage._redis import Redis
            db = database.instance.get()
            self.storage = Redis(db=db)

        self.app.add_middleware(self)

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

    def get(self, ctx):
        return ctx[self.session_var]
