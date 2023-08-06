import psycopg2
import psycopg2.extras

connection = psycopg2.connect(
    f'postgresql://user:password@postgresql/testing_db',
    connection_factory=psycopg2.extras.LogicalReplicationConnection
)

cursor = connection.cursor()
replication_slot_name = 'testing'

try:
    cursor.create_replication_slot(replication_slot_name, output_plugin='wal2json')
except Exception:
    pass

cursor.start_replication(slot_name=replication_slot_name, decode=True, status_interval=1)
cursor.consume_stream(lambda message: print('received message:', message, message.payload))
