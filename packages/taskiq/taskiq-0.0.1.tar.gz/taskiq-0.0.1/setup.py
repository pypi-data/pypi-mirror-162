# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taskiq',
 'taskiq.abc',
 'taskiq.brokers',
 'taskiq.cli',
 'taskiq.formatters',
 'taskiq.middlewares',
 'taskiq.result_backends',
 'taskiq.tests']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.6.2,<2.0.0', 'typing-extensions>=3.10.0.0']

entry_points = \
{'console_scripts': ['taskiq = taskiq.__main__:main']}

setup_kwargs = {
    'name': 'taskiq',
    'version': '0.0.1',
    'description': 'Asynchronous task queue with async support',
    'long_description': '# Taskiq\n\nTaskiq is an asynchronous distributed task queue.\nThis project takes inspiration from big projects such as [Celery](https://docs.celeryq.dev) and [Dramatiq](https://dramatiq.io/).\nBut taskiq can send and run both the sync and async functions.\nAlso, we use [PEP-612](https://peps.python.org/pep-0612/) to provide the best autosuggestions possible. But since it\'s a new PEP, I encourage you to use taskiq with VS code because Pylance understands all types correctly.\n\n# Installation\n\nThis project can be installed using pip:\n```bash\npip install taskiq\n```\n\nOr it can be installed directly from git:\n\n```bash\npip install git+https://github.com/taskiq-python/taskiq\n```\n\n# Usage\n\nLet\'s see the example with the in-memory broker:\n\n```python\nimport asyncio\n\nfrom taskiq.brokers.inmemory_broker import InMemoryBroker\n\n\n# This is broker that can be used for\n# development or for demo purpose.\n# In production environment consider using\n# real distributed brokers, such as taskiq-aio-pika\n# for rabbitmq.\nbroker = InMemoryBroker()\n\n\n# Or you can optionally\n# pass task_name as the parameter in the decorator.\n@broker.task\nasync def my_async_task() -> None:\n    """My lovely task."""\n    await asyncio.sleep(1)\n    print("Hello")\n\n\nasync def main():\n    # Kiq is the method that actually\n    # sends task over the network.\n    task = await my_async_task.kiq()\n    # Now we print result of execution.\n    print(await task.get_result())\n\n\nasyncio.run(main())\n\n```\n\n\nYou can run it with python without any extra actions,\nsince this script uses the `InMemoryBroker`.\n\nIt won\'t send any data over the network,\nand you cannot use this type of broker in\na real-world scenario, but it\'s useful for\nlocal development if you do not want to\nset up a taskiq worker.\n\n\n## Brokers\n\nBrokers are simple. They don\'t execute functions,\nbut they can send messages and listen to new messages.\n\nEvery broker implements the [taskiq.abc.broker.AsyncBroker](https://github.com/taskiq-python/taskiq/blob/master/taskiq/abc/broker.py#L50) abstract class. All tasks are assigned to brokers, so every time you call the `kiq` method, you send this task to the assigned broker. (This behavior can be changed, by using `Kicker` directly).\n\nAlso you can add middlewares to brokers using `add_middlewares` method.\n\nLike this:\n\n```python\nfrom taskiq.brokers.inmemory_broker import InMemoryBroker\nfrom taskiq.middlewares.retry_middleware import SimpleRetryMiddleware\n\n# This is broker that can be used for\n# development or for demo purpose.\n# In production environment consider using\n# real distributed brokers, such as taskiq-aio-pika\n# for rabbitmq.\nbroker = InMemoryBroker()\nbroker.add_middlewares(\n    [\n        SimpleRetryMiddleware(\n            default_retry_count=4,\n        )\n    ]\n)\n```\n\nTo run middlewares properly you must add them using the `add_middlewares` method.\nIt lead to errors if you try to add them by modifying broker directly.\n\nAlso brokers have formatters. You can change format\nof a message to be compitable with other task execution\nsystems, so your migration to taskiq can be smoother.\n\n## Result backends\n\nAfter task is complete it will try to save the results of execution\nin result backends. By default brokers\nuse `DummyResultBackend` wich doesn\'t do anything. It\nwon\'t print the result in logs and it always returns\n`None` as the `return_value`, and 0 for `execution_time`.\nBut some brokers can override it. For example `InMemoryBroker` by default uses `InMemoryResultBackend` and returns correct results.\n\n\n## CLI\n\nTaskiq has a command line interface to run workers.\nIt\'s very simple to get it to work.\n\nYou just have to provide path to your broker. As an example, if you want to start listen to new tasks\nwith broker in module `my_project.broker` you just\nhave to run:\n\n```\ntaskiq my_project.broker:broker\n```\n\ntaskiq can discover tasks modules to import,\nif you add the `-fsd` (file system discover) option.\n\nLet\'s assume we have project with the following structure:\n\n```\ntest_project\n├── broker.py\n├── submodule\n│   └── tasks.py\n└── utils\n    └── tasks.py\n```\n\nYou can specify all tasks modules to import manually.\n\n```bash\ntaskiq test_project.broker:broker test_projec.submodule.tasks test_projec.utils.tasks\n```\n\nOr you can let taskiq find all python modules named tasks in current directory recursively.\n\n```bash\ntaskiq test_project.broker:broker -fsd\n```\n\nYou can always run `--help` to see all possible options.\n\n\n## Middlewares\n\nMiddlewares are used to modify message, or take\nsome actions after task is complete.\n\nYou can write your own middlewares by subclassing\nthe `taskiq.abc.middleware.TaskiqMiddleware`.\n\nEvery hook can be sync or async. Taskiq will execute it.\n\nFor example, this is a valid middleware.\n\n```python\nimport asyncio\n\nfrom taskiq.abc.middleware import TaskiqMiddleware\nfrom taskiq.message import TaskiqMessage\n\n\nclass MyMiddleware(TaskiqMiddleware):\n    async def pre_send(self, message: "TaskiqMessage") -> TaskiqMessage:\n        await asyncio.sleep(1)\n        message.labels["my_label"] = "my_value"\n        return message\n\n    def post_send(self, message: "TaskiqMessage") -> None:\n        print(f"Message {message} was sent.")\n\n```\n\nYou can use sync or async hooks without changing aything, but adding async to the hook signature.\n\nMiddlewares can store information in message.labels for\nlater use. For example `SimpleRetryMiddleware` uses labels\nto remember number of failed attempts.\n\n## Messages\n\nEvery message has labels. You can define labels\nusing `task` decorator, or you can add them using kicker.\n\nFor example:\n\n```python\n\n@broker.task(my_label=1, label2="something")\nasync def my_async_task() -> None:\n    """My lovely task."""\n    await asyncio.sleep(1)\n    print("Hello")\n\nasync def main():\n    await my_async_task.kiq()\n```\n\nIt\'s equivalent to this\n\n```python\n\n@broker.task\nasync def my_async_task() -> None:\n    """My lovely task."""\n    await asyncio.sleep(1)\n    print("Hello")\n\nasync def main():\n    await my_async_task.kicker().with_labels(\n        my_label=1,\n        label2="something",\n    ).kiq()\n```\n\n## Kicker\n\nThe kicker is the object that sends tasks.\nWhen you call kiq it generates a Kicker instance,\nremembering current broker and message labels.\nYou can change the labels you want to use for this particular task or you can even change broker.\n\nFor example:\n\n```python\nimport asyncio\n\nfrom taskiq.brokers.inmemory_broker import InMemoryBroker\n\nbroker = InMemoryBroker()\nsecond_broker = InMemoryBroker()\n\n\n@broker.task\nasync def my_async_task() -> None:\n    """My lovely task."""\n    await asyncio.sleep(1)\n    print("Hello")\n\n\nasync def main():\n    task = await my_async_task.kicker().with_broker(second_broker).kiq()\n    print(await task.get_result())\n\n\nasyncio.run(main())\n\n```\n',
    'author': 'Pavel Kirilin',
    'author_email': 'win10@list.ru',
    'maintainer': 'Pavel Kirilin',
    'maintainer_email': 'win10@list.ru',
    'url': 'https://github.com/taskiq-python/taskiq',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
