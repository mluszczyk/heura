# Create your views here.

from contest.models import *
from contest.forms import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response, render
from django.utils import timezone
from django.core.urlresolvers import reverse

def index(request): 
	 contests = Contest.objects.all()
	 return render_to_response('index.html', {'contests': contests})

def render_contest(request, contest, contestant=None, key='', 
		is_contestant=False, authorized=False, contestant_received=0):
		
	inputs = Input.objects.filter(contest__pk=contest.id)
	submissions = Submission.objects.filter(input__contest__pk=contest.id).order_by('pk')

	now = timezone.now()
	over = contest.over()
	running = contest.running()

	if over:
		results = get_contest_results(contest)
	else:
		results = []

	if over and authorized and results[0][0]==contestant.hash: # authorized, so len(results)>0
		won = True
		withdraw_transaction = contestant.withdraw_transaction
	else:
		won = False
		withdraw_transaction = ''

	if contest.entrance_fee == 0:
		free = True
	else:
		free = False

	prize = get_contest_prize(contest)
	num_contestants = get_contestants(contest)

	to_pack = ( 'contest', 'contestant', 'authorized', 'key', 'contestant_received', 'is_contestant',
		'over', 'now', 'running', 'inputs', 'submissions', 'results', 'won', 'withdraw_transaction',
		'prize', 'num_contestants', 'free')
	packed = dict()
	for x in to_pack:
		packed[x] = locals()[x]	

	return render_to_response('contest.html', packed)

def contest(request, contest_id):
	contest = Contest.objects.get(pk=contest_id)
	return render_contest(request, contest)

def auth_by_key(key):
	contestant_filter = Contestant.objects.filter(hash=Contestant.hash_from_key(key))
	if contestant_filter.count() != 1:
		raise PermissionDenied

	contestant = contestant_filter.get()
	contest = contestant.contest

	return (contest, contestant)

def contestant(request, key):
	contest, contestant = auth_by_key(key)

	if contestant.authorized:
		contestant_received = 'ok'
		authorized = True
	else:
		contestant_received = contestant.get_received()
		
		if contestant_received >= contest.entrance_fee:
			contestant.authorized = True
			contestant.save()
			authorized = True
		else:
			authorized = False

	is_contestant = True

	to_pack = ('contest', 'contestant', 'key', 'authorized', 'contestant_received', 'is_contestant')
	packed = dict()
	for x in to_pack:
		packed[x] = locals()[x]

	return render_contest(request, **packed)


def get_input(request, input, key=''):
	input_filter = Input.objects.filter(pk=input)
	
	if input_filter.count() != 1:
		raise Http404

	input = input_filter.get()
	contest = input.contest

	try:
		contest_check, contestant = auth_by_key(key)
		auth = (contest_check == contest and contestant.authorized)

	except PermissionDenied:
		auth = False

	if contest.over() or (contest.running() and auth):
		return HttpResponse(input.text)
	else:
		raise PermissionDenied

def submit(request, input, key):
	# should throw error, if contest is over

	if request.method == 'POST':
		form = SubmitForm(request.POST)
		if form.is_valid():
			contest, contestant = auth_by_key(key)
			input_filter = Input.objects.filter(pk=input)

			if input_filter.count() != 1:
				raise Http404

			inputobj = input_filter.get()

			if inputobj.contest != contest:
				raise PermissionDenied	# should be checked in model

			text = form.cleaned_data['text']

			s = Submission.init_from_form(input=inputobj, contestant=contestant, contest=contest, text=text)
			s.save()

			return HttpResponseRedirect(reverse('contestant', args=[ key ]))
	
	else: 
		form = SubmitForm()
	
	return render(request, 'submit_form.html', { 'form': form, 'input': input, 'key': key })
	
def withdraw(request, key):
	if request.method == 'POST':
		form = WithdrawForm(request.POST)
		if form.is_valid():
			contest, contestant = auth_by_key(key)

			if contestant.withdraw_transaction != '':
				#return HttpResponse('wt: {}'.format(contestant.withdraw_transaction))	###
				raise PermissionDenied

			results = get_contest_results(contest)
			if contestant.hash != results[0][0]:
				#return HttpResponse('not winer')
				raise PermissionDenied

			# plz don't crash :P
			contestant.withdraw_transaction = 'processing...'
			contestant.save()
			amount = get_contest_prize(contest)
			x = contestant.withdraw(amount, form.cleaned_data['address'])
			
			contestant.withdraw_transaction = x
			contestant.save()

			return HttpResponseRedirect(reverse('contestant', args=[ key ]))
	else:
		form = WithdrawForm()
	
	return render(request, 'withdraw_form.html', { 'form': form, 'key': key })

def get_key(request, contest_id):
	c = Contestant(contest=Contest.objects.get(pk=contest_id))
	if c.contest.entrance_fee:
		c.get_new_address()
	key = c.generate_key()
	c.save()
	return render_to_response('get_key.html', {'key': key})

