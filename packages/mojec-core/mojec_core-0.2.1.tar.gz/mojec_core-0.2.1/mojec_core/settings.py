import os, sys

from dotenv import load_dotenv
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials

from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent

load_dotenv()

AUTH_USER_MODEL = 'app.User'

SECRET_KEY = 'da)(@*#Uhubjindu*(!@#$#@nfoinond-ahp*nen2@=*u)!g8m9pthdg'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


def db(key):
    return os.getenv(key)

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': "django.db.backends.sqlite3",
            'NAME': "test.db"
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': db("DB_ENGINE"),
            'NAME': db('POSTGRES_DB'),
            'USER': db('POSTGRES_USER'),
            'PASSWORD': db('POSTGRES_PASSWORD'),
            'HOST': db('DB_HOST'),
            'PORT': db('DB_PORT'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] %(asctime)s %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console', ],
        'level': 'DEBUG'
    },
    'loggers': {
        'django.request': {
            'handlers': [
                'console',
            ],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}
SAFE_DELETE_FIELD_NAME = "deletedAt"
SAFE_DELETE_CASCADED_FIELD_NAME = "deletedViaCascade"
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 15,
    'PAGINATE_BY_PARAM': 'limit',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'uid',
    'USER_ID_CLAIM': 'uid',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=12),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

CORS_ALLOW_ALL_ORIGINS = True
REDIS_CONFIG_KEY = "CONFIGURATIONS"


firebase_credentials = credentials.Certificate(PACKAGE_DIR / "firebase.json")
firebase_admin.initialize_app(firebase_credentials)

ONE_SIGNAL_APP_ID = "8bf62455-7eb2-46fb-84a3-c4a3e99d1b61"
ONE_SIGNAL_REST_API_KEY = "MzliODFkZGUtYmRmZS00OGE1LThmM2MtYWVjNDU3ZjM5ZTA0"
ONE_SIGNAL_USER_AUTH_KEY = "MzliODFkZGUtYmRmZS00OGE1LThmM2MtYWVjNDU3ZjM5ZTA0"
