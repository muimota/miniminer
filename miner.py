#miniminer 
import socket
import json
import hashlib
import binascii
import time
import random

address = '1Edh8qTf8H3xHQvKsFkQ39eNvHLN2URPU7'
nonce   = hex(random.randint(0,2**32-1))[2:].zfill(8)

print "address:{} nonce:{}".format(address,nonce)

sock    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('stratum.solo.nicehash.com', 3334))

#server connection
sock.sendall(b'{"id": 1, "method": "mining.subscribe", "params": []}\n')
response = json.loads(sock.recv(1024))
sub_details,extranonce1,extranonce2_size = response['result']

#authorize workers
sock.sendall(b'{"params": ["'+str(address)+'", "password"], "id": 2, "method": "mining.authorize"}\n')

response = ''
while response.count('\n') < 4:
    response += sock.recv(1024*3)
#get rid of empty lines
responses = [json.loads(res) for res in response.split('\n') if len(res.strip())>0]

#welcome message
print responses[0]['params'][0]+'\n'

try:
    job_id,prevhash,coinb1,coinb2,merkle_branch,version,nbits,ntime,clean_jobs \
        = responses[1]['params']
except:
    pprint(responses)


extranonce2 = '00'*extranonce2_size

coinbase = coinb1 + extranonce1 + extranonce2 + coinb2 
coinbase_hash_bin = hashlib.sha256(hashlib.sha256(binascii.unhexlify(coinbase)).digest()).digest()

print 'coinbase:\n{}\n\ncoinbase hash:{}\n'.format(coinbase,binascii.hexlify(coinbase_hash_bin))
merkle_root = coinbase_hash_bin
for h in merkle_branch:
    merkle_root = hashlib.sha256(hashlib.sha256(merkle_root + binascii.unhexlify(h)).digest()).digest()

merkle_root = binascii.hexlify(merkle_root)

#little endian
merkle_root = ''.join([merkle_root[i]+merkle_root[i+1] for i in range(0,len(merkle_root),2)][::-1])

print 'merkle_root:{}\n'.format(merkle_root)


blockheader = version + prevhash + merkle_root + ntime + nonce +\
    '000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000'
    
print 'blockheader:\n{}\n'.format(blockheader)

hash = hashlib.sha256(hashlib.sha256(binascii.unhexlify(blockheader)).digest()).digest()
print 'hash: {}'.format(binascii.hexlify(hash))
sock.close()
