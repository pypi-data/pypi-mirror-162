# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ansys',
 'ansys.fluent.visualization',
 'ansys.fluent.visualization.matplotlib',
 'ansys.fluent.visualization.pyvista']

package_data = \
{'': ['*']}

install_requires = \
['ansys-fluent-core>=0.10,<1.0',
 'ipyvtklink>=0.2.2',
 'matplotlib>=3.5.1',
 'pyside6>=6.2.3',
 'pyvista>=0.33.2',
 'pyvistaqt>=0.7.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.0,<5.0'],
 ':python_version <= "3.9"': ['vtk>=9.0.3']}

setup_kwargs = {
    'name': 'ansys-fluent-visualization',
    'version': '0.4.1',
    'description': 'A python wrapper for ansys Fluent visualization',
    'long_description': 'PyFluent Visualization\n======================\n|pyansys| |pypi| |GH-CI| |MIT| |black|\n\n.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC\n   :target: https://docs.pyansys.com/\n   :alt: PyAnsys\n\n.. |pypi| image:: https://img.shields.io/pypi/v/ansys-fluent-visualization.svg?logo=python&logoColor=white\n   :target: https://pypi.org/project/ansys-fluent-visualization\n   :alt: PyPI\n\n.. |GH-CI| image:: https://github.com/pyansys/pyfluent-visualization/actions/workflows/ci_cd.yml/badge.svg\n   :target: https://github.com/pyansys/pyfluent-visualization/actions/workflows/ci_cd.yml\n   :alt: GH-CI\n\n.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg\n   :target: https://opensource.org/licenses/MIT\n   :alt: MIT\n\n.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat\n   :target: https://github.com/psf/black\n   :alt: Black\n\nOverview\n--------\nThe PyFluent Visualization project provides post-processing and visualization\ncapabilities for PyFluent using `pyvista <https://docs.pyvista.org/>`_ and\n`matplotlib <https://matplotlib.org/>`_.\n\nDocumentation and Issues\n------------------------\nPlease see the latest release `documentation <https://fluentvisualization.docs.pyansys.com>`_\npage for more details.\n\nPlease feel free to post issues and other questions at `PyFluent Visualization Issues\n<https://github.com/pyansys/pyfluent-visualization/issues>`_.  This is the best place\nto post questions and code.\n\nInstallation\n------------\nThe ``ansys-fluent-visualization`` package currently supports Python 3.7 through Python\n3.10 on Windows and Linux.\n\nIf you\'re using Python 3.10, install the vtk package from .whl file\n`here in Windows <https://github.com/pyvista/pyvista-wheels/raw/main/vtk-9.1.0.dev0-cp310-cp310-win_amd64.whl>`_ or\n`here in Linux <https://github.com/pyvista/pyvista-wheels/raw/main/vtk-9.1.0.dev0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl>`_.\n\nInstall the latest release from `PyPI\n<https://pypi.org/project/ansys-fluent-visualization/>`_ with:\n\n.. code:: console\n\n   pip install ansys-fluent-visualization\n\nAlternatively, install the latest from `pyfluent-visualization GitHub\n<https://github.com/pyansys/pyfluent-visualization>`_ via:\n\n.. code:: console\n\n   pip install git+https://github.com/pyansys/pyfluent-visualization.git\n\n\nIf you plan on doing local "development" of PyFluent with Git, then install\nwith:\n\n.. code:: console\n\n   git clone https://github.com/pyansys/pyfluent-visualization.git\n   cd pyfluent-visualization\n   pip install pip -U\n   pip install -e .\n\nDependencies\n------------\nYou will need a locally installed licensed copy of ANSYS to run Fluent, with the\nfirst supported version being Ansys 2022 R2.\n\nGetting Started\n---------------\n\nBasic Usage\n~~~~~~~~~~~\n\n.. code:: python\n\n   from ansys.fluent.visualization.pyvista import Graphics\n   graphics = Graphics(session=session)\n   temperature_contour = graphics.Contours["contour-temperature"]\n   temperature_contour.field = "temperature"\n   temperature_contour.surfaces_list = ["in1", "in2", "out1"]\n   temperature_contour.display("window-1")\n\nAbove code assumes that a PyFluent session has already been created and a Fluent case\nwith input parameters has been set up. The `Analyzing Your Results\n<https://fluentvisualization.docs.pyansys.com/users_guide/postprocessing.html>`_ in\nthe user guide has a complete example.\n\nLicense and Acknowledgments\n---------------------------\n``PyFluent Visualization`` is licensed under the MIT license.\n\nThis module, ``ansys-fluent-visualization`` makes no commercial claim over Ansys\nwhatsoever. This tool extends the functionality of ``Fluent`` by adding a Python\ninterface to the Fluent without changing the core behavior or license of the original\nsoftware.  The use of the interactive Fluent control of ``PyFluent Visualization`` requires\na legally licensed local copy of Ansys.\n\nTo get a copy of Ansys, please visit `Ansys <https://www.ansys.com/>`_.\n',
    'author': 'ANSYS, Inc.',
    'author_email': 'ansys.support@ansys.com',
    'maintainer': 'PyAnsys developers',
    'maintainer_email': 'pyansys.maintainers@ansys.com',
    'url': 'https://github.com/pyansys/pyfluent-visualization',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
