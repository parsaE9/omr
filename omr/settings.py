# coding: utf-8

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '25nygr&*m8xyaq*wo2g&z4grnt9pxq&#mk_d7_3*4imbp$3#m0'

# DEBUG = os.environ.get('DEBUG', '') == 'True'
DEBUG = True
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']

AUTH_PASSWORD_VALIDATORS = []

ROOT_URLCONF = 'omr.urls'

WSGI_APPLICATION = 'omr.wsgi.application'


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_L10N = True
USE_TZ = True


LOGIN_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/'


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root/')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)


import dj_database_url
DATABASES = {'default': dj_database_url.config(default='sqlite:///database.db')}


INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'hours',
	'accounts',
	'widget_tweaks',
	'anymail',
	'debug_toolbar',
]


MIDDLEWARE = [
	'debug_toolbar.middleware.DebugToolbarMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'whitenoise.middleware.WhiteNoiseMiddleware',
]


TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates')],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]


ANYMAIL = {
	'MAILGUN_API_KEY': os.environ.get('MAILGUN_API', ''),
	'MAILGUN_SENDER_DOMAIN': 'sobhe.ir',
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
DEFAULT_FROM_EMAIL = u'عمر <omr@sobhe.ir>'
