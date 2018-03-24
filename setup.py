from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='infraboxcli',
      version='0.6.0',
      url='https://github.com/infrabox/cli',
      description='Command Line Interface for InfraBox',
      long_description=readme(),
      author='infrabox',
      license='MIT',
      packages=['infraboxcli',
                'infraboxcli.dashboard',
                'pyinfrabox',
                'pyinfrabox.infrabox',
                'pyinfrabox.badge',
                'pyinfrabox.docker_compose',
                'pyinfrabox.markup',
                'pyinfrabox.testresult'],
      install_requires=[
          'future', 'jsonschema', 'requests', 'colorama', 'socketIO_client', 'pyyaml', 'PyJWT', 'cryptography'
      ],
      classifiers=[
	         'Development Status :: 4 - Beta',
	         'Intended Audience :: Developers',
	         'Topic :: Software Development :: Build Tools',
	         'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      scripts=['bin/infrabox'],
      include_package_data=True,
      zip_safe=False)
