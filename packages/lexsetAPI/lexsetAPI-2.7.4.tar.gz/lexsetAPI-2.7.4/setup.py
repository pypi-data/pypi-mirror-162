from setuptools import setup


setup(name='lexsetAPI',
      version='2.7.4',
      author='F. Bitonti',
      author_email='Francis@lexset.ai',
      license='Apache 2.0',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3'
      ],
      packages=['lexsetAPI'],
      install_requires=[
          'pyjson',
          'PyYAML',
          'pyBase64',
          'requests'
      ]
)
