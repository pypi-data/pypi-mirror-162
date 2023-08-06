from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Environment :: Console',
    'Framework :: IPython',
    'Natural Language :: English',
    'Topic :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'
]

setup(
    name='StoaCalculator',
    version='1.1.0',
    description='Stoa Calculator is a powerful calculator that have everything you need to do any kind of calculations!',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    project_urls={
        'Documentation': 'https://pypi.org/project/StoaCalculator/',
        'Say Thanks!': 'https://saythanks.io/to/jorgeeldis',
        'Source': 'https://github.com/jorgeeldis/StoaCalculator',
        'Tracker': 'https://github.com/jorgeeldis/StoaCalculator/issues',
    },
    author='Jorge Eldis Gonzalez',
    author_email='jorgeeldisg30@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='calculator education algebra calculus trigonometry arithmetic university',
    packages=find_packages(),
    install_requires=['matplotlib', 'numpy', 'sympy'],
    python_requires='>=3'
)
