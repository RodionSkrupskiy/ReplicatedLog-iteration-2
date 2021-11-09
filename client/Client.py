import os
import grpc
import ReplicatedLog_pb2
import ReplicatedLog_pb2_grpc


slave_ports = ['50052', '50053']

def post():
    with grpc.insecure_channel('172.17.0.1:50051') as channel:
        client = ReplicatedLog_pb2_grpc.PostRequestServiceStub(channel)
        request = ReplicatedLog_pb2.POST(w=int(input('Enter write concern parameter: ')), msg=input('Enter values to log: '))
        response = client.PostRequest(request)
        print(response)

def get_master():
    with grpc.insecure_channel('172.17.0.1:50051') as channel:
        client = ReplicatedLog_pb2_grpc.GetRequestServiceStub(channel)
        request = ReplicatedLog_pb2.GET(msg='1')
        response = client.GetRequest(request)
        print(response.data)

def get_slaves():
    for port in slave_ports:
        with grpc.insecure_channel(f'172.17.0.1:{port}') as channel:
            client = ReplicatedLog_pb2_grpc.GetRequestServiceStub(channel)
            request = ReplicatedLog_pb2.GET(msg='1')
            response = client.GetRequest(request)
            print(response.data)

user_input = input('Enter POST, GET or q ').lower()
while user_input != 'q':
    if user_input == 'post':
        print('Calling POST')
        post()
    elif user_input == 'get':
        ask_node = input('Enter where you want logs from: m or s ').lower()
        if ask_node == 'm':
            print('calling GET')
            get_master()
        elif ask_node == 's':
            print('calling GET')
            get_slaves()

    else:
        print('Wrong input')
    user_input = input('Enter POST, GET or q ').lower()

