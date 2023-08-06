from setuptools import setup, find_packages


setup(
    name='MT5pytrader',
    version='0.51',
    description = "MT5 Trader",
    license='MIT',
    author="Raimi Azeez Babatunde",
    author_email='raimiazeez26@gmail.com',
    packages=['MT5pytrader'],
    url='https://github.com/raimiazeez26/MT5pytrader',
    keywords=['MT5pytrader', 'python', 'Metatrader5', 'MT5', 'algotrading',
             'autroading'],
    install_requires=[
          'MetaTrader5',
      ],
    zip_safe = False

)