# coding: utf8

from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.shortcuts import render, resolve_url
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

eusername = lambda email: email.strip()[:30].lower()


class SignupForm(forms.ModelForm):
	email = forms.EmailField(required=True)
	last_name = forms.CharField(required=True, max_length=30)

	class Meta:
		fields = ('last_name', 'email', 'password')
		model = User

	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(username=eusername(email)).count():
			raise forms.ValidationError('این رایانامه قبلا ثبت شده است.')
		return email

	def save(self, commit=True):
		user = super(SignupForm, self).save(commit=False)
		user.username = eusername(user.email)
		user.set_password(user.password)
		if commit:
			user.save()
		return user


def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			form.save()
			authenticated = authenticate(username=eusername(request.POST['email']), password=request.POST['password'])
			if authenticated:
				login(request, authenticated)

			redirect_to = request.GET.get('next', '')
			if redirect_to and is_safe_url(url=redirect_to, host=request.get_host()):
				return HttpResponseRedirect(redirect_to)

			return HttpResponseRedirect(resolve_url(settings.LOGIN_REDIRECT_URL))
	else:
		form = SignupForm()
	return render(request, 'registration/signup.html', {'form': form})


class LoginForm(forms.ModelForm):
	class Meta:
		fields = ('email', 'password')
		model = User

	def clean(self):
		username = eusername(self.cleaned_data.get('email', ''))
		password = self.cleaned_data.get('password', '')

		user = authenticate(username=username, password=password)
		if user is None:
			raise forms.ValidationError('رایانامه یا گذرواژه اشتباه است.')
		elif not user.is_active:
			raise forms.ValidationError('حساب شما فعال نیست.')

		self.authenticated_user = user
		return self.cleaned_data


def email_login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			login(request, form.authenticated_user)

			redirect_to = request.GET.get('next', '')
			if redirect_to and is_safe_url(url=redirect_to, allowed_hosts=settings.ALLOWED_HOSTS):
				return HttpResponseRedirect(redirect_to)

			return HttpResponseRedirect(resolve_url(settings.LOGIN_REDIRECT_URL))
	else:
		form = LoginForm()
	return render(request, 'registration/login.html', {'form': form, 'next': request.GET.get('next', '')})
