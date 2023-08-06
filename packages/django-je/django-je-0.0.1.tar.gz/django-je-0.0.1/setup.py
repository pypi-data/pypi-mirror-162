from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Education',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
]

setup(
    name='django-je',
    version='0.0.1',
    description='This is a simple library that performs a colect packages of django and more.',
    long_description=open('README.md').read() + '\n\n' +
    open('CHANGELOG.txt').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/',
    author='JAMAL EL KHDADI',
    author_email='jamalelkhdadi@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='cli',
    packages=find_packages(),
    install_requires=['typer']
)
