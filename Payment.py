import json
from http.client import HTTPSConnection
from dobraheura.settings import PAYMENT_API_KEY as AK

server = 'dogeapi.com'
url = '/wow'

def dict_to_url(data):
	return '&'.join(map(lambda x: '{}={}'.format(*x), data.items()))

class Payment(object):
	def request(self, **kwargs):
		conn = HTTPSConnection(server)
		full_url = '{}/?{}'.format(url, dict_to_url(kwargs))
		conn.request('GET', full_url)
		
		r1 = conn.getresponse()
		if r1.status != 200 or r1.reason != "OK": raise IOError

		data = r1.read().decode()
		conn.close()

		return json.loads(data)

	def get_balance(self): return self.request(api_key=AK, a='get_balance')
	def get_new_address(self): return self.request(api_key=AK, a='get_new_address')
	def get_my_addresses(self): return self.request(api_key=AK, a='get_my_addresses')
	def get_address_received(self, addr):
		return self.request(api_key=AK, a='get_address_received', \
		payment_address=addr)
	def withdraw(self, amount, addr):
		return self.request(api_key=AK, a='withdraw', amount=amount, payment_address=addr)

	def get_difficulty(self): return self.request(a='get_difficulty')
	def get_current_block(self): return self.request(a='get_current_block')
		
	
	
