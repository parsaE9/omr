from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView
from hours.views import *
from django.urls import path, include


urlpatterns = [
	# url(r'^$', RedirectView.as_view(url='sobhe/'), name='home'),
	path('', RedirectView.as_view(url='sobhe/'), name='home'),
	# url(r'^admin/', admin.site.urls),
	path('admin', admin.site.urls),
	# url(r'^accounts/', include('accounts.urls')),
	path('accounts/', include('accounts.urls')),


	url(r'^user/?$', login_required(UserDetail.as_view()), name='user'),
	url(r'^calendar/?$', login_required(CalendarView.as_view()), name='calendar'),

	url(r'^works/create/?$', login_required(WorkCreate.as_view()), name='work-create'),
	url(r'^works/update/(?P<pk>[\d]+)/?$', login_required(WorkUpdate.as_view()), name='work-update'),
	url(r'^works/delete/(?P<pk>[\d]+)/?$', login_required(WorkDelete.as_view()), name='work-delete'),

	url(r'^notes/create/?$', login_required(NoteCreate.as_view()), name='note-create'),
	url(r'^notes/update/(?P<pk>[\d]+)/?$', login_required(NoteUpdate.as_view()), name='note-update'),
	url(r'^notes/delete/(?P<pk>[\d]+)/?$', login_required(NoteDelete.as_view()), name='note-delete'),
	url(r'^notes/email/(?P<pk>[\d]+)/?$', note_email, name='note-email'),

	url(r'^(?P<slug>[\w\d-]+)/stats/?$', login_required(OrganizationStats.as_view()), name='organization'),
	url(r'^(?P<slug>[\w\d-]+)/hours/?$', login_required(OrganizationHours.as_view()), name='organization-hours'),
	url(r'^(?P<slug>[\w\d-]+)/import/?$', work_import, name='organization-import'),
	url(r'^(?P<slug>[\w\d-]+)/notes/?$', login_required(EmployeeNotes.as_view()), name='employee-notes'),
	url(r'^(?P<slug>[\w\d-]+)/?$', login_required(EmployeeHours.as_view()), name='employee'),
	url(r'^(?P<slug>[\w\d-]+)/(?P<employee>[\w\d@%\.+-]+)/?$', login_required(EmployeeHours.as_view()), name='employee-admin'),
]

if settings.DEBUG:
	import debug_toolbar
	urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls))] + urlpatterns
