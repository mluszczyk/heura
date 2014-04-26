from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('heura.views',
	url(r'^$', 'index'),
	url(r'^contest/(\w+)$', 'contest', name='contest'),
	url(r'^contestant/(\w+)$', 'contestant', name='contestant'),

	url(r'^get_key/(\w+)$', 'get_key', name='get_key'),
	url(r'^get_input/(\d+)(?:/(\w*))?$', 'get_input', name='get_input'),
	url(r'^submit/(\d+)(?:/(\w*))?$', 'submit', name='submit'),
	url(r'^withdraw/(\w+)$', 'withdraw', name='withdraw'),

    url(r'^i18n/', include('django.conf.urls.i18n')),


) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
