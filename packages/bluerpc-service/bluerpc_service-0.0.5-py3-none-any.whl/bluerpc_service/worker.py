import grpc
from bluerpc_service.rpc import (
    worker_pb2,
    worker_pb2_grpc,
    common_pb2,
)
import time
import platform

START_TIME = time.time()

class Worker(worker_pb2_grpc.WorkerServicer):
    async def WorkerInfo(
        self, request: common_pb2.Empty, context: grpc.aio.ServicerContext
    ) -> worker_pb2.WorkerInfoResponse:
        return worker_pb2.WorkerInfoResponse(
            uptime=round(time.time() - START_TIME),
            max_devices=-1,
            supported_types=[
                common_pb2.DeviceType.DEVICE_TYPE_BLE4,
                common_pb2.DeviceType.DEVICE_TYPE_CLASSIC,
            ],
            worker_type=worker_pb2.WorkerType.WORKER_TYPE_SERVICE,
            operating_system=platform.system(),
            operating_system_version=platform.release()
        )

