from IPython.parallel import Client
from DrQueue import Computer as DrQueueComputer


client = Client()

engine_ids = DrQueueComputer.query_all()
for engine_id in engine_ids:
    print("Deleting engine %s from DB." % engine_id)
    DrQueueComputer.delete_from_db_by_engine_id(engine_id)

