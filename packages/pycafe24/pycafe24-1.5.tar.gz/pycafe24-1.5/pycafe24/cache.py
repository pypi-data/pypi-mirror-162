

import json




class Cache(object):

	def __init__(self,mall_id=None, cache_path=None):

		print(cache_path)
		if cache_path:
			self.cache_path = cache_path

		else:
			if mall_id:
				self.cache_path = "pycafe24/cache/" + mall_id



	def get_token(self):

		token_info = None
		try:
			print(self.cache_path)
			f = open(self.cache_path)
			token_info = json.loads(f.read())
			print(token_info)
			f.close()

		except IOError:
			print("error while getting token from cache")

		return token_info



	def save_token(self,token_info):
		print(token_info)
		try:
			f = open(self.cache_path,"w")
			f.write(json.dumps(token_info))
			f.close()
		except TypeError:
			print("error while serializing")
		except IOError:
			print("IOError")
