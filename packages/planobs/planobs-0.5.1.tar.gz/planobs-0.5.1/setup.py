# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['planobs']

package_data = \
{'': ['*'], 'planobs': ['data/*', 'data/references/*']}

install_requires = \
['Shapely>=1.8.2,<2.0.0',
 'astroplan>=0.7',
 'astropy>=5.0,<6.0',
 'cligj>=0.7.2,<0.8.0',
 'geopandas>=0.11.0,<0.12.0',
 'lxml>=4.9.1,<5.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'pandas>=1.4.3,<2.0.0',
 'penquins>=2.1.0,<3.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'ztfquery>=1.18.4,<2.0.0']

extras_require = \
{':extra == "slack"': ['Flask>=2.1.3,<3.0.0',
                       'slack>=0.0.2,<0.0.3',
                       'slackeventsapi>=3.0.1,<4.0.0']}

setup_kwargs = {
    'name': 'planobs',
    'version': '0.5.1',
    'description': 'Plan observations with the Zwicky Transient Facility',
    'long_description': '# planobs\nToolset for planning and triggering observations with ZTF. GCN parsing is currently only implemented for IceCube alerts.\n\nIt checks if the object is observable with a maximum airmass on a given date, plots the airmass vs. time, computes two optimal (minimal airmass at night) observations of 300s in g- and r and generate the ZTF field plots for all fields having a reference. There is also the option to create a longer (multiday) observation plan.\n\n[![CI](https://github.com/simeonreusch/planobs/actions/workflows/continous_integration.yml/badge.svg)](https://github.com/simeonreusch/planobs/actions/workflows/continous_integration.yml)\n[![Coverage Status](https://coveralls.io/repos/github/simeonreusch/planobs/badge.svg?branch=main)](https://coveralls.io/github/simeonreusch/planobs?branch=main)\n[![PyPI version](https://badge.fury.io/py/planobs.svg)](https://badge.fury.io/py/planobs)\n[![DOI](https://zenodo.org/badge/512753573.svg)](https://zenodo.org/badge/latestdoi/512753573)\n\n# Requirements\n[ztfquery](https://github.com/mickaelrigault/ztfquery) for checking if fields have a reference.\n\nplanobs requires at least Python 3.8\n\n# Installation\nUsing Pip: ```pip install planobs```.\n\nOtherwise, you can clone the repository: ```git clone https://github.com/simeonreusch/planobs```. This also gives you access to the Slackbot.\n\n# General usage\n```python\nfrom planobs.plan import PlanObservation\n\nname = "testalert" # Name of the alert object\ndate = "2020-05-05" #This is optional, defaults to today\nra = 133.7\ndec = 13.37\n\nplan = PlanObservation(name=name, date=date, ra=ra, dec=dec)\nplan.plot_target() # Plots the observing conditions\nplan.request_ztf_fields() # Checks in which ZTF fields this \n# object is observable and generates plots for them.\n```\nThe observation plot and the ZTF field plots will be located in the current directory/[name]\n![](examples/figures/observation_plot_generic.png)\n\nNote: Checking if fields have references requires ztfquery, which needs IPAC credentials.\n\n# Usage for IceCube alerts\n```python\nfrom planobs.plan import PlanObservation\n\nname = "IC201007A" # Name of the alert object\ndate = "2020-10-08" #This is optional, defaults to today\n# Now no ra and dec values are given, but alertsource \n# is set to \'icecube\'. This enables GCN archive parsing \n# for the alert name. If it is not found, it will use \n#the latest GCN notice (these are automated).\n\nplan = PlanObservation(name=name, date=date, alertsource="icecube")\nplan.plot_target() # Plots the observing conditions\nplan.request_ztf_fields() # Checks in which ZTF fields \n# this object is observable and generates plots for them.\nprint(plan.recommended_field) # In case there is an error in the\n# GCN, you will get the field with the most overlap here\n```\n![](examples/figures/observation_plot_icecube.png)\n![](examples/figures/grid_icecube.png)\n\n# Triggering ZTF\n\n`planobs` can be used for directly scheduling ToO observations with ZTF. \nThis is done through API calls to the `Kowalski` system, managed by the kowalski python manager [penquins](https://github.com/dmitryduev/penquins).\n\nTo use this functionality, you must first configure the connection details. You need both an API token, and to know the address of the Kowalski host address. You can then set these as environment variables:\n\n```bash\nexport KOWALSKI_HOST=something\nexport KOWALSKI_API_TOKEN=somethingelse\n```\n\nYou can then import the Queue class for querying, submitting and deleting ToO triggers:\n\n## Querying\n\n```python\nfrom planobs.api import Queue\n\nq = Queue(user="yourname")\n\nexisting_too_requests = get_too_queues(names_only=True)\nprint(existing_too_requests)\n```\n\n## Submitting\n\n```python\nfrom planobs.api import Queue\n\ntrigger_name = "ToO_IC220513A_test"\n\n# Instantiate the API connection\nq = Queue(user="yourname")\n\n# Add a trigger to the internal submission queue.\n# If not specified otherwise, validity_window_end_mjd\n# is computed from the exposure time\n\nq.add_trigger_to_queue(\n    trigger_name=trigger_name,\n    validity_window_start_mjd=59719.309333333334,\n    field_id=427,\n    filter_id=1,\n    exposure_time=300,\n)\n\nq.submit_queue()\n\n# Now we verify that our trigger has been successfully submitted\n\nexisting_too_requests = get_too_queues(names_only=True)\nprint(existing_too_requests)\nassert trigger_name in existing_too_requests\n```\n\n## Deleting\n```python\nfrom planobs.api import Queue\n\nq = Queue(user="yourname")\n\ntrigger_name = "ToO_IC220513A_test"\n\nres = q.delete_trigger(trigger_name=trigger_name)\n```\n\n# Citing the code\n\nIf you make use of this code, please cite it! A DOI is provided by Zenodo, which can reference both the code repository and specific releases:\n\n[![DOI](https://zenodo.org/badge/512753573.svg)](https://zenodo.org/badge/latestdoi/512753573)\n\n# Contributors\n\n* Simeon Reusch [@simeonreusch](https://github.com/simeonreusch)\n* Robert Stein [@robertdstein](https://github.com/robertdstein)',
    'author': 'Simeon Reusch',
    'author_email': 'simeon.reusch@desy.de',
    'maintainer': 'Simeon Reusch',
    'maintainer_email': 'simeon.reusch@desy.de',
    'url': 'https://github.com/simeonreusch/planobs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
