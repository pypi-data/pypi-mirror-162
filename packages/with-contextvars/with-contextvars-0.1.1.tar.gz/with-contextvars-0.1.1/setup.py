# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['with_contextvars']
setup_kwargs = {
    'name': 'with-contextvars',
    'version': '0.1.1',
    'description': 'Context manager for setting contextvars variables',
    'long_description': 'with-contextvars\n================\n\nThis module provides ``Set``, a context manager which sets one or more ``contextvars``\nvariables upon activation and resets them to their previous values at exit.\n\nUsage::\n\n    import contextvars, with_contextvars\n    A = contextvars.ContextVar("A")\n    B = contextvars.ContextVar("B")\n    A.set("Hello,")\n    B.set("world!")\n    print(A.get(), B.get())\n    # prints: Hello, world!\n    with with_contextvars.Set((A, "other"), (B, "value")):\n        print(A.get(), B.get())\n        # prints: other value\n    print(A.get(), B.get())\n    # prints: Hello, world!\n\nEven the entirety of variable assignments of a ``contextvars.Context`` object\n(as obtained from ``contextvars.copy_context()``) can be activated by initializing\n``Set`` with its items::\n\n    with with_contextvars.Set(*context.items()):\n        ...\n\nHowever, using ``contextvars.Context.run()`` is more efficient and should be preferred\nwhere possible.\n\nMore information can be found in the documentation of ``Set``.\n',
    'author': 'Robert Schindler',
    'author_email': 'dev@bob1.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bob1de/with-contextvars',
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
