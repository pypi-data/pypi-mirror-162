#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from setuptools import setup, find_packages


setup(
    name='MT5pytrader',
    version='0.12',
    description = "mt5",
    license='MIT',
    author="Raimi Azeez Babatunde",
    author_email='raimiazeez26@gmail.com',
    packages=find_packages('MT5pytrader'),
    install_requires=[
          'MetaTrader5==5.0.37',
      ],
    zip_safe = False

)

