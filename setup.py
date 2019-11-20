from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='infraboxcli',
      version='2.0',
      url='https://github.com/infrabox/cli',
      description='Command Line Interface for InfraBox',
      long_description=readme(),
      author='infrabox',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          "lockfile",
          "python-daemon",
          "appdirs",
          "urllib3==1.24",
          "unittest-xml-reporting",
          "PyYAML",
          "inquirer",
          "future",
          "colorama",
          "pyjwt",
          "click==7.0",
          "requests==2.21.0",
          "tabulate",
          "socketIO_client",
          'jsonschema',
          'cryptography'
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      scripts=['bin/infrabox',
               'bin/infrabox-client',
               'bin/infrabox-daemon',
               'bin/infrabox-bash-autocompletion'],
      include_package_data=True,
      zip_safe=False)
