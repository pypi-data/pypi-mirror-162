import grpc
import asyncio
import signal
import argparse

from bluerpc_service.rpc import (
    ble_pb2_grpc,
    worker_pb2_grpc,
)
from bluerpc_service.ble import BluetoothLE
from bluerpc_service.worker import Worker

async def serve(bind_addr="[::]:50052"):
    server = grpc.aio.server()
    worker_pb2_grpc.add_WorkerServicer_to_server(Worker(), server)
    ble_pb2_grpc.add_BluetoothLEServicer_to_server(BluetoothLE(), server)
    server.add_insecure_port(bind_addr)
    await server.start()
    print(f"BlueRPC worker running on {bind_addr}")
    await server.wait_for_termination()

def handler(a,b):
    exit(0)

def run():
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    parser = argparse.ArgumentParser(description='BlueRPC Worker')
    parser.add_argument('--bind_addr',
        type=str,
        help='bind address of the server',
        default="[::]:50052",
        nargs='?'
    )
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(serve(args.bind_addr))

if __name__ == "__main__":
    run()
