import tika
from dateutil.parser import parser

tika.TikaClientOnly = True

from tika import parser
parser.ServerEndpoint="http://localhost:9999"
fx = parser.from_file(
    r"/home/vmadmin/python/v6/file-service-02/config.yml",
    serverEndpoint=parser.ServerEndpoint
)
print(fx)