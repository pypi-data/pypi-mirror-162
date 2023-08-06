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
