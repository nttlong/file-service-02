"""
mongodb://codx:c0dx2022@docdb-2022-10-13-03-50-24.cluster-ctlppr6ybtky.ap-southeast-1.docdb.amazonaws.com:27017/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false
"""
import certifi
ca = certifi.where()

import pymongo
import sys
"""
ssh -i "ec2Access.pem" -L 27017:sample-cluster.node.us-east-1.docdb.amazonaws.com:27017 ubuntu@ec2-34-229-221-164.compute-1.amazonaws.com -N 

"""
pp="Server=docdb-2022-10-13-03-50-24.ctlppr6ybtky.ap-southeast-1.docdb.amazonaws.com; Port=27107; User=codx; Password=c0dx2022; UseSSL=True; SSLServerCert=*; Other='UseFindAPI=True';"
##Create a MongoDB client, open a connection to Amazon DocumentDB as a replica set and specify the read preference as secondary preferred

path_to_ca_file='rds-combined-ca-bundle.pem'
# cnn=f'mongodb://{username}:{password}@docdb-2022-10-13-03-50-24.ctlppr6ybtky.ap-southeast-1.docdb.amazonaws.com:27017/?connectTimeoutMS=300000&ssl=true&tlsCAFile={path_to_ca_file}&retryWrites=false'
# cnn=r'mongodb://codx:c0dx2022@localhost:27017/?connectTimeoutMS=300000&ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&retryWrites=false'
cnn=r'mongodb://codx:c0dx2022@localhost:27017/?sslVerifyCertificate=false&connectTimeoutMS=300000&ssl=true&tlsCAFile=rds-combined-ca-bundle.pem&retryWrites=false'
#cnn=r'mongodb://localhost:27017'
# cnn=r'mongodb://codx:c0dx2022@docdb-2022-10-13-03-50-24.ctlppr6ybtky.ap-southeast-1.docdb.amazonaws.com:27017'
username='codx'
password='c0dx2022'
server = 'docdb-2022-10-13-03-50-24.ctlppr6ybtky.ap-southeast-1.docdb.amazonaws.com'
port=27017
cer_file='rds-combined-ca-bundle.pem'
"""
mongodb+srv://<username>:<password>@cluster0.3otii.mongodb.net/?retryWrites=true&w=majority
"""
server='cluster0.3otii.mongodb.net'
client = pymongo.MongoClient(


    host="172.16.7.25",
    port=27018,
    username='admin',
    password='123456',
    # tlsAllowInvalidCertificates=True,
    # tlsCAFile=cer_file,
    # ssl=True
)
# client = pymongo.MongoClient('mongodb://<sample-user>:<password>@sample-cluster.node.us-east-1.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false')
"""
ssh -i "lv-codx.pem" -L 27017:docdb-2022-10-13-03-50-24.ctlppr6ybtky.ap-southeast-1.docdb.amazonaws.com:27017 ec2-user@ec2-54-255-150-177.ap-southeast-1.compute.amazonaws.com -N -vvv

"""
##Specify the database to be used
db = client.sample_database

##Specify the collection to be used
col = db.sample_collection

##Insert a single document
col.insert_one({'hello':'Amazon DocumentDB'})

##Find the document that was previously written
x = col.find_one({'hello':'Amazon DocumentDB'})

##Print the result to the screen
print(x)

##Close the connection
client.close()