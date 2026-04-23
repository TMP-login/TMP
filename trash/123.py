import requests
import base64

headers = {
 'content-length':'244',
 'sec-ch-ua-platform':'"Windows"',
 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
 'accept':'application/json, text/plain, */*',
 'sec-ch-ua':'"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
 'content-type':'application/json',
 'sec-ch-ua-mobile':'?0',
 'origin':'https://ews.mtyl0.com',
 'sec-fetch-site':'same-origin',
 'sec-fetch-mode':'cors',
 'sec-fetch-dest':'empty',
 'referer':'https://ews.mtyl0.com/user/login-form/login',
 'accept-encoding':'gzip, deflate, br, zstd',
 'accept-language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
 'priority':'u=1, i'}
payload=base64.b64decode("eyJvcGVyYXRpb25OYW1lIjoiVXNlckdyZWV0aW5nIiwidmFyaWFibGVzIjp7ImlucHV0Ijp7InVzZXJfYWNjb3VudCI6Imd1YWppeWluZ2xpMDAyIn19LCJxdWVyeSI6InF1ZXJ5IFVzZXJHcmVldGluZygkaW5wdXQ6IFVzZXJHcmVldGluZ0lucHV0T2JqKSB7XG4gIFVzZXJHcmVldGluZyhpbnB1dDogJGlucHV0KSB7XG4gICAgZ3JlZXRpbmdcbiAgICBoYXNfc2V0X2dyZWV0aW5nXG4gICAgX190eXBlbmFtZVxuICB9XG59XG4ifQ==")

response0 = requests.request("POST", "https://ews.mtyl0.com/APIV2/GraphQL?l=zh-cn&pf=web&udid=b9bb9c21-f51d-45bd-85e5-27d99c8a2b42", headers=headers, data=payload)

