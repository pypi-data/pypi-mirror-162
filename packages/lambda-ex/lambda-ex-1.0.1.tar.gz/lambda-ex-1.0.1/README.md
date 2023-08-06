# lambda-ex

python lambda expression in multiple lines.

## install

```shell
pip install git+https://github.com/likianta/lambda-ex
```

*note: it requires python 3.8+.*

## usage

```python
from lambda_ex import xlambda

add = xlambda('a, b', """
    return a + b
""")

print(add(1, 2))  # -> 3
```

### kwargs

```python
from lambda_ex import xlambda

add = xlambda('a, b, c=0', """
    return a + b + c
""")

print(add(1, 2))  # -> 3
print(add(1, 2, 3))  # -> 6
print(add(a=1, b=2, c=3))  # -> 6
```

if you are passing a complex object, for example a long list, you can also use
"post" kwargs like below:

```python
from lambda_ex import xlambda

print_names = xlambda('title_case=False', """
    for n in names:
        if title_case:
            print(n.title())
        else:
            print(n)
""", kwargs={
    'names': (
        'anne',
        'bob',
        'charlie',
        'david',
        'erin',
    )
})

print_names(title_case=True)
#   -> Anne
#      Bob
#      Charlie
#      David
#      Erin
print_names(title_case=True, names=('fred', 'george', 'harry'))
#   -> Fred
#      George
#      Harry
```

### type annotations

```python
from lambda_ex import xlambda

add = xlambda('a: int, b: int', """
    return a + b
""")

print(add(1, 2))  # -> 3
```

### recursive call

use `__selfunc__` to call itself:

```python
from lambda_ex import xlambda

fibonacci = xlambda(('n'), """
    if n <= 0:
        raise ValueError(n)
    if n <= 2:
        return 1
    return __selfunc__(n - 1) + __selfunc__(n - 2)
""")

fibonacci(10)  # -> 55
```

### context (locals and globals)

lambda-ex can directly access locals and globals in its occurrence:

```python
from lambda_ex import xlambda

a = 1
b = 2

add = xlambda('', """
    return a + b
""")

add()  # -> 3
```

and modify "global" values:

```python
from lambda_ex import xlambda

a = 1
b = 2
c = 0

add = xlambda('', """
    global c
    c = 3
    return a + b + c
""")

print(add())  # -> 6
print(a, b, c)  # -> 1 2 3
```

warning: there is some limitation in this case, see [here](#20220810124919).

## tips & tricks

-   please check `examples` folder to get more usages.

-   if you're using pycharm, you can add a code template to pycharm's live
    template:

    ```
    xlambda('$END$', """

    """)
    ```

    ![](.assets/20220810125842.png)

-   by default lambda-ex inherits caller context, if you want to forbid this
    (it would be little faster then), set `inherit_context` to False:

    ```python
    from lambda_ex import xlambda
    hello_world = xlambda('', """
        print('hello world')
    """, inherit_context=False)
    ```

## cautions & limitations

-   use `\\n` instead of `\n` in your lambda expression. or you may use the
    r-string (example below).

    ```python
    from lambda_ex import xlambda
    foo = xlambda('', r"""
        print('one\ntwo\nthree')
    """)
    foo()
    ```

<a id="20220810124919"></a>

-   you can only use `global` when xlambda in top module, otherwise it won't
    affect outside variables:

    ```python
    from lambda_ex import xlambda

    def foo():
        a = 1
        b = 2
        c = 0

        add = xlambda('', """
            global c  # no effect
            # btw do never use `nonlocals ...` in xlambda, it will raise an
            #   error at once.
            c = 3
            return a + b + c
        """)

        print(add())  # -> 6
        print(a, b, c)  # -> 1 2 0
        #                        ^ no change

    foo()
    ```
