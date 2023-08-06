# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['network3_perseus']

package_data = \
{'': ['*'], 'network3_perseus': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'hedera-sdk-py>=2.15.0,<3.0.0',
 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['network3_perseus = network3_perseus.script:run']}

setup_kwargs = {
    'name': 'network3-perseus',
    'version': '0.1.94',
    'description': 'Generating and applying intent-based Network configuration from Hedera',
    'long_description': '# perseus\nNetwork Device Configuration from Hedera Hashgraph Intent\n\n## Setting up guestshell\n### Enable guestshell\n```console\nswitch# guestshell enable\n```\nWait until the guestshell becomes active\n\n### Resize guestshell diskspace\n```console\nswitch# conf t\nswitch(config)# guestshell resize rootfs 2000\nswitch(config)# guestshell resize memory 2688\nswitch(config)# guesthshell reboot\n```\n\n### Update DNS\n```console\n[cisco@guestshell ~] $ sudo vi /etc/resolv.conf\nnameserver <dns server IP address>\ndomain <domain that matches NX-OS configured domain>\n```\n\n## Install Python 3.8\n```console\n[cisco@guestshell ~] $ sudo yum -y install epel-release\n[cisco@guestshell ~] $ sudo yum -y update\n[cisco@guestshell ~] $ sudo yum -y groupinstall "Development Tools"\n[cisco@guestshell ~] $ sudo yum -y install openssl-devel bzip2-devel libffi-devel xz-devel\n```\n### Confirm GCC\n```console\n[cisco@guestshell ~] $ gcc --version\ngcc (GCC) 4.8.5 20150623 (Red Hat 4.8.5-39)\n```\n### Install Python 3.8.12\n```console\n[cisco@guestshell ~] $ sudo yum -y install wget\n[cisco@guestshell ~] $ wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz\n[cisco@guestshell ~] $ tar xvf Python-3.8.12.tgz\n[cisco@guestshell ~] $ cd Python-3.8*/\n[cisco@guestshell ~] $ ./configure --enable-optimizations\n[cisco@guestshell ~] $ sudo make altinstall\n```\n\n### Confirm install\n```console\n[cisco@guestshell ~]$ python3.8 --version\nPython 3.8.12\n[cisco@guestshell ~] $ rm -rf Python-3.8*/\n[cisco@guestshell ~] $ rm Python-3.8.12.tgz\n```\n\n### Add Python to the Path\n\n### Cleanup\n```\n[cisco@guestshell ~] $ rm -rf Python-3.8.12\n[cisco@guestshell ~] $ rm Python-3.8.12.tgz\n```\n\n## Upgrade pip\n```console\n[cisco@guestshell ~] $ /usr/bin/python -m pip install --upgrade pip\n```\n\n## Install Java JDK\n```console\n[cisco@guestshell ~] $ curl https://download.oracle.com/java/18/latest/jdk-18_linux-x64_bin.rpm --output jdk-18_linux-x64_bin.rpm\n[cisco@guestshell ~] $ sudo rpm -Uvh jdk-18_linux-x64_bin.rpm\n[cisco@guestshell ~] $ cat <<EOF | sudo tee /etc/profile.d/jdk18.sh\nexport JAVA_HOME=/usr/java/default\nexport PATH=\\$PATH:\\$JAVA_HOME/bin\nEOF\n[cisco@guestshell ~] $ source /etc/profile.d/jdk18.sh\n[cisco@guestshell ~] $ rm jdk-18_linux-x64_bin.rpm\n```\n\n### Verify Java\n```console\n[cisco@guestshell ~] $ java -version\njava version "18.0.1.1" 2022-04-22\nJava(TM) SE Runtime Environment (build 18.0.1.1+2-6)\nJava HotSpot(TM) 64-Bit Server VM (build 18.0.1.1+2-6, mixed mode, sharing)\n```\n\n## Setup Network3 Perseus\n### Install Network3_Perseus\npip install the package\n```console\n[cisco@guestshell ~] $ python3.8 -m pip install network3_perseus\n```\n### setup call_clid.py\n```console\n[cisco@guestshell ~] $ sudo vi call_clid.py\nimport sys\nfrom cli import *\n\nif sys.argv[1] == "show running-config":\n  output = cli("show running-config")\nelse:\n  output = clid(sys.argv[1])\nprint(output)  \n:wq\n```\n\n### setup cli_configure.py\n```console\n[cisco@guestshell ~] $ sudo vi cli_configure.py\nimport sys\nfrom cli import *\nconfiguration = sys.argv[1]\ncli(configuration)\n:wq\n```\n\n## Configure Network3 Medusa\n### Configure Java\n```console\n[cisco@guestshell ~] $ OPERATOR_ID={ Hedera account id }\n[cisco@guestshell ~] $ OPERATOR_PRIVATE_KEY={ Hedera private key }\n```\n\n### (Optional)\nExport your Webex Room and Webex token to send alerts to Webex when Network3 Medusa writes data to Hedera\nexport WEBEX_ROOM="Webex room id"\nexport WEBEX_TOKEN="Webex token id"',
    'author': 'John Capobianco',
    'author_email': 'ptcapo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
