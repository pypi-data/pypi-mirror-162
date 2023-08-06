from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup_args = dict(
     name='ShynaProcess',
     version='0.39',
     packages=find_packages(),
     author="Shivam Sharma",
     author_email="shivamsharma1913@gmail.com",
     description="Shyna Backend Functionality Package For phase one processing",
     long_description=long_description,
     long_description_content_type="text/markdown",
    )

install_requires = [
    "setuptools",
    "wheel",
    'requests',
    'nltk',
    'feedparser',
    'certifi',
    'ShynaTime',
    'google_speech',
    'ShynaDatabase',
    'googlesearch-python',
    'wikipedia',
    'sox',
    'python-telegram-bot',
    'IMDbPY',
    'wget'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
