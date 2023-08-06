from distutils.core import setup
setup(
  name = 'azuretls',
  packages = ['azuretls'],  
  version = '0.2.12',     
  license='MIT',       
  author = 'Noste',                  
  author_email = 'nooooste@gmail.com',     
  url = 'https://github.com/Noooste/azuretls', 
  download_url = 'https://github.com/Noooste/azuretls/archive/refs/tags/0.2.12.tar.gz',
  keywords = ['TLS', 'API', 'AZURE'],  
  install_requires=[
          'urllib3',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)