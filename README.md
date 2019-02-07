HardCheck
==============================

Checkpointing/Restore Framework for Reconfigurable Systems

Copyright (C) 2016, Shinya Takamaeda-Yamazaki

E-mail: shinya\_at\_is.naist.jp


License
==============================

Apache License 2.0
(http://www.apache.org/licenses/LICENSE-2.0)


What's HardCheck?
==============================



Installation
==============================

Requirements
--------------------

- Python: 2.7, 3.4 or later

Python3 is recommended.

- Icarus Verilog: 0.9.7 or later

Install on your platform. For exmple, on Ubuntu:

    sudo apt-get install iverilog

- Jinja2: 2.8 or later

Install on your python environment by using pip:

    pip install jinja2

- Pyverilog: 1.0.6 or later

Install from pip (or download and install from GitHub):

    pip install pyverilog
    
- Veriloggen: 0.6.1 or later

Install from pip (or download and install from GitHub):

    pip install veriloggen
    
- IPgen: 0.2.0 or later

Install from pip (or download and install from GitHub):

    pip install ipgen

Options
--------------------

- pytest: 2.8.2 or later
- pytest-pythonpath: 0.7 or later

These softwares are required for running the tests in tests and examples:

    pip install pytest pytest-pythonpath

Install
--------------------

Install HardCheck:

    python setup.py install


Getting Started
==============================


Publication
==============================


Related Project
==============================

[Pyverilog](https://github.com/PyHDI/Pyverilog)
- Python-based Hardware Design Processing Toolkit for Verilog HDL

[Veriloggen](https://github.com/PyHDI/veriloggen)
- A library for constructing a Verilog HDL source code in Python

[IPgen](https://github.com/PyHDI/ipgen)
- IP-core package generator for AXI4/Avalon
