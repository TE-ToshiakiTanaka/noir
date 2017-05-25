import os
import socket
import threading
from banner import Banner
from itsdangerous import bytes_to_int
from Queue import Queue

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp"))

class MinicapStream:

    __instance = None
    __mutex = threading.Lock()
    def __init__(self):
        self.IP = "127.0.0.1"
        #self.IP = socket.gethostname()
        #self.IP = "localhost"
        print(self.IP)
        self.PORT = 1313
        self.Pid = 0
        self.banner = Banner()
#       self.minicapSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.minicapSocket=None
        self.ReadImageStreamTask = None
        self.push = None
        self.picture = Queue()

    @staticmethod
    def getBuilder():
        """Return a single instance of TestBuilder object """
        if (MinicapStream.__instance == None):
            MinicapStream.__mutex.acquire()
            if (MinicapStream.__instance == None):
                MinicapStream.__instance = MinicapStream()
            MinicapStream.__mutex.release()
        return MinicapStream.__instance

    def get_d(self):
        print self.picture.qsize()

    def run(self):
        self.minicapSocket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.minicapSocket.connect((self.IP, self.PORT))
#         return self.ReadImageStream()
        self.ReadImageStreamTask = threading.Thread(target=self.ReadImageStream).start()



    def ReadImageStream(self):
        readBannerBytes = 0
        bannerLength = 2
        readFrameBytes = 0
        frameBodylength = 0
        dataBody = ""
        counter = 0
        while True:
            reallen=self.minicapSocket.recv(4096)
            length = len(reallen)
            if not length:
                continue
            cursor = 0
            while cursor < length:
                #just do it
                if readBannerBytes < bannerLength:
                    if readBannerBytes==0:
                        self.banner.version = bytes_to_int(reallen[cursor])
                    elif readBannerBytes==1:
                        bannerLength = bytes_to_int(reallen[cursor])
                        self.banner.length = bannerLength
                    elif readBannerBytes in [2,3,4,5]:
                        self.banner.pid += (bytes_to_int(reallen[cursor]) << ((readBannerBytes - 2) * 8)) >> 0;
                    elif readBannerBytes in [6,7,8,9]:
                        self.banner.real_width += (bytes_to_int(reallen[cursor]) << ((readBannerBytes - 6) * 8)) >> 0;
                    elif readBannerBytes in [10,11,12,13]:
                        self.banner.real_height += (bytes_to_int(reallen[cursor]) << ((readBannerBytes - 10) * 8)) >> 0;
                    elif readBannerBytes in [14,15,16,17]:
                        self.banner.virtual_width += (bytes_to_int(reallen[cursor]) << ((readBannerBytes - 14) * 8)) >> 0;
                    elif readBannerBytes in [18,19,20,21]:
                        self.banner.virtual_height += (bytes_to_int(reallen[cursor]) << ((readBannerBytes - 18) * 8)) >> 0;
                    elif readBannerBytes == 22:
                        self.banner.orientation = bytes_to_int(reallen[cursor])*90
                    elif readBannerBytes == 23:
                        self.banner.quirks = bytes_to_int(reallen[cursor])
                    cursor += 1
                    readBannerBytes += 1
                    if readBannerBytes == bannerLength:
                        print self.banner.toString()
                elif readFrameBytes < 4:
                    frameBodylength =frameBodylength+ ((bytes_to_int(reallen[cursor])<<(readFrameBytes*8)) >> 0)
                    cursor += 1
                    readFrameBytes += 1
                else:
                    if length - cursor >= frameBodylength:
                        dataBody = dataBody + reallen[cursor:(cursor+frameBodylength)]
                        if bytes_to_int(dataBody[0])!=0xFF or bytes_to_int(dataBody[1])!=0xD8:
                            return
                        self.picture.put(dataBody)
                        if counter % 10 == 0:
                            self.save_file(os.path.join(PATH, "pic%s.png" % str(counter)), dataBody)
                        cursor += frameBodylength
                        frameBodylength = 0
                        readFrameBytes = 0
                        dataBody = ""
                        counter = counter + 1
                    else:
                        dataBody = dataBody + reallen[cursor:length]
                        frameBodylength -= length - cursor;
                        readFrameBytes += length - cursor;
                        cursor = length;


# adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1200x1920@1200x1920/0
#             adb forward tcp:1313 localabstract:minicap


    def save_file(self,file_name, data):
        file=open(file_name, "wb")
        file.write(data)
        file.flush()
        file.close()




if __name__ == '__main__':
    a = MinicapStream.getBuilder()
    print id(a)
    a.run()
    print a.picture
