# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['psex', 'psex.funcs', 'psex.weaks']

package_data = \
{'': ['*']}

install_requires = \
['pocx>=0.2.2,<0.3.0', 'pyyaml>=6.0,<7.0']

setup_kwargs = {
    'name': 'psex',
    'version': '0.1.1',
    'description': 'A simple, fast and powerful password scanner engine tool was built by antx.',
    'long_description': '# psex\nA simple, fast and powerful password scanner engine tool was built by antx.\n\n## Description\npsex is a simple, fast and powerful password scanner engine tool was built by antx. psex also \nsupport some useful features, which like fofa search and parse assets to verify. psex has been built in some weak username and password. \n\n## Install\n\n```bash\npip3 install psex\n```\n\n## Usage\n\n### PSE Sample:\n\n```python\n# Title: xxxxxxx\n# Author: antx\n# Email: wkaifeng2007@163.com\n\nfrom loguru import logger\nfrom redis import Redis\nfrom psex import ScannerEngine\nfrom psex.funcs.assetio import AssetIO\nfrom psex.weaks import weak_passwords\n\n\nclass Scanner(ScannerEngine):\n    def __init__(self):\n        super(Scanner, self).__init__()\n\n    @logger.catch(level=\'ERROR\')\n    def is_connected(self, connection):\n        """\n        check if the connection is connected.\n        """\n        try:\n            connection.ping()\n            return True\n        except Exception as e:\n            return False\n\n    @logger.catch(level=\'ERROR\')\n    def create_connect(self, *args):\n        """\n        \n        create a connection.\n        \n        """\n        connection = Redis(host=args[0], port=args[1], password=args[3], db=0, socket_connect_timeout=self.timeout,\n                           socket_timeout=self.timeout)\n        return connection\n\n    @logger.catch(level=\'ERROR\')\n    def dia(self):\n        asset_io = AssetIO()\n        ips = asset_io.get_file_assets(\'source_redis.csv\')\n        passwords = weak_passwords(\'redis\')\n        for password in passwords:\n            for ip_port in ips:\n                ip_port = ip_port.strip()\n                ip = ip_port.split(\':\')[0]\n                port = int(ip_port.split(\':\')[1])\n                logger.debug(f\'Connecting to {ip} ......\')\n                logger.warning(f\'Testing {ip_port} with password: "{password}" !\')\n                result = self.poc(ip, port, \'\', password)\n                if result:\n                    asset_io.save2file(\'redis_success\', ip, port, \'\', password)\n\n\nif __name__ == \'__main__\':\n    ds = Scanner()\n    ds.dia()\n```\n',
    'author': 'antx-code',
    'author_email': 'wkaifeng2007@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/antx-code/psex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
