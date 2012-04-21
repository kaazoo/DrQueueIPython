from IPython.parallel import Client
from DrQueue import Computer as DrQueueComputer


client = Client()

for engine_id in client.ids:
    DrQueueComputer.delete_from_db_by_engine_id(engine_id)

