# применение миграций.
from concurrent import futures

import grpc
from src.proxyproto import proxyproto_pb2_grpc
from src.rpc.cetrifugo import CentrifugoHandler
import os
from dotenv import load_dotenv
from yoyo import read_migrations, get_backend


def apply_migrations():
    migrations = read_migrations("./migrations")
    backend = get_backend(os.environ.get("APP_DATABASE_URL"))
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))



def serve():
    load_dotenv()
    apply_migrations()
    port = os.getenv("APP_PORT", "10000")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proxyproto_pb2_grpc.add_CentrifugoProxyServicer_to_server(CentrifugoHandler(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
