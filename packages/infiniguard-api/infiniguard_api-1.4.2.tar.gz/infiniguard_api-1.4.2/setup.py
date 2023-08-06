
SETUP_INFO = dict(
    name = 'infiniguard_api',
    version = '1.4.2',
    author = 'Maxim Kigel',
    author_email = 'mkigel@infinidat.com',

    url = None,
    license = 'BSD',
    description = """Infiniguard API""",
    long_description = """Infiniguard API prototype""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'apispec==3.3.0',
'configobj',
'ddt',
'dictdiffer',
'dnspython==1.16.0',
'flask-apispec==0.9.0',
'Flask==1.1.2',
'iba-install',
'icmplib==1.0.4',
'infi.caching',
'ipaddress',
'logbook==1.1.0',
'marshmallow==3.6.1',
'pendulum==1.4.2',
'pyroute2==0.5.12',
'represent',
'schematics==2.0.1',
'setuptools',
'sqlalchemy',
'structlog',
'webargs==5.5.1',
'wrapt',
'xmltodict'
],
    namespace_packages = [],

    package_dir = {'': 'src'},
    package_data = {'': [
'flask_apispec/static/*',
'flask_apispec/templates/*'
]},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [
'infiniguard_api = infiniguard_api.scripts.infiniguard_api_gui:main',
'infiniguard_api_postinstall = infiniguard_api.scripts.utils:postinstall',
'infiniguard_api_preuninstall = infiniguard_api.scripts.utils:preuninstall'
],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

