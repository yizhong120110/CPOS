# This is the frame details of the ICM which part of the HuaXia bank special service ESB.

Inbound request:
0       1               2               4               12                 16              20          size+20       size+22
+-------+---------------+---------------+---------------+------------------+---------------+ +-------------+ +-----------+
|header |    type       |    version    |     token     |     sequance     |      size     | |    payload  | | frame-end |
+-------+---------------+---------------+---------------+------------------+---------------+ +-------------+ +-----------+
octet    octet           short           longlong        long               long              size octets      2 octets

header:	1 byte, always 0x01
type:	1 byte ,message type.  
		0x01:icm pack(icp->icm(BAOWEN))  0x02:icm pack(icm->icp(BAOWEN))
		0x03:icm pack(icm->icp(ACCEPTED))  0x04:icm pack(icm->icp(REFUSED))
		if 03 or 04 , the message in payloads will describ the details.

version: 2 bytes,0-65535, midware/message version
token:	8 bytes, peer token , not support yet. always 0x000x000x000x000x000x000x000x00
sequance: 4bytes, unique id to distinguish message peers .  server sends back message with the same sequance number as request.
size : 4bytes, payload length, in bytes .
palyload : .....
frame-end :  2bytes , always 0x57, 0x53('WS')


payload:
ICPs -> ICM
0            15         size+15     
+-------------+ +-----------+      
|      ID     | |  message  |      
+-------------+ +-----------+      
 octets           size octets 

ID:	16 bytes, string , max length is 16, if less than 16 charecters , the remains will be filled up with 0x00.
	this ID represents the commnode , and will be used in distinguishing which unpack method will be applied on the message.
message:	the message received by ICPs, and will be forwarded to the ICM . (jie shou dao de bao wen).



ICM -> ICPs
0            15         size+15     
+-------------+ +-----------+      
|      ID     | |  message  |      
+-------------+ +-----------+      
 octets           size octets 

id:	16 bytes, string , max length is 16, if less than 16 characters , the remains will be filled up with 0x00.
message:	the message will be sent back to ICPs.  (xiang ying ma@ yao fa song de bao wen )
formation of message :
message is a string that is the message(Bao Wen.)
only Exception is the TIMEOUT message starts with 'Timeout@'
for example : "Timeout@some description about the reason."



