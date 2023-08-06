from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='tantanbasic',
    version='0.0.1',
    description='Day la test thu vien tinh toan 2 so',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='tantan',
    author_email='tanxuantan16@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='tantanbasic',
    packages=find_packages(),
    install_requires=['']
)