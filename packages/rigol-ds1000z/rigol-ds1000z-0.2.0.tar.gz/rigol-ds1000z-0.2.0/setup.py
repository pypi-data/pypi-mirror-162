# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rigol_ds1000z', 'rigol_ds1000z.app', 'rigol_ds1000z.src']

package_data = \
{'': ['*']}

install_requires = \
['PyVISA>=1.11.3,<2.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.2,<2.0.0',
 'si-prefix>=1.2.2,<2.0.0',
 'textual>=0.1.18,<0.2.0']

entry_points = \
{'console_scripts': ['rigol-ds1000z = rigol_ds1000z.cli:main']}

setup_kwargs = {
    'name': 'rigol-ds1000z',
    'version': '0.2.0',
    'description': 'Python library for interfacing with Rigol DS1000Z series oscilloscopes.',
    'long_description': '# rigol-ds1000z\n\n## An oscilloscope user interface that never leaves the terminal.\n\n![RigolDS1000Z_StillScreen](docs/rigol_ds1000z.png)\n\n![Rigol_DS1000Z_Animated](docs/rigol_ds1000z.gif)\n\n## A simple command line tool for grabbing data and pictures.\n\n```shell\nrigol-ds1000z --help\nrigol-ds1000z --visa rsrc --display path/to/file.png\nrigol-ds1000z --visa rsrc --waveform src path/to/file.csv \n```\n\nUnless a VISA resource is specified with the `--visa` argument, the CLI will search for a Rigol DS1000Z series oscilloscope and connect to the first one it finds.\n\nThe CLI can capture and save to file an image of the display (`--display`) or the waveform data of the specified source channel (`--waveform`).\n\n## A compact Python interface for automating test procedures.\n\nSee the provided [examples](examples/) and read the [documentation.](https://amosborne.github.io/rigol-ds1000z/)\n\n```python\nfrom rigol_ds1000z import Rigol_DS1000Z\nfrom rigol_ds1000z import process_display, process_waveform\nfrom time import sleep\n\nwith Rigol_DS1000Z() as oscope:\n    # reset to defaults and print the IEEE 488.2 instrument identifier\n    ieee = oscope.ieee(rst=True)\n    print(ieee.idn)\n\n    # configure channels 1 and 2, the timebase, and the trigger\n    channel1 = oscope.channel(1, probe=1, coupling="AC", offset=3.0, scale=2)\n    channel2 = oscope.channel(2, probe=1, scale=1, display=True)\n    timebase = oscope.timebase(main_scale=200e-6)\n    trigger = oscope.trigger(mode="EDGE", source=2, coupling="DC", level=1.5)\n\n    # send an SCPI commands to setup the math channel\n    oscope.write(":MATH:DISPlay ON")\n    oscope.write(":MATH:OPER SUBT")\n    oscope.write(":MATH:SOUR2 CHAN2")\n    oscope.write(":MATH:SCAL 5")\n    oscope.write(":MATH:OFFS -10")\n\n    # wait three seconds then single trigger\n    sleep(3)\n    oscope.single()\n\n    # capture the display image\n    display = oscope.display()\n    process_display(display, show=True)\n\n    # plot the channel 1 waveform data\n    waveform = oscope.waveform(source=1)\n    process_waveform(waveform, show=True)\n\n```\n\n## Installation instructions and notes to the user.\n\n`pip install rigol-ds1000z`\n\nAvailable on [PyPI](https://pypi.org/project/rigol-ds1000z/). This package uses [PyVISA](https://pyvisa.readthedocs.io/en/1.12.0/introduction/getting.html) to communicate with the oscilloscope, which requires that the user also installs the National Instrument\'s VISA library for their operating system.\n\nThis software has been tested on Windows (Command Prompt and PowerShell), although it should be possible to run in other shells and/or operating systems. For best visual performance, a default of white text on a black background is recommended.\n\nThe software does insert some sleep time on specific commands (such as reset and autoscale) to ensure fluid operation of the oscilloscope. The user may find that they require additional downtime after certain command sequences.\n\n## Software development and references.\n\n[Rigol DS1000Z programming manual.](https://beyondmeasure.rigoltech.com/acton/attachment/1579/f-0386/1/-/-/-/-/DS1000Z_Programming%20Guide_EN.pdf)\n\n| Command Category | Coverage |\n| --- | --- |\n| AUToscale, etc. | YES |\n| ACQuire | no |\n| CALibrate | no |\n| CHANnel | YES |\n| CURSor | no |\n| DECoder | no |\n| DISPlay | YES |\n| ETABle | no |\n| FUNCtion | no |\n| IEEE 488.2 | YES |\n| LA | no |\n| LAN | no |\n| MATH | no |\n| MASK | no |\n| MEASure | no |\n| REFerence | no |\n| STORage | no |\n| SYSTem | no |\n| TIMebase | YES |\n| TRIGger | PARTIAL |\n| WAVeform | YES |\n\n- Package management by [Poetry](https://python-poetry.org/).\n- Automated processing hooks by [pre-commit](https://pre-commit.com/).\n- Code formatting in compliance with [PEP8](https://www.python.org/dev/peps/pep-0008/) by [isort](https://pycqa.github.io/isort/), [black](https://github.com/psf/black), and [flake8](https://gitlab.com/pycqa/flake8).\n- Static type checking in compliance with [PEP484](https://www.python.org/dev/peps/pep-0484/) by [mypy](http://www.mypy-lang.org/).\n- Test execution with random ordering and code coverage analysis by [pytest](https://docs.pytest.org/en/6.2.x/).\n- Automated documentation generation by [sphinx](https://www.sphinx-doc.org/en/master/).\n\nInstalling the development environment requires running the following command sequence.\n\n```shell\npoetry install\npoetry run pre-commit install\n```\n\nIn order for all tests to pass channel 2 must be connected to the calibration square wave.\n',
    'author': 'amosborne',
    'author_email': 'amosborne@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/amosborne/rigol-ds1000z',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
