# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyxxl', 'pyxxl.tests', 'pyxxl.tests.api']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

extras_require = \
{'doc': ['mkdocs==1.3.0',
         'mkdocstrings[python]>=0.19.0,<0.20.0',
         'mkdocs-material>=8.3.2,<9.0.0',
         'mdx-include>=1.4.1,<2.0.0']}

setup_kwargs = {
    'name': 'pyxxl',
    'version': '0.1.7',
    'description': 'A Python executor for XXL-jobs',
    'long_description': '# xxl-jobs 的python客户端实现\n\n<p align="center">\n<a href="https://pypi.org/project/pyxxl" target="_blank">\n    <img src="https://img.shields.io/pypi/v/pyxxl?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/pyxxl" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/pyxxl.svg?color=%2334D058" alt="Supported Python versions">\n</a>\n<a href="https://pypi.org/project/pyxxl" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/fcfangcc/pyxxl?color=%2334D058" alt="Coverage">\n</a>\n</p>\n\n使用pyxxl可以方便的把Python写的方法注册到xxl-job中,使用xxl-job-admin管理Python定时任务和周期任务\n\n## 已经支持的功能\n\n* 执行器注册到job-admin\n* task注册，类似于flask路由装饰器的用法\n* 任务的管理（支持在界面上取消，发起等操作，任务完成后会回调admin）\n* 所有阻塞策略的支持\n* 异步支持（推荐）\n\n## 待实现\n\n- [x] 自定义日志 和 界面上查看日志\n\n## 如何使用\n\n```shell\npip install pyxxl\n```\n\n```python\nimport asyncio\n\nfrom pyxxl import PyxxlRunner\n\napp = PyxxlRunner(\n    "http://localhost:8080/xxl-job-admin/api/",\n    executor_name="xxl-job-executor-sample",\n    port=9999,\n    host="172.17.0.1",\n)\n\n@app.handler.register(name="demoJobHandler")\nasync def test_task():\n    await asyncio.sleep(5)\n    return "成功..."\n\n# 如果你代码里面没有实现全异步，请使用同步函数，不然会阻塞其他任务\n@app.handler.register(name="xxxxx")\ndef test_task3():\n    return "成功3"\n\n\napp.run_executor()\n```\n\n\n更多示例和接口文档请参考 [PYXXL文档](https://fcfangcc.github.io/pyxxl/example/) ，具体代码在example文件夹下面\n\n\n## 开发人员\n下面是开发人员如何快捷的搭建开发调试环境\n\n### 启动xxl的调度中心\n\n```shell\n./init_dev_env.sh\n```\n\n\n### 启动执行器\n\n\n```shell\npoetry install\n# 修改app.py中相关的配置信息,然后启动\npoetry run python example/app.py\n```\n',
    'author': 'fcfangcc',
    'author_email': 'swjfc22@live.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fcfangcc/pyxxl',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
