import random
import time
import sys
import grpc
import ReplicatedLog_pb2
import ReplicatedLog_pb2_grpc
from concurrent import futures

ipaddress = sys.argv[1]
host = int(sys.argv[2])
logs = []
class SlaveLogger(ReplicatedLog_pb2_grpc.PostRequestServiceServicer):
    def PostRequest(self, request, context):
        time.sleep(random.randint(0, 8))
        logs.append(request.msg)
        return ReplicatedLog_pb2.POSTResponse(msg='1')

class SlaveSendLogs(ReplicatedLog_pb2_grpc.GetRequestServiceServicer):
    def GetRequest(self, request, context):
        return ReplicatedLog_pb2.GETResponse(data=logs)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ReplicatedLog_pb2_grpc.add_PostRequestServiceServicer_to_server(SlaveLogger(), server)
    ReplicatedLog_pb2_grpc.add_GetRequestServiceServicer_to_server(SlaveSendLogs(), server)
    server.add_insecure_port(f"{ipaddress}:{host}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

