try:
	import requests  ,re, os , sys , random , uuid , user_agent , json,secrets,secrets
	from uuid import uuid4
	from secrets import *
	from user_agent import generate_user_agent
	import requests
	import names
	import uuid,string
	import instaloader
	import hashlib
	import urllib
	import mechanize
	import json
	import secrets
	import smtplib
    
	
except ImportError:
	os.system('pip install requests')
	os.system('pip install user_agent')
	
	
uid = str(uuid4)
class salammzere3:
	
	def Instalogin(email,password):
		
		UrlSalam = 'https://www.instagram.com/accounts/login/ajax/'
		
		HeadSalam = {

    'accept':'*/*',
    'accept-encoding':'gzip, deflate, br',
    'accept-language':'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-length':'317',
    'content-type':'application/x-www-form-urlencoded',
    'cookie':'mid=YdduAwAEAAH5tvQgBxaWFmtCauW1; ig_did=3B9E189F-664C-4C27-BAD4-A4DC839FFFFA; ig_nrcb=1; shbid="15789\0545722116218\0541674148260:01f7b34891a790ddc3b2f8f61b0c76d2e539c3efaedb09b6812283940bfcc6739f7a6930"; shbts="1642612260\0545722116218\0541674148260:01f74a3f9c5b7857cd36ad8a36a61bbe4bcc22061a61a730590ea1f665bd85916ae193b4"; csrftoken=qMiGRabzXyZlJPciGxtTKQAJZkCv0Rhi',
    'origin':'https://www.instagram.com',
    'referer':'https://www.instagram.com/',
    'sec-fetch-dest':'empty',
    'sec-fetch-mode':'cors',
    'sec-fetch-site':'same-origin',
    'user-agent':generate_user_agent(),
    'x-asbd-id':'198387',
    'x-csrftoken':'qMiGRabzXyZlJPciGxtTKQAJZkCv0Rhi',
    'x-ig-app-id':'936619743392459',
    'x-ig-www-claim':'0',
    'x-instagram-ajax':'9e76603e49dc',
    'x-requested-with':'XMLHttpRequest'}
    
		DatSalam = {
	'username': email,
	'enc_password': '#PWD_INSTAGRAM_BROWSER:0:&:'+ password
	}
		ReqSalam = requests.post(UrlSalam,headers=HeadSalam,data=DatSalam)
		if ('"authenticated":true') in ReqSalam.text:
			
			
			os.system('rm -rf sessionid.txt')
			
			APK = ReqSalam.cookies['sessionid']
			
			f = open('sessionid.txt','a')
			
			f.write(APK+"\n")
			
			f.close()
			
			return {'status':'Success','login':'true','sessionid':str(APK)}
			
		if str('"message":"challenge_required","challenge"') in ReqSalam.text:
			
			return False
			
		else:
			
			return None
		


	def gmail(email):
	    url = 'https://android.clients.google.com/setup/checkavail'
	    headers = {
		'Content-Length':'98',
		'Content-Type':'text/plain; charset=UTF-8',
		'Host':'android.clients.google.com',
		'Connection':'Keep-Alive',
		'user-agent':'GoogleLoginService/1.3(m0 JSS15J)',}
	    data = json.dumps({
		'username':str(email),
		'version':'3',
		'firstName':'GDO_0',
		'lastName':'GDOTools' })
	    res = requests.post(url,data=data,headers=headers)
	    if res.json()['status'] == 'SUCCESS':
	           return {'status':'Success','email':True}
	           
	    else:
	           return {'status':'error','email':False}
            
	def instagram(email):
	    headers = {
            # 'Content-Length': '143',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'i.instagram.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Instagram 6.12.1 Android (25/7.1.2; 160dpi; 383x681; LENOVO/Android-x86; 4242ED1; x86_64; android_x86_64; en_US)',
            'Accept-Language': 'en-US',
            'X-IG-Connection-Type': 'WIFI',
            'X-IG-Capabilities': 'AQ==',
            # 'Accept-Encoding': 'gzip',
        }

	    data = {
            'ig_sig_key_version': '4',
            "q": f"{email}"
        }

	    response = requests.post('https://i.instagram.com/api/v1/users/lookup/', headers=headers, data=data).text
	    if "ok" in response:
	       return {'email': email,'status':'True'}
	    else:
	        return {'email': email,'status':'False'}
	        
	        
	def tiktok(email):
	    url = "https://api2-t2.musical.ly/aweme/v1/passport/find-password-via-email/?version_code=7.6.0&language=ar&app_name=musical_ly&vid=43647C38-9344-40A3-AD8E-29F6C7B987E4&app_version=7.6.0&is_my_cn=0&channel=App%20Store&mcc_mnc=&device_id=6999590732555060741&tz_offset=10800&account_region=&sys_region=SA&aid=1233&screen_width=1242&openudid=a0594f8115e0a1a51e1a31490aeef9afc2409ff4&os_api=18&ac=WIFI&os_version=12.5.4&app_language=ar&tz_name=Asia/Riyadh&device_platform=iphone&build_number=76001&iid=7021194671750481669&device_type=iPhone7,1&idfa=20DB6089-D1C6-49EF-8943-9C310C8F1B5D&mas=002ed4fcfe1207217efade4142d0b05e0c845e118f07206205d6a8&as=a11664d78a2e110bd08018&ts=16347494182"
	    headers = {
            'Host': 'api2-t2.musical.ly',
            'Cookie': 'store-country-code=sa; store-idc=alisg; install_id=7021194671750481669; odin_tt=7b67a77e780e497b1c89d483072f567580c860fe622a9ad519c8af998a287f424ed5f97297928981fa70ca6e8cb2648ebc46af23c9c9588a540567c77f877d307588080b16d8b92d3c3f875da9cd2291; ttreq=1$ee9fd401f276e956ba82d3ffd7392ffa6829472d',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': str(generate_user_agent()),
            'Accept-Language': 'ar-SA;q=1',
            'Content-Length': '25',
            'Connection': 'close'}
	    data = {"email": email}
	    req = requests.post(url, headers=headers, data=data)
	    if "Sent successfully" in req.text:
	        return {'email': email,'status':'True'}
	        
	    else:
	        return {'email': email,'status':'False'}


	def logintiktok(email,password):
	    url = 'https://api2.musical.ly/passport/user/login/?mix_mode=1&username=1&email=&mobile=&account=&password=hg&captcha=&ts=&app_type=normal&app_language=en&manifest_version_code=2018073102&_rticket=1633593458298&iid=7011916372695598854&channel=googleplay&language=en&fp=&device_type=SM-G955F&resolution=1440*2792&openudid=91cac57ba8ef12b6&update_version_code=2018073102&sys_region=AS&os_api=28&is_my_cn=0&timezone_name=Asia/Muscat&dpi=560&carrier_region=OM&ac=wifi&device_id=6785177577851504133&mcc_mnc=42203&timezone_offset=14400&os_version=9&version_code=800&carrier_region_v2=422&app_name=musical_ly&version_name=8.0.0&device_brand=samsung&ssmix=a&build_number=8.0.0&device_platform=android&region=US&aid=&as=&cp=Qm&mas='
	    headers = \
            {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'cookie': 'csrftoken=' + str(secrets.token_hex(8) * 2) + '; sessionid=' + str(secrets.token_hex(8) * 2) + ';',
            'User-Agent': 'Connectionzucom.zhiliaoapp.musically/2018073102 (Linux; U; Android 9; en_AS; SM-G955F; Build/PPR1.180610.011; Cronet/58.0.2991.0)z',
            'Host': 'api2.musical.ly', 'Connection': 'keep-alive'}
	    data = {"email": str(email), "password": str(password)}
	    res = requests.post(url, headers=headers, data=data)
	    if ("user_id") in res.text:
	        sessionid = str(res.json()['data']['session_key'])
	        return {'username': str(email), 'password': str(password), 'status': 'True', 'SessionId': sessionid}
	        
	    elif ("Incorrect account or password") in res.text:
	       return {'username': str(email), 'password': str(password), 'status' :'Error Password Or Username'}
	    else:
	        return {'username': str(email), 'password': str(password), 'status' :'False'}
	        
	  
	  
	def hotmail(email):
	    url = "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=0&emailAddress=" + str(email) + "&_=1604288577990"
	    headers = {
    	    "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": str(generate_user_agent()),
            "Connection": "close",
            "Host": "odc.officeapps.live.com",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://odc.officeapps.live.com/odc/v2.0/hrd?rs=ar-sa&Ver=16&app=23&p=6&hm=0",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
            "canary": "BCfKjqOECfmW44Z3Ca7vFrgp9j3V8GQHKh6NnEESrE13SEY/4jyexVZ4Yi8CjAmQtj2uPFZjPt1jjwp8O5MXQ5GelodAON4Jo11skSWTQRzz6nMVUHqa8t1kVadhXFeFk5AsckPKs8yXhk7k4Sdb5jUSpgjQtU2Ydt1wgf3HEwB1VQr+iShzRD0R6C0zHNwmHRnIatjfk0QJpOFHl2zH3uGtioL4SSusd2CO8l4XcCClKmeHJS8U3uyIMJQ8L+tb:2:3c",
            "uaid": "d06e1498e7ed4def9078bd46883f187b",
            "Cookie": "xid=d491738a-bb3d-4bd6-b6ba-f22f032d6e67&&RD00155D6F8815&354"}
	    res = requests.post(url, data="", headers=headers).text
	    if ("Neither") in res:
	        return {'status': 'Success', 'email': 'True'}
	    else:
	        return {'email': email,'status':'False'}

	    