import json
import re
from datetime import datetime

from markdown import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_task.Ali_QWen import get_article


def job(*args, **kwargs):
    """
    定时任务执行同步函数示例
    """
    print(args)
    print(kwargs)
    print(f'{datetime.now()}同步函数执行了')


async def async_job(*args, **kwargs):
    """
    定时任务执行异步函数示例
    """
    print(args)
    print(kwargs)
    print(f'{datetime.now()}异步函数执行了')


async def gen_article_job(*args, **kwargs):
    print("执行任务gen_article_job")
    async for query_db in get_db():
        result = get_article(["我爱祖国", "我爱党和人民"])
        await query_db.commit()
        await query_db.close()