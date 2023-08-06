from distutils.core import setup

f = open("README.rst")

setup(
  name = 'dynamic_variables',
  version = '2.0.0',
  description = 'Change variables dynamically in runtime with the help of a simple GUI',
  long_description = f.read(),
  long_description_content_type = "text/x-rst",
  packages = ['dynamic_variables'],
  license='MIT',
  author = 'Cahid Enes Keles',
  author_email = 'cahideneskeles54@gmail.com',
  url = 'https://github.com/cahidenes/dynamic_variables',
  download_url = 'https://github.com/cahidenes/dynamic_variables/archive/refs/tags/v2.0.0.tar.gz',
  keywords = ['dynamic', 'variable', 'config', 'gui', 'change', 'runtime'],
  install_requires=[
          'appdirs', 'customtkinter'
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],
)
