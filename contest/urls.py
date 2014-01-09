from django.conf.urls import patterns, include, url

urlpatterns = patterns('contest.views',
	url(r'^$', 'index'),
	url(r'^contest/(\w+)$', 'contest', name='contest'),
	url(r'^contestant/(\w+)$', 'contestant', name='contestant'),

	url(r'^get_key/(\w+)$', 'get_key', name='get_key'),
	url(r'^get_input/(\d+)(?:/(\w*))?$', 'get_input', name='get_input'),
	url(r'^submit/(\d+)(?:/(\w*))?$', 'submit', name='submit'),
	url(r'^withdraw/(\w+)$', 'withdraw', name='withdraw')
)
