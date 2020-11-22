from setuptools import setup

APP = ['geekhub/geekhub.py']
DATA_FILES = [
    'Resources/alert.png',
    'Resources/notification.png',
]
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps'],
    'iconfile': 'Resources/logo.icns',
}

VERSION = '0.1.3'

setup(
    name='geekhub',
    version=VERSION,
    description='A little statusbar for to geekhub',
    license='MIT',
    author='Leetao',
    author_email='leetao@gmail.com',
    packges=['geekhub'],
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    install_requires=['requests', 'BeautifulSoup4', 'rumps'],
    setup_requires=['py2app'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Chinese',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.7',
    ]
)
