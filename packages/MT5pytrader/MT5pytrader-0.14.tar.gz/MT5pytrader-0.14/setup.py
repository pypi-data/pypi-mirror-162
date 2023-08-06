from setuptools import setup, find_packages


setup(
    name='MT5pytrader',
    version='0.14',
    description = "MT5 Trader",
    license='MIT',
    author="Raimi Azeez Babatunde",
    author_email='raimiazeez26@gmail.com',
    packages=find_packages(),
    install_requires=[
          'MetaTrader5==5.0.37',
      ],
    zip_safe = False

)

