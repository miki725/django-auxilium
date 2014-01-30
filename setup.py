import os
from setuptools import setup
from django_auxilium import __version__, __author__


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])

    if filepaths:
        return {package: filepaths}
    else:
        return None


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name             = 'django-auxilium',
    version          = __version__,
    author           = __author__,
    author_email     = 'miroslav@miki725.com',
    description      = ('Django utility app to help in Django development'),
    long_description = read('README.rst') + read('LICENSE.rst'),
    license          = 'MIT',
    keywords         = 'django',
    url              = 'https://github.com/miki725/django-auxilium',
    packages         = get_packages('django_auxilium'),
    data_files       = get_package_data('django_auxilium'),
    install_requires = ['django'],
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
)
