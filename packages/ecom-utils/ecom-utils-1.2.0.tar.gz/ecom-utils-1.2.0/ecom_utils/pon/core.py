import json
import requests

ENDPOINT_STAGE = 'https://devapp8.ecomchaco.com.ar'
ENDPOINT_PROD = 'https://devapp8.ecomchaco.com.ar'

API_ENDPOINTS = {
	'get_token_application': '_endpointbase_/ponapitest/oauth/access_token',
	'obtener_jurisdicciones': '_endpointbase_/ponapitest/rest/ConsultaJurisdicciones',
	'obtener_oficinas': '_endpointbase_/ponapitest/rest/ConsultaOficinas'
}

class Pon():
	def __init__(self, username, password, client_id, mode_stage=True):
		self.username = username
		self.password = password
		self.client_id = client_id
		self.mode_stage = mode_stage

		self.access_token = None
		self.scope = None
		self.refresh_token = None
		self.user_guid = None

	def get_endpoint_base(self):
		if self.mode_stage:
			return ENDPOINT_STAGE
		return ENDPOINT_PROD

	def get_token_application(self):
		url = API_ENDPOINTS['get_token_application'].replace("_endpointbase_", self.get_endpoint_base())
		headers = {
			"client_id": self.client_id,
			"grant_type": "password",
			"scope": "FullControl",
			'username': self.username,
			'password': self.password,
		}

		response = requests.post(url, headers=headers)
		if response.status_code == 200:
			data = response.json()
			self.access_token = data.get("access_token", None)
			self.scope = data.get("scope", None) 
			self.refresh_token = data.get("refresh_token", None)
			self.user_guid = data.get("user_guid", None)
	
	def obtener_jurisdicciones(self):
		if self.access_token is None:
			self.get_token_application()
			if self.access_token is None:
				return None
		jurisdicciones = []

		url = API_ENDPOINTS['obtener_jurisdicciones'].replace("_endpointbase_", self.get_endpoint_base())

		headers = {
			"Authorization": self.access_token,
			"Content-Type": "application/json"
		}

		data = json.dumps({
			"Orden": 0,
		    "Id": 0,
		    "Nombre": ""
		})
		response = requests.post(url, headers=headers, data=data)
		if response.status_code == 200:
			data = response.json()
			jurisdicciones = data["SDTJurisdicciones"]["Jurisdicciones"]
		return jurisdicciones

	def obtener_oficinas(self, jurId):
		if self.access_token is None:
			self.get_token_application()
			if self.access_token is None:
				return None
		oficinas = []

		url = API_ENDPOINTS['obtener_oficinas'].replace("_endpointbase_", self.get_endpoint_base())

		headers = {
			"Authorization": self.access_token,
			"Content-Type": "application/json"
		}

		data = json.dumps({
			"JurId": jurId
		})
		response = requests.post(url, headers=headers, data=data)

		if response.status_code == 200:
			data = response.json()
			oficinas = data["SDTOficinas"]["Oficinas"]
		return oficinas