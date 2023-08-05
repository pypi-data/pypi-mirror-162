from setuptools import setup, find_packages

VERSION = '0.2.1'
DESCRIPTION = 'Mojec core package'
LONG_DESCRIPTION = 'Package that holds all models and common ' \
                   'functions/classes of Mojec project'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="mojec_core",
    version=VERSION,
    author="Folayemi Bello",
    author_email="<bello.folayemi.az@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    package_data={'': ['firebase.json']},
    include_package_data=True,
    install_requires=["django", "djangorestframework",
                      "djangorestframework-simplejwt", "drf-yasg",
                      "python-dotenv", "django-safedelete", "firebase-admin",
                      "django-cors-headers", "redis", "onesignal-sdk"],
    # add any
    # additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'mojec'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",

    ]
)
