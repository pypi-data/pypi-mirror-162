# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['aioredis_fastapi']

package_data = \
{'': ['*']}

install_requires = \
['aioredis>=2.0.1,<3.0.0', 'fastapi>=0.79.0,<0.80.0']

setup_kwargs = {
    'name': 'aioredis-fastapi',
    'version': '1.0.0',
    'description': 'aioredis_fastapi is an asynchronous redis based session backend for FastAPI powered applications.',
    'long_description': '================\naioredis_fastapi\n================\n\n.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg\n   :target: https://github.com/wiseaidev/aioredis_fastapi/blob/main/LICENSE\n   :alt: License\n\n.. image:: https://raw.githubusercontent.com/wiseaidev/aioredis_fastapi/main/assets/banner.jpeg\n   :target: https://github.com/wiseaidev/aioredis_fastapi/\n   :alt: Banner\n\n\n\n**aioredis_fastapi** is an asynchronous `redis based session`_ backend for FastAPI powered applications.\n\n🚸This repository is currently under testing, kind of production-ready.🚸\n\n\n🛠️ Requirements\n---------------\n\n**aioredis_fastapi** requires Python 3.9 or above.\n\nTo install Python 3.9, I recommend using `pyenv`_. You can refer to `this section`_ of the readme file on how to install poetry and pyenv into your linux machine.\n\n🚨 Installation\n---------------\n\nWith :code:`pip`:\n\n.. code-block:: console\n\n   python3.9 -m pip install aioredis-fastapi\n\nor by checking out the repo and installing it with `poetry`_:\n\n.. code-block:: console\n\n   git clone https://github.com/wiseaidev/aioredis_fastapi.git && cd aioredis_fastapi && poetry install\n\n\n🚸 Usage\n--------\n\n.. code-block:: python3\n\n   from typing import Any\n   from fastapi import Depends, FastAPI, Request, Response\n   from aioredis_fastapi import (\n       get_session_storage,\n       get_session,\n       get_session_id,\n       set_session,\n       del_session,\n       SessionStorage,\n   )\n\n   app = FastAPI(title=__name__)\n\n\n   @app.post("/set-session")\n   async def _set_session(\n       request: Request,\n       response: Response,\n       session_storage: SessionStorage = Depends(get_session_storage),\n   ):\n       session_data = await request.json()\n       await set_session(response, session_data, session_storage)\n\n\n   @app.get("/get-session")\n   async def _get_session(session: Any = Depends(get_session)):\n       return session\n\n\n   @app.post("/del-session")\n   async def _delete_session(\n       session_id: str = Depends(get_session_id),\n       session_storage: SessionStorage = Depends(get_session_storage),\n   ):\n       await del_session(session_id, session_storage)\n       return None\n\n\n🛠️ Custom Config\n----------------\n\n.. code-block:: python3\n\n   from aioredis_fastapi import settings\n   from datetime import timedelta\n   import random\n\n   settings(\n      redis_url="redis://localhost:6379",\n      session_id_name="session-id",\n      session_id_generator=lambda: str(random.randint(1000, 9999)),\n      expire_time= timedelta(days=1)\n   )\n\n\n🌐 Interacting with the endpoints\n---------------------------------\n\n.. code-block:: python3\n\n   from httpx import AsyncClient\n   import asyncio\n   from config import settings\n\n   async def main():\n       client = AsyncClient()\n       r = await client.post("http://127.0.0.1:8000/set-session", json=dict(a=1, b="data", c=True))\n       r = await client.get("http://127.0.0.1:8000/get-session", cookies={settings().session_id_name: "ssid"})\n       print(r.text)\n       return r.text\n\n   loop = asyncio.new_event_loop()\n   asyncio.set_event_loop(loop)\n   try:\n       loop.run_until_complete(main())\n   finally:\n       loop.close()\n       asyncio.set_event_loop(None)\n\n\n🎉 Credits\n----------\n\nThe following projects were used to build and test :code:`aioredis_fastapi`.\n\n- `python`_\n- `poetry`_\n- `pytest`_\n- `flake8`_\n- `coverage`_\n- `rstcheck`_\n- `mypy`_\n- `pytestcov`_\n- `tox`_\n- `isort`_\n- `black`_\n- `precommit`_\n\n\n👋 Contribute\n-------------\n\nIf you are looking for a way to contribute to the project, please refer to the `Guideline`_.\n\n\n📝 License\n----------\n\nThis program and the accompanying materials are made available under the terms and conditions of the `GNU GENERAL PUBLIC LICENSE`_.\n\n.. _GNU GENERAL PUBLIC LICENSE: http://www.gnu.org/licenses/\n.. _redis based session: https://github.com/duyixian1234/fastapi-redis-session\n.. _Guideline: https://github.com/wiseaidev/aioredis_fastapi/blob/main/CONTRIBUTING.rst\n.. _this section: https://github.com/wiseaidev/frozndict#%EF%B8%8F-requirements\n.. _pyenv: https://github.com/pyenv/pyenv\n.. _poetry: https://github.com/python-poetry/poetry\n.. _python: https://www.python.org/\n.. _pytest: https://docs.pytest.org/en/7.1.x/\n.. _flake8: https://flake8.pycqa.org/en/latest/\n.. _coverage: https://coverage.readthedocs.io/en/6.3.2/\n.. _rstcheck: https://pypi.org/project/rstcheck/\n.. _mypy: https://mypy.readthedocs.io/en/stable/\n.. _pytestcov: https://pytest-cov.readthedocs.io/en/latest/\n.. _tox: https://tox.wiki/en/latest/\n.. _isort: https://github.com/PyCQA/isort\n.. _black: https://black.readthedocs.io/en/stable/\n.. _precommit: https://pre-commit.com/\n',
    'author': 'Mahmoud Harmouch',
    'author_email': 'business@wiseai.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wiseaidev/aioredis_fastapi',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
