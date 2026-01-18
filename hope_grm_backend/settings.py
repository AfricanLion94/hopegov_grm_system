import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'replace-this-with-your-own-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['grm.hbiagroexport.com', 'www.grm.hbiagroexport.com']  # Allow local access for frontend

# =========================
# INSTALLED APPS
# =========================
INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',  # For handling CORS (frontend-backend communication)

    # Your custom apps
    'grm',
]

# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings (allow frontend to connect)
CORS_ALLOWED_ORIGINS = [
    "http://grm.hbiagroexport.com",  # If running frontend on Live Server
    "http://grm.hbiagroexport.com",
    "http://grm.hbiagroexport.com",  # If needed
]

# =========================
# URLS & TEMPLATES
# =========================
ROOT_URLCONF = 'hope_grm_backend.urls'

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

WSGI_APPLICATION = 'hope_grm_backend.wsgi.application'

# =========================
# DATABASE
# =========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'owkmpnzj_grm_db',  # e.g., grm_db
        'USER': 'owkmpnzj_grm',
        'PASSWORD': 'hopegov2026@',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
# =========================
# PASSWORD VALIDATION
# =========================
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

# =========================
# INTERNATIONALIZATION
# =========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =========================
# STATIC FILES
# =========================
#STATIC_URL = '/static/'
#STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
#STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# =========================
# MEDIA FILES (for file uploads)
# =========================
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/owkmpnzj/grm.hbiagroexport.com/media'

# =========================
# DEFAULT AUTO FIELD
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# REST FRAMEWORK
# =========================
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# Production Security Settings (add these for SSL and security)
SECURE_SSL_REDIRECT = True  # Redirects HTTP to HTTPS
SESSION_COOKIE_SECURE = True  # Ensures session cookies are only sent over HTTPS
CSRF_COOKIE_SECURE = True  # Ensures CSRF cookies are only sent over HTTPS

# Static Files Settings (for serving CSS/JS/images in production)
STATIC_URL = '/static/'  # URL path for static files
STATIC_ROOT = '/home/owkmpnzj/grm.hbiagroexport.com/hope_grm_backend/staticfiles'  # Full server path to static files (adjust 'yourusername' to your cPanel username)