try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='proxycurl',
    version='0.0.11',
    python_requires='==3.*,>=3.7.0',
    author='Nubela',
    author_email='tech@nubela.co',
    description='Proxycurl is a set of tools designed to serve as plumbing for fresh and processed data in your application',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=['proxycurl', 'proxycurl.asyncio', 'proxycurl.gevent', 'proxycurl.twisted'],
    package_dir={"": "."},
    package_data={},
    install_requires=[],
    project_urls={
        "Homepage":  "https://nubela.co/proxycurl",
        "Bug Tracker":  "https://github.com/nubelaco/proxycurl-linkedin-scraper/issues",
        "Documentation": "https://nubela.co/proxycurl/docs",
        "Source Code": "https://github.com/nubelaco/proxycurl-linkedin-scraper",
    },
    extras_require={"asyncio": ["aiohttp==3.*,>=3.7.4", "asyncio==3.*,>=3.4.3"], "dev": ["jinja2==3.*,>=3.0.1"], "gevent": ["gevent==21.*,>=21.1.1", "requests==2.*,>=2.25.0"], "twisted": ["treq==21.*,>=21.5.0", "twisted==21.*,>=21.7.0"]},
)
