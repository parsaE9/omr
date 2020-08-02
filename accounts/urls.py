from django.conf.urls import url
from accounts.views import *
from django.contrib.auth.views import (
    LoginView, LogoutView, logout_then_login,
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.urls import path

urlpatterns = [
    url(r'^signup/?$', signup, name='signup'),
    # path('signup', accounts.views.signup, name='signup'),

    url(r'^login/?$', email_login, name='login'),
    # path('login/?', accounts.views.email_login, name='login'),

    url(r'^logout/?$', logout_then_login, name='logout'),

    # url(r'^password/change/$', PasswordChangeView.as_view(success_url='done/'), name='password_change'),
    path('password/change/', PasswordChangeView.as_view(success_url='done/'), name='password_change'),

    # url(r'^password/change/done/$', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password/change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),

    # url(r'^password/reset/$', PasswordResetView.as_view(success_url='done/'), name='password_reset'),
    path('password/reset/', PasswordResetView.as_view(success_url='done/'), name='password_reset'),

    # url(r'^password/reset/done/$', PasswordResetDoneView, name='password_reset_done'),
    # doesn't work with parsa@gmail.com
    path('password/reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),

    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(success_url='complete/'), name='password_reset_confirm'),
    url(r'^password/reset/complete/$', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
