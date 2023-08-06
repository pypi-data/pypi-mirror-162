from setuptools import setup

with open("README.md", "r") as fh:
    description = fh.read()

setup(
    name="Odoo_API_Library",
    version="1.0.0.2",
    description="Store user access token for one-time-login",
    long_description=description,
    long_description_content_type="text/markdown",
    packages=['Odoo_API_Library'],
    author="Han Zaw Nyein",
    author_email="hanzawnyineonline@gmail.com",
    zip_safe=False,
    install_requires=['PyJWT', 'simplejson']
)
