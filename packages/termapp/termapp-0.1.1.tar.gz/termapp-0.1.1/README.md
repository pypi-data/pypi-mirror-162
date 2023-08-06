# termapp

[![CI Status](https://github.com/halimath/termapp/workflows/CI/badge.svg)](https://github.com/halimath/termapp/actions/workflows/ci.yaml)
[![Releases](https://img.shields.io/github/v/release/halimath/termapp.svg)](https://github.com/halimath/termapp/releases)
[![PyPi](https://img.shields.io/pypi/v/termapp.svg)](https://pypi.org/project/termapp/)
[![Wheel](https://img.shields.io/pypi/wheel/termapp.svg)](https://pypi.org/project/termapp/)
[![Python Versions](https://img.shields.io/pypi/pyversions/termapp.svg)](https://pypi.org/project/termapp/)

Create terminal applications with python.

# Installation

```shell
pip install termapp
```

# Usage

```python
import asyncio

from termapp.asyncio import create_app

app = create_app()


async def start():
    await app.info('info')
    await app.details('additional details')
    await app.warn('warn')
    await app.danger('error')
    await app.success('success')
    await app.failure('failure')

    await app.start_progress(show_completion=True)    
    await asyncio.sleep(5)
    await app.stop_progress()
    await app.success('all done')


async def warn_later():
    await asyncio.sleep(0.5)
    await app.update_progress(completion=0.3, message='Some task to be done')
    await asyncio.sleep(0.5)
    await app.update_progress(completion=0.6)
    await asyncio.sleep(0.5)
    await app.update_progress(message='Another task to be done')
    await asyncio.sleep(0.5)
    await app.update_progress(completion=0.9)
    await asyncio.sleep(1)
    await app.warn('Something unexpected happened')


async def main():
    return await asyncio.gather(start(), warn_later())

asyncio.run(main())
```

# License

Copyright 2022 Alexander Metzner.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
