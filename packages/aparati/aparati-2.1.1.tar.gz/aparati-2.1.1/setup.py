from setuptools import setup
setup(
    name='aparati',
    packages=['Scripts'],
    version='2.1.1',
    license='MIT',
    description=' this tools is for download video from aparat.com (an iranian website)',
    author='mehdi',
    author_email='thisisnotreall@dont.com',
    url='https://github.com/mehdigdr/aparat-dl',
    download_url='https://github.com/mehdigdr/aparat-dl/archive/v2.1.1tar.gz',
    keywords=['AparatDL', 'aparat', 'aparat_dowoloader'],
    install_requires=[
        "webdriver-manager == 3.8.2",
        'beautifulsoup4',
        'certifi',
        'chardet',
        'idna',
        'requests',
        'soupsieve',
        'urllib3',
        'youtube-dl',
        "requests",
        "beautifulsoup4",
        "selenium",
        "setuptools",
        "beautifulsoup4",
        "certifi",
        " chardet",
        "idna",
        "requests",
        "soupsieve",
        "urllib3",
        "youtube-dl",

    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        'Development Status :: 5 - Production/Stable',
        "Operating System :: OS Independent",
        'License :: OSI Approved :: MIT License',

    ],
    entry_points={

        'console_scripts': [
            'aparati = Scripts.aparat_dl:main',
        ],
    },

)
