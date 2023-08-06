# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tinyticker', 'tinyticker.waveshare_lib', 'tinyticker.web']

package_data = \
{'': ['*'],
 'tinyticker.web': ['templates/*',
                    'templates/css/*',
                    'templates/images/*',
                    'templates/js/*']}

install_requires = \
['Flask>=2.0.2,<3.0.0',
 'Pillow>=9.0.0,<10.0.0',
 'RPi.GPIO>=0.7.0,<0.8.0',
 'cryptocompare>=0.7.5,<0.8.0',
 'matplotlib>=3.5.1,<4.0.0',
 'mplfinance>=0.12.7-alpha.17,<0.13.0',
 'packaging>=21.2,<22.0',
 'pandas>=1.3.5,<2.0.0',
 'qrcode>=7.3.1,<8.0.0',
 'spidev>=3.5,<4.0',
 'yfinance>=0.1.63,<0.2.0']

entry_points = \
{'console_scripts': ['tinyticker = tinyticker.__main__:main',
                     'tinyticker-web = tinyticker.web.__main__:main']}

setup_kwargs = {
    'name': 'tinyticker',
    'version': '0.2.1',
    'description': 'A tiny Raspberry Pi powered ePaper ticker.',
    'long_description': '<h1 align="center">🚀 tinyticker 🚀</h5>\n<h3 align="center"><img src="https://i.imgur.com/2mF86LQ.png" width=500><img src="https://i.imgur.com/BPiGmxo.png" height=600 align=right></h3>\n<h5 align="center">size doesn\'t matter</h5>\n<p align="center">\n  <a href="https://pypi.org/project/tinyticker/"><img src="https://img.shields.io/pypi/v/tinyticker"></a>\n  <a href="./LICENSE.md"><img src="https://img.shields.io/badge/license-MIT-blue.svg"></a>\n</p>\n\n`tinyticker` uses a Raspberry Pi zero W and a small ePaper display to periodically display a stock or crypto chart.\n\nA `flask` web interface is created to set the ticker options and control the Raspberry Pi.\n\n`tinyticker` uses the [`cryptocompare`](https://github.com/lagerfeuer/cryptocompare) API to query the crypto price information, you\'ll need to get yourself a free [API key](https://min-api.cryptocompare.com/pricing). As well as the [`yfinance`](https://github.com/ranaroussi/yfinance) package to get the stock financial data.\n\n## Hardware\n\nShopping list:\n\n- [Raspberry Pi Zero WH](https://www.adafruit.com/product/3708)\n- One of these ePaper displays:\n  - [Waveshare ePaper 2.13in Black & White](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT)\n  - [Waveshare ePaper 2.13in Black, White & Red](<https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_(B)>)\n  - [Waveshare ePaper 2.13in Black, White & Yellow](<https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_(C)>)\n- A micro sd card\n\n## Recommended setup\n\nFlash the latest iso from [tinyticker-images](https://github.com/loiccoyle/tinyticker-images) onto a SD card and you should be good to go.\n\n## Manual setup\n\nI highly recommend using [comitup](https://github.com/davesteele/comitup) to setup the networking on your RPi.\n\n- Write the `comitup` [image](https://davesteele.github.io/comitup/latest/comitup-lite-img-latest.html) to your sd card\n- Boot up the RPi and setup the networking\n- ssh into your RPi, you\'ll probably want to change the password while you\'re at it\n- Enable the [SPI interface](https://www.raspberrypi-spy.co.uk/2014/08/enabling-the-spi-interface-on-the-raspberry-pi/)\n- (Optional) rename the hostname of your RPi by editing the `/etc/hostname` and `/etc/hosts` file\n- (Optional) rename the Wifi AP name by editing the `/etc/comitup.conf` file\n- Install the `BCM2835` driver:\n  ```sh\n  curl http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz | tar xzv\n  cd bcm2835-1.60/\n  ./configure\n  make\n  make install\n  ```\n- Install `pip`:\n  ```sh\n  sudo apt install python3-pip\n  ```\n- Install dependency requirements:\n  ```sh\n  sudo apt install libatlas-base-dev libopenjp2-7 libtiff5 libxml2-dev libxslt1-dev\n  ```\n- Install `tinyticker` (the `CFLAGS` variable is required for `RPi.GPIO` to install):\n  ```sh\n  pip install tinyticker\n  ```\n- To setup `tinyticker` to start on boot, copy over the [`systemd` unit files](./systemd) and enable them.\n- On boot, a qrcode linking to the `flask` app will be flashed on the display\n- Leave a star, reboot and HODL !\n\nNote: the Raspberry Pi zero isn\'t very fast so be patient :)\n',
    'author': 'Loic Coyle',
    'author_email': 'loic.coyle@hotmail.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/loiccoyle/tinyticker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
