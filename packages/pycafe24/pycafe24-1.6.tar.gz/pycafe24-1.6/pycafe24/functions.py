import requests
import json
from .exceptions import Cafe24Exception

class Cafe24Client(object):
	def __init__(self,credentials_manager):
		self.credentials_manager = credentials_manager


	def _put(self,url,payload):
		if not self.credentials_manager.has_valid_access_token():
			self.credentials_manager.get_refresh_token()
		headers = {
					'Authorization': "Bearer {0}".format(self.credentials_manager.access_token),
					'Content-Type': "application/json",
					'X-Cafe24-Api-Version': "2022-06-01",
					'X-Api-Call-Limit': "1/40"
					}
		response = requests.request("PUT",url,data=payload,headers=headers)
		return response


	def _post(self,url,payload):
		if not self.credentials_manager.has_valid_access_token():
			self.credentials_manager.get_refresh_token()
		headers = {
					'Authorization': "Bearer {0}".format(self.credentials_manager.access_token),
					'Content-Type': "application/json",
					'X-Cafe24-Api-Version': "2022-06-01",
					'X-Api-Call-Limit': "1/40"
					}
		response = requests.request("POST",url,data=payload,headers=headers)
		return response

	def _get(self,url,payload):
		if not self.credentials_manager.has_valid_access_token():
			self.credentials_manager.get_refresh_token()
		headers = {
					'Authorization': "Bearer {0}".format(self.credentials_manager.access_token),
					'Content-Type': "application/json",
					'X-Cafe24-Api-Version': "2022-06-01",
					'X-Api-Call-Limit': "1/40"
					}
		response = requests.request("GET",url,data=payload,headers=headers)


		return response

	def _delete(self,url,payload):
		if not self.credentials_manager.has_valid_access_token():
			self.credentials_manager.get_refresh_token()
		headers = {
					'Authorization': "Bearer {0}".format(self.credentials_manager.access_token),
					'Content-Type': "application/json",
					'X-Cafe24-Api-Version': "2022-06-01",
					'X-Api-Call-Limit': "1/40"
					}
		response = requests.request("DELETE",url,data=payload,headers=headers)
		return response




	def num_coupon(self):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/coupons/count".format(self.credentials_manager.mall_id)
		response = self._get(url,payload=payload)
		return response


	def list_coupon(self):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/coupons".format(self.credentials_manager.mall_id)
		response = self._get(url,payload=payload)
		return response

	def create_coupon(self,
					coupon_name,
					benefit_type,
					issue_type,
					available_period_type,
					available_site,
					available_scope,
					available_product,
					available_category,
					available_amount_type,
					available_coupon_count_by_order,
					**rest
					):

		"""
		Creates a coupon

		Parameters:
			Required
				- coupon_name : name of coupon
				- benefit_type : benefit type (A: flat discount, B: percentage discount)
				- issue_type : issue type of coupon (M)
				- available_period_type : available date type of coupon (F: general period, R: dependent on coupon issuance date, M: until end of current month)
				- available_site : available site (W: web only, M: mobile only, use both W and M for web and mobile)
				- available_scope : available scope (P: coupon available only for product, O: coupon available for order)
				- available_product : products that the following coupon can use (U: no restrictions, I: apply only products listed in available_product_list, E: exclude products listed in available_product_list)
				- available_category : categories that the following coupon can use (U: no restrictions, I: apply only categories listed in available_product_list, E: exclude products listed in available_product_list)
				- available_amount_type : When the coupon can be applied (E: before payment discount, I: after payment discount)
				- available_coupon_count_by_order : Max number of coupon that can be used per order
		"""

		request = {}
		payload = {}
		discountType = None
		url = "https://{0}.cafe24api.com/api/v2/admin/coupons".format(self.credentials_manager.mall_id)

		if not coupon_name:
			raise Cafe24Exception(-1,-1,"coupon_name is a required parameter")
		request["coupon_name"] = coupon_name

		if not benefit_type:
			raise Cafe24Exception(-1,-1,"benefit_type is a required parameter")
		request["benefit_type"] = benefit_type

		if not issue_type:
			raise Cafe24Exception(-1,-1,"issue_type is a required parameter")
		request["issue_type"] = issue_type

		if not available_period_type:
			raise Cafe24Exception(-1,-1,"available_period_type is a required parameter")
		request["available_period_type"] = available_period_type

		if not available_site:
			raise Cafe24Exception(-1,-1,"available_site is a required parameter")
		request["available_site"] = available_site

		if not available_scope:
			raise Cafe24Exception(-1,-1,"available_scope is a required parameter")
		request["available_scope"] = available_scope

		if not available_product:
			raise Cafe24Exception(-1,-1,"available_product is a required parameter")
		request["available_product"] = available_product

		if not available_category:
			raise Cafe24Exception(-1,-1,"available_category is a required parameter")
		request["available_category"] = available_category

		if not available_amount_type:
			raise Cafe24Exception(-1,-1,"available_amount_type is a required parameter")
		request["available_amount_type"] = available_amount_type

		if not available_coupon_count_by_order:
			raise Cafe24Exception(-1,-1,"available_coupon_count_by_order is a required parameter")
		request["available_coupon_count_by_order"] = available_coupon_count_by_order

		for (key,value) in rest.items():
			if key == "shop_no":
				payload[key] = value
			else:
				if key == "discount_amount" and discountType == None:
					discountType = key
				elif key == "discount_amount" and discountType != None:
					raise Cafe24Exception(-1,-1,"there can only be one discount type")
				if key == "discount_rate" and discountType == None:
					discountType = key
				elif key == "discount_rate" and discountType != None:
					raise Cafe24Exception(-1,-1,"there can only be one discount type")

				request[key] = value

		payload["request"] = request


		response = self._post(url,payload=json.dumps(payload))
		return response


	def list_issue_coupon(self,coupon_no):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/coupons/{1}/issues".format(self.credentials_manager.mall_id,coupon_no)
		response = self._get(url,payload=payload)
		return response


	def issue_coupon(self,
					coupon_no,
					issued_member_scope,
					**rest):
		payload = {}
		request = {}

		if not coupon_no:
			raise Cafe24Exception(-1,-1,"coupon_no is required")
		request["coupon_no"] = coupon_no
		url = "https://{0}.cafe24api.com/api/v2/admin/coupons/{1}/issues".format(self.credentials_manager.mall_id,coupon_no)

		if not issued_member_scope:
			raise Cafe24Exception(-1,-1,"issued_member_scope")
		request["issued_member_scope"] = issued_member_scope

		for (key,value) in rest.items():
			if key == "shop_no":
				payload[key] = value
			else:
				request[key] = value

		payload["request"] = request

		response = self._post(url,payload=json.dumps(payload))
		return response


	def list_customer_coupon(self,member_id):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/customers/{1}/coupons".format(self.credentials_manager.mall_id,member_id)
		response = self._get(url,payload=payload)
		return response

	def count_customer_coupon(self,member_id):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/customers/{1}/coupons/count".format(self.credentials_manager.mall_id,member_id)
		response = self._get(url,payload=payload)
		return response

	def delete_customer_coupon(self,member_id,coupon_no):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/customers/{1}/coupons/{2}".format(self.credentials_manager.mall_id,member_id,coupon_no)
		response = self._delete(url,payload=payload)
		return response

	def retrieve_points(self,member_id,email,order_id,group_no,start_date,end_date,case,points_category,offset,limit):

		pass

	def modify_points(self,member_id, amount, type, **rest):
		payload = {}
		request = {}

		url = "https://{0}.cafe24api.com/api/v2/admin/points".format(self.credentials_manager.mall_id)


		if len(member_id) > 20 and len(member_id) <= 0:
			raise Cafe24Exception(-1,-1,"member_id has to be between 0 ~ 20 characters")
		request["member_id"] = member_id

		if float(amount) <= 0 and float(amount) > 1000000:
			raise Cafe24Exception(-1,-1,"amount has to be between 0 ~ 1,000,000")
		request["amount"] = amount


		if not (type == "increase" or type == "decrease"):
			raise Cafe24Exception(-1,-1,"point type has to be either 'increase' or 'decrease'")
		request["type"] = type

		for (key,value) in rest.items():
			if key == "shop_no":
				payload[key] = value
			else:
				request[key] = value

		payload["request"] = request

		response = self._post(url,payload=json.dumps(payload))
		return response





	"""

	Scripts!

	"""

	def create_scripttag(self, display_location, **rest):
		payload = {}
		request = {}

		url = "https://{0}.cafe24api.com/api/v2/admin/scripttags".format(self.credentials_manager.mall_id)

		if not display_location:
			raise Cafe24Exception(-1,-1,"display_location is a required parameter")
		request["display_location"] = display_location

		for (key,value) in rest.items():
			if key == "shop_no":
				payload[key] = value
			else:
				request[key] = value
		payload["request"] = request

		response = self._post(url,payload=json.dumps(payload))
		return response

	def update_scripttag(self,script_no,**rest):
		payload = {}
		request = {}

		url = "https://{0}.cafe24api.com/api/v2/admin/scripttags/{1}".format(self.credentials_manager.mall_id,(script_no))

		if not script_no:
			raise Cafe24Exception(-1,-1,"script_no is a required parameter")
		for (key,value) in rest.items():
			if key == "shop_no":
				payload[key] = value
			else:
				request[key] = value
		payload["request"] = request

		response = self._put(url,payload=json.dumps(payload))
		return response

	def retrieve_scripttag(self,script_no):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/scripttags/{1}".format(self.credentials_manager.mall_id,(script_no))
		print(url)
		response = self._get(url,payload=payload)
		return response

	def num_scripttag(self):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/scripttags/count".format(self.credentials_manager.mall_id)
		print(url)
		response = self._get(url,payload=payload)
		return response

	def list_scripttag(self):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/scripttags".format(self.credentials_manager.mall_id)
		response = self._get(url,payload=payload)
		return response

	def delete_scripttag(self,script_no):
		payload = {}
		url = "https://{0}.cafe24api.com/api/v2/admin/scripttags/{1}".format(self.credentials_manager.mall_id,(script_no))
		print(url)
		response = self._delete(url,payload=payload)
		return response
