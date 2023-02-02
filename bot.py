import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from sqlalchemy.orm import sessionmaker
from tgbot.config import load_config, Config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.admin_add import register_admin_add
from tgbot.handlers.admin_delete import register_delete_time
from tgbot.handlers.admin_edit_time import register_edit_time
from tgbot.handlers.admin_info import register_info_time
from tgbot.infrastucture.database.functions.channel_photo import get_photo, delete_channel_photo
from tgbot.infrastucture.database.functions.setup import create_session_pool
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.scheduler import SchedulerMiddleware

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, session_pool, environment: dict, scheduler):
    dp.setup_middleware(DatabaseMiddleware(session_pool))
    dp.setup_middleware(EnvironmentMiddleware(**environment))
    dp.setup_middleware(SchedulerMiddleware(scheduler))


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_admin_add(dp)
    register_edit_time(dp)
    register_delete_time(dp)
    register_info_time(dp)


async def send_message_to_channel(bot: Bot, config: Config, session_pool: sessionmaker):
    async with session_pool() as session:
        photo = await get_photo(session)
        if photo:
            await bot.send_photo(chat_id=config.tg_bot.channel_id, photo=photo.file_id)

            await delete_channel_photo(session, photo_id=photo.photo_id)
        else:
            return


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2(host='redis_cache',
                            password=config.tg_bot.redis_password)

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    session_pool = await create_session_pool(config.db, echo=False)

    job_stores = {
        "default": RedisJobStore(
            host='redis_cache',  password=config.tg_bot.redis_password,
            jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running"
        )
    }

    bot['config'] = config
    bot['session_pool'] = session_pool

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))

    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(config, declared_class=Config)
    scheduler.ctx.add_instance(session_pool, declared_class=sessionmaker)

    register_all_middlewares(
        dp,
        session_pool=session_pool,
        environment=dict(config=config),
        scheduler=scheduler
    )
    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        scheduler.start()
        if not scheduler.get_job('send_message_to_channel'):
            scheduler.add_job(send_message_to_channel, "interval", minutes=15, id="send_message_to_channel",
                              replace_existing=True)
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
