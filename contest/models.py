from django.db import models
from Payment import Payment
import string
import random
from hashlib import sha256
from django.utils import timezone
from django.db.models import Max, Count

from contest import checker

KEY_LEN = 20
SALT = '1uGq'
def random_string(len):
	return ''.join(random.choice(string.digits+string.ascii_letters) for _ in range(len))

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
	
	def over(self):
		return (self.end_date < timezone.now())

	def evaluate(self, input, output):
		return checker.longest_cycle_evaluate(input, output)
		

#	full_name = models.CharField()
#	short = models.CharField()

def get_contest_prize(contest):
	count = Contestant.objects.filter(contest=contest, authorized=True).count()
	fee = contest.entrance_fee
	return count * fee - fee/2

class TaskLongestCycle(Contest):
	class Meta:
		proxy = True

	cur_type = 'longest_cycle'

	def correct_task(self):
		return self.type == self.cur_type

	def __unicode__(self):
		if self.correct_task():
			return '#{}'.format(self.id)
		else:
			return '#{} (not realy {})'.format(self.id, cur_type)

def hashstr(x):
	return sha256((x).encode()).hexdigest()
		

class Contestant(models.Model):
	hash = models.CharField(max_length=70, default='')
	entrance_address = models.CharField(max_length=70, default='')
	
	authorized = models.BooleanField(default=False)
	withdraw_transaction = models.CharField(max_length=100)

	contest = models.ForeignKey('Contest')

	@staticmethod
	def hash_from_key(key):
		return hashstr(key)

	def generate_key(self):
		key = random_string(KEY_LEN)
		self.hash = self.hash_from_key(key)
		return key

	def get_new_address(self):
		p = Payment()
		addr = p.get_new_address()
		self.entrance_address = addr
		return addr

	def get_received(self):
		p = Payment()
		return p.get_address_received(self.entrance_address)
	
	def withdraw(self, amount, address):
		p = Payment()
		return p.withdraw(amount, address)
		

class Input(models.Model):
	contest = models.ForeignKey('Contest')
	text = models.TextField()

class Submission(models.Model):
	@staticmethod
	def init_from_form(input, contestant, text, contest):
		hash = hashstr(text)
		
		try:
			score = contest.evaluate(input.text, text)
		except Exception as e:
			score = 0 
			#raise e 		##### !!!!

		if not contest.running():
			return None
		
		s = Submission(input=input, contestant=contestant, text=text, hash=hash, score=score)
		return s

	input = models.ForeignKey('Input')
	contestant = models.ForeignKey('Contestant')
	date = models.DateTimeField(auto_now=True)
	score = models.FloatField()
	text = models.TextField()
	hash = models.CharField(max_length=70)

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

	contestants = Contestant.objects.filter(contest=contest)
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

