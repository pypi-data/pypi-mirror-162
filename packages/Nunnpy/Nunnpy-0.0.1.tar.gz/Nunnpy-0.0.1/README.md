urllib3
Build status on Travis Build status on AppVeyor Documentation Status Coverage Status PyPI version Bountysource Gitter
urllib3 is a powerful, sanity-friendly HTTP client for Python. Much of the Python ecosystem already uses urllib3 and you should too. urllib3 brings many critical features that are missing from the Python standard libraries:

Thread safety.
Connection pooling.
Client-side SSL/TLS verification.
File uploads with multipart encoding.
Helpers for retrying requests and dealing with HTTP redirects.
Support for gzip and deflate encoding.
Proxy support for HTTP and SOCKS.
100% test coverage.
urllib3 is powerful and easy to use:

>>> import urllib3
>>> http = urllib3.PoolManager()
>>> r = http.request('GET', 'http://httpbin.org/robots.txt')
>>> r.status
200
>>> r.data
'User-agent: *\nDisallow: /deny\n'
Installing
urllib3 can be installed with pip:

$ pip install urllib3
Alternatively, you can grab the latest source code from GitHub:

$ git clone git://github.com/urllib3/urllib3.git
$ python setup.py install
Documentation
urllib3 has usage and reference documentation at urllib3.readthedocs.io.

Contributing
urllib3 happily accepts contributions. Please see our contributing documentation for some tips on getting started.

Maintainers
@theacodes (Thea Flowers)
@SethMichaelLarson (Seth M. Larson)
@haikuginger (Jesse Shapiro)
@lukasa (Cory Benfield)
@sigmavirus24 (Ian Cordasco)
@shazow (Andrey Petrov)
👋

Sponsorship
If your company benefits from this library, please consider sponsoring its development.

Sponsors include:

Google Cloud Platform (2018-present), sponsors @theacodes’s work on an ongoing basis
Abbott (2018-present), sponsors @SethMichaelLarson’s work on an ongoing basis
Akamai (2017-present), sponsors @haikuginger’s work on an ongoing basis
Hewlett Packard Enterprise (2016-2017), sponsored @Lukasa’s work on urllib3