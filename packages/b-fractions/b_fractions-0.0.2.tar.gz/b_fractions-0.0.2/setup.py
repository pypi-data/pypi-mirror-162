from setuptools import _install_setup_requires, setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name = 'b_fractions',
    version = '0.0.2',
    description = 'This module enables you to use fractions within your program',
    long_description = open('README.md', encoding='utf-8').read(),
    long_description_content_type = "text/markdown",
    url = 'https://mahditaz.pythonanywhere.com',
    author = 'Md Mahdi Tajwar Raeed',
    author_email = 'mahdi05tazwar@gmail.com',
    license = 'MIT',
    classifiers = classifiers,
    keywords = ['fractions', 'fraction', 'mathematical', 'calculation', 'simple', 'Mahdi', 'advanced'],
    packages = find_packages(),
    install_requires = [''] 
)