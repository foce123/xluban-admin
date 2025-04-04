from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.env_do import AppEnv
from module_admin.entity.vo.env_vo import EnvModel, EnvPageQueryModel
from utils.page_util import PageUtil


class EnvDao:
    """
    环境管理模块数据库操作层
    """

    @classmethod
    async def get_env_by_id(cls, db: AsyncSession, env_id: int):
        """
        根据环境id获取在用环境详细信息

        :param db: orm对象
        :param env_id: 环境id
        :return: 在用环境信息对象
        """
        env_info = (
            (await db.execute(select(AppEnv).where(AppEnv.env_id == env_id, AppEnv.status == '0')))
            .scalars()
            .first()
        )

        return env_info

    @classmethod
    async def get_env_detail_by_id(cls, db: AsyncSession, env_id: int):
        """
        根据环境id获取环境详细信息

        :param db: orm对象
        :param env_id: 环境id
        :return: 环境信息对象
        """
        env_info = (await db.execute(select(AppEnv).where(AppEnv.env_id == env_id))).scalars().first()

        return env_info

    @classmethod
    async def get_env_detail_by_info(cls, db: AsyncSession, env: EnvModel):
        """
        根据环境参数获取环境信息

        :param db: orm对象
        :param env: 环境参数对象
        :return: 环境信息对象
        """
        env_info = (
            (
                await db.execute(
                    select(AppEnv).where(
                        AppEnv.env_name == env.env_name if env.env_name else True,
                        AppEnv.env_code == env.env_code if env.env_code else True,
                        AppEnv.env_sort == env.env_sort if env.env_sort else True,
                    )
                )
            )
            .scalars()
            .first()
        )

        return env_info

    @classmethod
    async def get_env_list(cls, db: AsyncSession, query_object: EnvPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取环境列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 环境列表信息对象
        """
        query = (
            select(AppEnv)
            .where(
                AppEnv.env_code.like(f'%{query_object.env_code}%') if query_object.env_code else True,
                AppEnv.env_name.like(f'%{query_object.env_name}%') if query_object.env_name else True,
                AppEnv.status == query_object.status if query_object.status else True,
            )
            .order_by(AppEnv.env_sort)
            .distinct()
        )
        env_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return env_list

    @classmethod
    async def add_env_dao(cls, db: AsyncSession, env: EnvModel):
        """
        新增岗位数据库操作

        :param db: orm对象
        :param post: 岗位对象
        :return:
        """
        db_env = AppEnv(**env.model_dump())
        db.add(db_env)
        await db.flush()

        return db_env

    @classmethod
    async def edit_env_dao(cls, db: AsyncSession, env: dict):
        """
        编辑环境数据库操作

        :param db: orm对象
        :param env: 需要更新的环境字典
        :return:
        """
        await db.execute(update(AppEnv), [env])

    @classmethod
    async def delete_env_dao(cls, db: AsyncSession, env: EnvModel):
        """
        删除环境数据库操作

        :param db: orm对象
        :param env: 环境对象
        :return:
        """
        await db.execute(delete(AppEnv).where(AppEnv.env_id.in_([env.env_id])))
