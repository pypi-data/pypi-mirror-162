import requests
import six
import base64
import datetime

from pycafe24.cache import Cache

class Cafe24AuthBase(object):
	def __init__(self,session):
		if isinstance(session,requests.Session):
			self._session = session
		else:
			from requests import api
			self._session = api




class Cafe24Credentials(object):
	def __init__(
		self,
		mall_id=None,
		client_id=None,
		client_secret=None,
		csrf_token=None,
		redirect_uri=None,
		scope=None,
		cache_handler=None
	):

		self.mall_id = mall_id
		self.client_id = client_id
		self.client_secret = client_secret
		self.csrf_token = csrf_token
		self.redirect_uri = redirect_uri
		self.scope = scope
		self.cache_handler = cache_handler


		self.access_token = None
		self.refresh_token = None
		self.access_token_expiration = None
		self.refresh_token_expiration = None


		if self.cache_handler:
			token_info = self.cache_handler.get_token()
			self.access_token = token_info["access_token"]
			self.refresh_token = token_info["refresh_token"]
			self.access_token_expiration=token_info["access_token_expiration"]
			self.refresh_token_expiration=token_info["refresh_token_expiration"]



	def has_valid_access_token(self):
		if self.access_token == None:
			return False
		else:
			print("KST")
			KST = datetime.timezone(datetime.timedelta(hours=9))
			access_token_expiration_timestamp = datetime.datetime.strptime(self.access_token_expiration,"%Y-%m-%dT%H:%M:%S.%f")
			# current_timestamp = datetime.datetime.now(KST)
			current_timestamp = datetime.datetime.now()
			# print(datetime.datetime.now())

			if current_timestamp > access_token_expiration_timestamp:
				return False
			else:
				return True

	def has_valid_refresh_token(self):
		if self.refresh_token == None:
			return False
		else:
			print("KST")
			KST = datetime.timezone(datetime.timedelta(hours=9))
			refresh_token_expiration_timestamp = datetime.datetime.strptime(self.refresh_token_expiration,"%Y-%m-%dT%H:%M:%S.%f")
			current_timestamp = datetime.datetime.now()

			if current_timestamp > refresh_token_expiration_timestamp:
				return False
			else:
				return True



	def get_authentication_code(self):
		oauth_url = "https://{0}.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id={1}&redirect_uri={2}&scope={3}".format(self.mall_id,self.client_id,self.redirect_uri,self.scope)

		response = requests.get(oauth_url);
		# print(response.url)

		response = requests.get(response.url)

		return response.url

	def get_refresh_token(self):
		url = "https://{0}.cafe24api.com/api/v2/oauth/token".format(self.mall_id)
		auth_header = base64.b64encode(
			six.text_type(self.client_id + ":" + self.client_secret).encode("ascii")
		)
		headers = {"Authorization": "Basic %s" % auth_header.decode("ascii"), "Content-Type":"application/x-www-form-urlencoded"}

		data = {
			"grant_type":"refresh_token",
			"refresh_token":self.refresh_token
		}

		response = requests.post(url,data=data,headers=headers,verify=True)
		print(response.json())
		json_out = response.json()
		print("jsonout is ",json_out)
		self.access_token = json_out["access_token"]
		self.access_token_expiration = json_out["expires_at"]
		self.refresh_token = json_out["refresh_token"]
		self.refresh_token_expiration = json_out["refresh_token_expires_at"]

		if self.cache_handler:
			self.cache_handler.save_token({"access_token":self.access_token,"refresh_token":self.refresh_token,
					"access_token_expiration":self.access_token_expiration,"refresh_token_expiration":self.refresh_token_expiration})



	def get_access_code(self,authentication_code):
		oauth_url = "https://{0}.cafe24api.com/api/v2/oauth/token".format(self.mall_id)

		auth_header = base64.b64encode(
			six.text_type(self.client_id + ":" + self.client_secret).encode("ascii")
		)
		headers = {"Authorization": "Basic %s" % auth_header.decode("ascii"), "Content-Type":"application/x-www-form-urlencoded"}

		data = {
			"grant_type":"authorization_code",
			"code": authentication_code,
			"redirect_uri" : self.redirect_uri
		}

		response = requests.post(oauth_url,data=data,headers=headers,verify=True)
		print(response.json())
		json_out = response.json()

		self.access_token = json_out["access_token"]
		self.access_token_expiration = json_out["expires_at"]
		self.refresh_token = json_out["refresh_token"]
		self.refresh_token_expiration = json_out["refresh_token_expires_at"]

		if self.cache_handler:
			self.cache_handler.save_token({"access_token":self.access_token,"refresh_token":self.refresh_token,
					"access_token_expiration":self.access_token_expiration,"refresh_token_expiration":self.refresh_token_expiration})



	def __str__(self):
		return """
			\nmall_id : {0} \n
			\nclient_id : {1} \n
			\nclient_secret : {2} \n
			\ncsrf_token : {3} \n
			\nredirect_uri : {4} \n
			\nscope : {5} \n
			\naccess_token : {6} \n
			\naccess_token_expiration : {7} \n
			\nrefresh_token : {8} \n
			\nrefresh_token_expiration: {9} \n
		""".format(self.mall_id,self.client_id,self.client_secret,self.csrf_token,self.redirect_uri,
					self.scope,self.access_token,self.access_token_expiration,self.refresh_token,self.refresh_token_expiration)
