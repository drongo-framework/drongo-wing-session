from .common import DEFAULT

from bson.objectid import ObjectId
from datetime import datetime

import pickle


class Mongo(object):
    def __init__(self, **config):
        self.collection = config.get('collection')

    def _create_session(self):
        return str(self.collection.insert_one({'value': DEFAULT}).inserted_id)

    def load(self, session_id):
        try:
            sess = self.collection.find_one(dict(_id=ObjectId(session_id)))
        except Exception:
            sess = None

        if sess is None:
            sess = {'value': DEFAULT}
            session_id = self._create_session()

        session = pickle.loads(sess['value'])
        session._sessid = session_id

        return session

    def save(self, session):
        session_id = session._sessid or self._create_session()
        self.collection.update_one(dict(_id=ObjectId(session_id)), {
            '$set': {
                'value': pickle.dumps(session),
                'last_updated': datetime.utcnow()
            }
        })
