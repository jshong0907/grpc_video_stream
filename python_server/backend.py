import grpc
import Proto.stream_pb2 as stream_pb2
import Proto.stream_pb2_grpc as stream_pb2_grpc
import io
from websocket import Wss_Server
from yolo_utils import Yolo_Utils_Class
from concurrent import futures
from PIL import Image
from time import sleep
import datetime

class Streaming(stream_pb2_grpc.StreamingServicer):
    def __init__(self, container):
        super(Streaming, self).__init__()
        self.Y = Yolo_Utils_Class()
        self.container = container
            
    def ImgStream(self, request_iterator, context): #server handler
        for req in request_iterator:
            io_file = io.BytesIO(req.data) #convert data type
            pil = Image.open(io_file) #convert data type
            
            ########### processing data #############
            box_data = self.Y.yolo_box_data(pil_img = pil, ind = req.id, save=True)
            plotted_img = self.Y.yolo_img_data(pil_img= pil)
            ########### processing data #############
            
            response = stream_pb2.Result()
            response.smoke = False if len(box_data)==0 else True
            
            container.append(plotted_img)
            
            yield response

def logger(message, **kwagrs):
    print('[' + datetime.datetime.now().isoformat()[:-3] + '] ' + ' [grpc] : '+ message, **kwagrs)

if __name__=="__main__":
    container = []
    wss_thread = Wss_Server(addr = "localhost", port=3001,container= container)
    wss_thread.daemon = True # main 죽으면 같이 죽도록 설정
    wss_thread.start() #websocket 서버 실행
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stream_pb2_grpc.add_StreamingServicer_to_server(Streaming(container), server)
    logger("****************************************")
    logger("*        🟢 grpc server started        *")
    logger("*        listening on port : 50051     *")
    logger("****************************************")
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()
