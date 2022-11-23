import http.client
import ssl
import json

# connection = http.client.HTTPSConnection('test-oms.qtsc.com.vn')
connection = http.client.HTTPSConnection(
    'test-oms.qtsc.com.vn',
    context = ssl._create_unverified_context()
)

headers = {'Content-type': 'application/json'}

foo = {'username': 'admin/root','password':'root'}
json_foo = json.dumps(foo)

connection.request('POST', '/lvfile/api/accounts/token', json_foo, headers)

response = connection.getresponse()
print(response.read().decode())