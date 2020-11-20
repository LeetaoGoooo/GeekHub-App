from setuptools import setup

APP = ['app.py']

OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps'],
    'iconfile': 'geekhub.ico',
}

VERSION='0.1.2'

setup(
    name='geekhub',
    version=VERSION,
    description='A little statusbar for to geekhub',
    license='MIT',
    author='Leetao',
    author_email='leetao@gmail.com',
    packges=['geekhub'],
    app=APP,
    options={'py2app': OPTIONS},
    install_requires=['requests','BeautifulSoup4','pyqt5'],
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