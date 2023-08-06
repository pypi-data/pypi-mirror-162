from setuptools import setup

setup(
    name="telepathy",
    version='2.1.6',
    author='Jordan Wildon',
    author_email='j.wildon@pm.me',
    packages=['telepathy'],
    url='https://pypi.python.org/pypi/telepathy/',
    license='LICENSE.txt',
    description='An OSINT toolkit for investigating Telegram chats.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    py_modules=['telepathy'],
    install_requires=[
        'click == 7.1.2',
        'telethon == 1.24.0',
        'pandas == 1.4.2',
        'colorama == 0.4.3',
        'alive_progress == 2.4.1',
        'beautifulsoup4 == 4.9.3',
    ],
    entry_points='''
        [console_scripts]
        telepathy=telepathy.telepathy:cli
    ''',
)
