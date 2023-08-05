# Cage® class v.3.1.0 (Cage file server v.4.1)
# © A.S.Aliev, 2019-2022


#   Parameters

PAGESIZE = 64 * 2 ** 10  # 64Kb     size of one page in buffer

NUMPAGES = 2 ** 10  # 1024    number of pages in buffer

MAXSTRLEN = 64 * 2 ** 20  # 64Mb   max length (amount) of byte's data arrays
#   in read/write file operations

MAX_CHANNELS = 64  # maximum number of simultaneously opened channels

CAGE_SERVER_NAME = "cage_server"

DEFAULT_SERVER_PORT = "127.0.0.1:3570"  # default file server - ip:port ("main" port)
                                        # "192.168.99.100:3570"    

ATTEMPTS_MAKE_CONNECTION = 5  # max. number of attempts to connect with each file server     
CONNECTION_TIMEOUT = 5  # timeout after attempt to connect with file server (sec.)                 

ATTEMPTS_GET_RESPONSE = 5  # max. number of attempts to get response from server      
GET_RESPONSE_TIMEOUT = 5  # timeout for recieving common & client ports from server (sec.)

RESPONSE_TIMEOUT = 5000  # 5 sec. timeout get response from server (msec)
                                       
WRITE_THREAD_PAR =  False  #   True - threading while write pushed page

CACHE_FILE = "cage"  #  default name for cash during cage sleep

CACHE_FILE2 = "cage2"

SPLITTER=b"\x00" * 4        # split cage_id and JWT in client_id 

CAGE_SERVER_WWW = '' # "ec2-35-180-190-111.eu-west-3.compute.amazonaws.com:3570" 
                     #  "127.1.0.0:3570"  
                     #  "cageserver.ddns.net:3570"

CAGE_DEBUG =   False # True  #                                                  
