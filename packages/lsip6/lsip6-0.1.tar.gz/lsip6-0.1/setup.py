from setuptools import setup

setup(name='lsip6',
      version='0.1',
      description='Find link-local IPv6 neighbors on point-to-point links',
      url='https://git.sr.ht/~martijnbraam/lsip6',
      author='Martijn Braam',
      author_email='martijn@brixit.nl',
      license='MIT',
      packages=['lsip6'],
      entry_points={
          'console_scripts': ['lsip6=lsip6.__main__:main'],
      })