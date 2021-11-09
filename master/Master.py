import os
import grpc
import ReplicatedLog_pb2
import ReplicatedLog_pb2_grpc
from concurrent import futures
import sys
from threading import Thread, Lock
from queue import Queue



logs = []
def logslaves(host, port, msg, lock, w, counter):
    with grpc.insecure_channel(f'{host}:{port}') as channel:
        client = ReplicatedLog_pb2_grpc.PostRequestServiceStub(channel)
        slave_request = ReplicatedLog_pb2.POST(msg=msg)
        response = client.PostRequest(slave_request)
        print('1', port, counter)
        if counter[0] < w:
            if response.msg == '1':
                counter[0] += 1
                print(port, counter[0])
                return 1
        return 1

class Logger(ReplicatedLog_pb2_grpc.PostRequestServiceServicer):
    def PostRequest(self, request, context):
        logs.append(request.msg)
        counter = [1]

        lock = Lock()
        t1 = Thread(target=logslaves, args=('slave1', 50052, request.msg, lock, request.w, counter))
        t2 = Thread(target=logslaves, args=('slave2', 50053, request.msg, lock, request.w, counter))
        t1.start()
        t2.start()

        while True:
            if counter[0] == request.w:
                return ReplicatedLog_pb2.POSTResponse(msg=f'Master and Slaves have recived msg, w={request.w}, counter={counter}')


class SendLogs(ReplicatedLog_pb2_grpc.GetRequestServiceServicer):
    def GetRequest(self, request, context):
        return ReplicatedLog_pb2.GETResponse(data=logs)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    ReplicatedLog_pb2_grpc.add_PostRequestServiceServicer_to_server(Logger(), server)
    ReplicatedLog_pb2_grpc.add_GetRequestServiceServicer_to_server(SendLogs(), server)
    server.add_insecure_port("master:50051")
    server.start()
    server.wait_for_termination()



if __name__ == "__main__":
    serve()

