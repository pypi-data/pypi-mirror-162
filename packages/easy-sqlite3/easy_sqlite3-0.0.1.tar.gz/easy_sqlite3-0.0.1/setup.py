from setuptools import setup, find_packages

classifiers = ['Development Status :: 5 - Production/Stable',
                'Operating System :: Microsoft :: Windows',
                'Intended Audience :: Information Technology', 
                'License :: OSI Approved :: MIT License',
                'Programming Language :: Python :: 3']

setup(
    name='easy_sqlite3',
    version='0.0.1',
    description='Simple Python Library to make sqlite commands simpler and more elegant',
    long_description=open('README.txt').read() + "\n\n" + open('CHANGELOG.txt').read(),
    author='Muhammed Rayan Savad',
    author_email='muhammedrayan.official@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='sqlite3',
    packages=find_packages(),
    install_requires=['']
)
