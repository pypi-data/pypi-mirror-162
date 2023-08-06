# Inspiration: https://tinyurl.com/2am2r7ga
import abc


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def create_collection(self, collection, overwrite=True):
        raise NotImplementedError

    @abc.abstractmethod
    def drop_collection(self, collection):
        raise NotImplementedError

    @abc.abstractmethod
    def find(self, collection, query=None):
        raise NotImplementedError

    @abc.abstractmethod
    def insert(self, collection, records, return_result=False):
        raise NotImplementedError

    @abc.abstractmethod
    def drop(self, collection, query, return_result=False):
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, collection, query, new_vals, return_result=False):
        raise NotImplementedError


class MongoRepository(AbstractRepository):
    def __init__(self, client, db):
        self.client = client
        self.db = self.client[db]

    def create_collection(self, collection, overwrite=False):
        collections = self.db.list_collection_names()
        if collection not in collections:
            self.db.create_collection(collection)

        if (collection in collections) and (overwrite):
            self.db[collection].drop()
            self.db.create_collection(collection)

    def drop_collection(self, collection):
        if collection in self.db.list_collection_names():
            self.db[collection].drop()

    def find(self, collection, query=None):
        if query is None:
            q = {}
        else:
            q = query
        return self.db[collection].find(q)

    def insert(self, collection, records, return_result=False):
        r = self.db[collection].insert_many(records)
        if return_result:
            return {
                "acknowledged": r.acknowledged,
                "inserted_count": len(r.inserted_ids),
            }

    def drop(self, collection, query, return_result=False):
        r = self.db[collection].delete_many(query)
        if return_result:
            return {
                "acknowledged": r.acknowledged,
                "deleted_count": r.deleted_count,
            }

    def update(self, collection, query, new_vals, return_result=False):
        nv = {"$set": {new_vals}}
        r = self.db[collection].update_many(query, nv)
        if return_result:
            return {
                "acknowledged": r.acknowledged,
                "matched_count": r.matched_count,
                "modified_count": r.modified_count,
            }


class FakeRepository(AbstractRepository):
    def __init__(self, client="client", db="wqu-abtest"):
        self.client = client
        self.db_name = db
        self.db = {}

    def create_collection(self, collection, overwrite=True):
        if (overwrite) or (collection not in self.db.keys()):
            self.db[collection] = list()
        else:
            pass

    def drop_collection(self, collection):
        self.db.pop(collection, None)

    def find(self, collection, query=None):
        if query is None:
            yield self.db[collection]
        else:
            ((key, val),) = query.items()
            for d in self.db[collection]:
                if (key in d) and (d[key] == val):
                    yield d

    def insert(self, collection, records, return_result=False):
        self.db[collection] = self.db[collection] + list(records)
        if return_result:
            return {"acknowledged": True}

    def drop(self, collection: str, query: dict, return_result=False):
        deleted_count = 0
        new_collection = []
        # Need special case for using MongoDB operator for resetting experiment
        if ("inExperiment" in query) and ("$exists" in query["inExperiment"]):
            for d in self.db[collection]:
                if "inExperiment" not in d:
                    new_collection.append(d)
                else:
                    deleted_count += 1
        else:
            ((key, val),) = query.items()
            for d in self.db[collection]:
                if (key not in d) or (d[key] != val):
                    new_collection.append(d)
                else:
                    deleted_count += 1
        self.db[collection] = new_collection
        if return_result:
            return {"acknowledged": True, "deleted_count": deleted_count}

    def update(self, collection, query, new_vals, return_result=False):
        matched_count = 0
        modified_count = 0
        ((key, val),) = query.items()
        ((new_key, new_val),) = new_vals.items()
        for d in self.db[collection]:
            if d[key] == val:
                matched_count += 1
                d[new_key] = new_val
                # I know this counter doesn't exactly work
                modified_count += 1

        if return_result:
            return {
                "acknowledged": True,
                "matched_count": matched_count,
                "modified_count": modified_count,
            }
