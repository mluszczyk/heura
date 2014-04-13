from django.db import models
from payment import Payment
from django.utils import timezone
from django.db.models import Max, Count
from heurasite.settings import CONTESTANT_KEY_LEN
from heura.taskcontrollers import controllers
from heura.utils import random_string, hash_string

# Create your models here.

class Contest(models.Model):
	announce_date = models.DateTimeField()
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()
	entrance_fee = models.FloatField()

	type = models.CharField(max_length=300)

	def __unicode__(self):
		return '{} #{}'.format(self.type, self.id)

	def running(self):
		return (self.start_date < timezone.now() < self.end_date)
	
	def controller(self):
		return controllers[self.type]

	def over(self):
		return (self.end_date < timezone.now())

	def evaluate(self, input, output):
		return self.controller().evaluate(input, output)

	def get_contestants(self):
		count = self.contestant_set.filter(authorized=True).count()
		return count

	def get_prize(self):
		count = self.get_contestants()
		fee = self.entrance_fee
		return count * fee

class Contestant(models.Model):
	hash = models.CharField(max_length=70, default='')
	entrance_address = models.CharField(max_length=70, default='')
	
	authorized = models.BooleanField(default=False)
	withdraw_transaction = models.CharField(max_length=100)

	contest = models.ForeignKey('Contest')

	def generate_key(self):
		key = random_string(CONTESTANT_KEY_LEN)
		self.hash = hash_string(key)
		return key

	def get_new_address(self):
		p = Payment()
		addr = p.get_new_address()
		self.entrance_address = addr
		return addr

	def get_received(self):
		if self.entrance_address == '':
			return 0.0
		p = Payment()
		return p.get_address_received(self.entrance_address)
	
	def withdraw(self, amount, address):
		p = Payment()
		return p.withdraw(amount, address)

class Input(models.Model):
	contest = models.ForeignKey('Contest')
	text = models.FileField(upload_to='upload/input/%m%d/%H%M%S')

	def get_str(self):
		self.text.open()
		return self.text.read().decode()
			

class Submission(models.Model):
	input = models.ForeignKey('Input')
	contestant = models.ForeignKey('Contestant')
	date = models.DateTimeField(auto_now=True)
	score = models.FloatField()
	text = models.FileField(upload_to='upload/submit/%m%d/%H%M%S')
	hash = models.CharField(max_length=70)

	def set_from_form(self, input, contestant, contest):
		hash = hash_string(self.get_str())
		
		try:
			self.score = contest.evaluate(input.get_str(), self.get_str())
		except Exception as e:
			self.score = 0 
			raise e 		##### !!!!

		if not contest.running():
			return None
		
		self.input = input
		self.contestant = contestant
		self.hash = hash

	def get_str(self):
		self.text.open()
		return self.text.read().decode()

def get_contest_results(contest):
	subs = Submission.objects.filter(input__contest=contest)
	best = dict()
	last = dict()

	for sub in subs:
		key = (sub.input.pk, sub.contestant.pk)
		if key in best:
			best[key] = max(best[key], sub.score)
		else:
			best[key] = sub.score

		ck = sub.contestant.pk
		if ck in last:
			last[ck] = max(last[ck], sub.date)
		else:
			last[ck] = sub.date

	inputs = list(Input.objects.filter(contest=contest).values('pk'))

	contestants = contest.contestant_set.filter(contest=contest, authorized=True)
	results = []
	for con in contestants:
		user = [ ]
		for input in inputs:
			key = (input['pk'], con.pk)
			if key in best:
				user.append(best[key])
			else:
				user.append(0)

		if con.pk in last:
			date = last[con.pk]
		else:
			date = contest.start_date

		results.append([con.hash, sum(user), date] + user)

	results.sort(key=lambda x: (-x[1], x[2]))
	return results

