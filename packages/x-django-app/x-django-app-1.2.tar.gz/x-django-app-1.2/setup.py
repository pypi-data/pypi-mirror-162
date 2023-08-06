from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

setup(
    name="x-django-app",
    version="1.2",
    description="A Python package to get weather reports for any location.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/XecusM/x-django-app",
    author="Mohamed Aboel-fotouh",
    author_email="abo.elfotouh@live.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["x_django_app"],
    include_package_data=True,
    install_requires=['django', 'djangorestframework', 'langdetect'],
)
