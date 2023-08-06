
from setuptools import setup, find_packages
setup(
    name='Mensajes-Crackbana',
    version='5.0',
    description='Un paquete para saludar y despedir',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jesús Cabana',
    author_email='jesuscabana111@gmail.com',
    url='https://www.hektor.dev',
    license_files=['LICENSE'],
    packages=find_packages(),
    scripts=[],
    test_suite='tests',
    install_requires=[paquete.strip()
                      for paquete in open("requirements.txt").readlines()],
    classifiers=[
        'Environment :: Web Environment',
        'License :: Free For Home Use',
        'Natural Language :: English',
        'Operating System :: Microsoft',
        'Programming Language :: Python :: 3.9',
        'Topic :: Database',
        
        
    ],
)
