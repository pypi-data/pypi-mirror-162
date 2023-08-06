# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lambda_ex']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'lambda-ex',
    'version': '1.0.1',
    'description': 'Python lambda expression in multiple lines.',
    'long_description': '# lambda-ex\n\npython lambda expression in multiple lines.\n\n## install\n\n```shell\npip install git+https://github.com/likianta/lambda-ex\n```\n\n*note: it requires python 3.8+.*\n\n## usage\n\n```python\nfrom lambda_ex import xlambda\n\nadd = xlambda(\'a, b\', """\n    return a + b\n""")\n\nprint(add(1, 2))  # -> 3\n```\n\n### kwargs\n\n```python\nfrom lambda_ex import xlambda\n\nadd = xlambda(\'a, b, c=0\', """\n    return a + b + c\n""")\n\nprint(add(1, 2))  # -> 3\nprint(add(1, 2, 3))  # -> 6\nprint(add(a=1, b=2, c=3))  # -> 6\n```\n\nif you are passing a complex object, for example a long list, you can also use\n"post" kwargs like below:\n\n```python\nfrom lambda_ex import xlambda\n\nprint_names = xlambda(\'title_case=False\', """\n    for n in names:\n        if title_case:\n            print(n.title())\n        else:\n            print(n)\n""", kwargs={\n    \'names\': (\n        \'anne\',\n        \'bob\',\n        \'charlie\',\n        \'david\',\n        \'erin\',\n    )\n})\n\nprint_names(title_case=True)\n#   -> Anne\n#      Bob\n#      Charlie\n#      David\n#      Erin\nprint_names(title_case=True, names=(\'fred\', \'george\', \'harry\'))\n#   -> Fred\n#      George\n#      Harry\n```\n\n### type annotations\n\n```python\nfrom lambda_ex import xlambda\n\nadd = xlambda(\'a: int, b: int\', """\n    return a + b\n""")\n\nprint(add(1, 2))  # -> 3\n```\n\n### recursive call\n\nuse `__selfunc__` to call itself:\n\n```python\nfrom lambda_ex import xlambda\n\nfibonacci = xlambda((\'n\'), """\n    if n <= 0:\n        raise ValueError(n)\n    if n <= 2:\n        return 1\n    return __selfunc__(n - 1) + __selfunc__(n - 2)\n""")\n\nfibonacci(10)  # -> 55\n```\n\n### context (locals and globals)\n\nlambda-ex can directly access locals and globals in its occurrence:\n\n```python\nfrom lambda_ex import xlambda\n\na = 1\nb = 2\n\nadd = xlambda(\'\', """\n    return a + b\n""")\n\nadd()  # -> 3\n```\n\nand modify "global" values:\n\n```python\nfrom lambda_ex import xlambda\n\na = 1\nb = 2\nc = 0\n\nadd = xlambda(\'\', """\n    global c\n    c = 3\n    return a + b + c\n""")\n\nprint(add())  # -> 6\nprint(a, b, c)  # -> 1 2 3\n```\n\nwarning: there is some limitation in this case, see [here](#20220810124919).\n\n## tips & tricks\n\n-   please check `examples` folder to get more usages.\n\n-   if you\'re using pycharm, you can add a code template to pycharm\'s live\n    template:\n\n    ```\n    xlambda(\'$END$\', """\n\n    """)\n    ```\n\n    ![](.assets/20220810125842.png)\n\n-   by default lambda-ex inherits caller context, if you want to forbid this\n    (it would be little faster then), set `inherit_context` to False:\n\n    ```python\n    from lambda_ex import xlambda\n    hello_world = xlambda(\'\', """\n        print(\'hello world\')\n    """, inherit_context=False)\n    ```\n\n## cautions & limitations\n\n-   use `\\\\n` instead of `\\n` in your lambda expression. or you may use the\n    r-string (example below).\n\n    ```python\n    from lambda_ex import xlambda\n    foo = xlambda(\'\', r"""\n        print(\'one\\ntwo\\nthree\')\n    """)\n    foo()\n    ```\n\n<a id="20220810124919"></a>\n\n-   you can only use `global` when xlambda in top module, otherwise it won\'t\n    affect outside variables:\n\n    ```python\n    from lambda_ex import xlambda\n\n    def foo():\n        a = 1\n        b = 2\n        c = 0\n\n        add = xlambda(\'\', """\n            global c  # no effect\n            # btw do never use `nonlocals ...` in xlambda, it will raise an\n            #   error at once.\n            c = 3\n            return a + b + c\n        """)\n\n        print(add())  # -> 6\n        print(a, b, c)  # -> 1 2 0\n        #                        ^ no change\n\n    foo()\n    ```\n',
    'author': 'Likianta',
    'author_email': 'likianta@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/likianta/lambda-ex',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
