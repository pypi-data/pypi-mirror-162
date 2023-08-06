from distutils.core import setup

with open('E:/Python/NoConfusion/readme.md', encoding='utf-8') as readme:
    LONG_DESCRIPTION = readme.read()


setup(
    name='noconfusion',
    packages=['E:/Python/NoConfusion/src/NoConfusion'],
    license='MIT',
    description='A library for no longer have confusion in python',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
)