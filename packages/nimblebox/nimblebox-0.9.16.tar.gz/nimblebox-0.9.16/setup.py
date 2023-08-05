# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nimblebox',
 'nimblebox.framework',
 'nimblebox.hyperloop',
 'nimblebox.lib',
 'nimblebox.nbxlib',
 'nimblebox.relics',
 'nimblebox.sub_utils']

package_data = \
{'': ['*'],
 'nimblebox': ['__pycache__/hyperloop/.git', 'assets/*'],
 'nimblebox.framework': ['protos/*']}

install_requires = \
['Jinja2==3.0.3',
 'dill==0.3.4',
 'grpcio==1.43.0',
 'mypy-protobuf==3.2.0',
 'protobuf==3.20.1',
 'python-json-logger==2.0.2',
 'randomname>=0.1.3,<0.2.0',
 'requests>=2.25.1,<3.0.0',
 'tabulate==0.8.9']

extras_require = \
{'serving': ['fastapi>=0.78.0,<0.79.0', 'uvicorn>=0.18.2,<0.19.0']}

setup_kwargs = {
    'name': 'nimblebox',
    'version': '0.9.16',
    'description': 'ML Inference 🥶',
    'long_description': '<a href="https://nimblebox.ai/" target="_blank"><img src="./assets/built_at_nbx.svg" align="right"></a>\n\n# 🏖️ Nbox\n\n`nbox` is NimbleBox.ai\'s official SDK.\n\n> The entire purpose of this package is to make using ML 🥶.\n\n```\npip install nbox\n```\n\n## 🔥 Usage\n\n`nbox` provides first class support API for all NimbleBox.ai infrastructure (NBX-Build, Jobs, Deploy) and services (NBX-Workspaces) components. Write jobs using `nbox.Operators`:\n\n```python\nfrom nbox import Operator\nfrom nbox.nbxlib.ops import Magic\n\n# define a class object\nweekly_trainer: Operator = Magic()\n\n# call your operators\nweekly_trainer(\n  pass_values = "directly",\n)\n\n# confident? deploy it to your cloud\nweekly_trainer.deploy(\n  job_id_or_name = "magic_jobs",\n  schedule = Schedule(4, 30, [\'fri\']) # schedule like humans\n)\n```\n\nDeploy your machine learning or statistical models:\n\n```python\nfrom nbox import Model\nfrom transformers import AutoModelForSequenceClassification, AutoTokenizer\n\n# define your pre and post processing functions\ndef pre(x: Dict):\n  return AutoTokenizer(**x)\n\n# load your classifier with functions\nmodel = AutoModelForSequenceClassification.from_pretrained("distill-bert")\nclassifier = Model(model, pre = pre)\n\n# call your model\nclassifier(f"Is this a good picture?")\n\n# get full control on exporting it\nspec = classifier.torch_to_onnx(\n  TorchToOnnx(...)\n)\n\n# confident? deploy it your cloud\nurl, key = classifier.deploy(\n  spec, deployment_id_or_name = "classification"\n)\n\n# use it anywhere\npred = requests.post(\n  url,\n  json = {\n    "text": f"Is this a good picture?"\n  },\n  header = {"Authorization": f"Bearer {key}"}\n).json()\n```\n\n# 🧩 License\n\nThe code in thist repo is licensed as [Apache License 2.0](./LICENSE). Please check for individual repositories for licenses.\n',
    'author': 'NBX Research',
    'author_email': 'research@nimblebox.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NimbleBoxAI/nbox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
