from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.dao.app_env_dao import EnvDao
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.env_vo import DeleteEnvModel, EnvModel, EnvPageQueryModel
from utils.common_util import CamelCaseUtil, export_list2excel


class EnvService:
    """
    环境管理模块服务层
    """

    @classmethod
    async def get_env_list_services(
        cls, query_db: AsyncSession, query_object: EnvPageQueryModel, is_page: bool = False
    ):
        """
        获取环境列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 环境列表信息对象
        """
        env_list_result = await EnvDao.get_env_list(query_db, query_object, is_page)

        return env_list_result

    @classmethod
    async def check_env_name_unique_services(cls, query_db: AsyncSession, page_object: EnvModel):
        """
        检查环境名称是否唯一service

        :param query_db: orm对象
        :param page_object: 环境对象
        :return: 校验结果
        """
        env_id = -1 if page_object.env_id is None else page_object.env_id
        env = await EnvDao.get_env_detail_by_info(query_db, EnvModel(envName=page_object.env_name))
        if env and env.post_id != env_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def check_env_code_unique_services(cls, query_db: AsyncSession, page_object: EnvModel):
        """
        检查环境编码是否唯一service

        :param query_db: orm对象
        :param page_object: 环境对象
        :return: 校验结果
        """
        env_id = -1 if page_object.env_id is None else page_object.env_id
        env = await EnvDao.get_env_detail_by_info(query_db, EnvModel(envCode=page_object.env_code))
        if env and env.post_id != env_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_env_services(cls, query_db: AsyncSession, page_object: EnvModel):
        """
        新增环境信息service

        :param query_db: orm对象
        :param page_object: 新增环境对象
        :return: 新增环境校验结果
        """
        if not await cls.check_env_name_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增环境{page_object.env_name}失败，环境名称已存在')
        elif not await cls.check_env_code_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增环境{page_object.env_name}失败，环境编码已存在')
        else:
            try:
                await EnvDao.add_env_dao(query_db, page_object)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='新增成功')
            except Exception as e:
                await query_db.rollback()
                raise e

    @classmethod
    async def edit_env_services(cls, query_db: AsyncSession, page_object: EnvModel):
        """
        编辑环境信息service

        :param query_db: orm对象
        :param page_object: 编辑环境对象
        :return: 编辑环境校验结果
        """
        edit_env = page_object.model_dump(exclude_unset=True)
        env_info = await cls.env_detail_services(query_db, page_object.env_id)
        if env_info.post_id:
            if not await cls.check_env_name_unique_services(query_db, page_object):
                raise ServiceException(message=f'修改环境{page_object.env_name}失败，环境名称已存在')
            elif not await cls.check_env_code_unique_services(query_db, page_object):
                raise ServiceException(message=f'修改环境{page_object.env_name}失败，环境编码已存在')
            else:
                try:
                    await EnvDao.edit_env_dao(query_db, edit_env)
                    await query_db.commit()
                    return CrudResponseModel(is_success=True, message='更新成功')
                except Exception as e:
                    await query_db.rollback()
                    raise e
        else:
            raise ServiceException(message='环境不存在')

    @classmethod
    async def delete_env_services(cls, query_db: AsyncSession, page_object: DeleteEnvModel):
        """
        删除环境信息service

        :param query_db: orm对象
        :param page_object: 删除环境对象
        :return: 删除环境校验结果
        """
        if page_object.post_ids:
            env_id_list = page_object.env_ids.split(',')
            try:
                for env_id in env_id_list:
                    env = await cls.env_detail_services(query_db, int(env_id))
                    await EnvDao.delete_env_dao(query_db, EnvModel(envId=env_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入环境id为空')

    @classmethod
    async def env_detail_services(cls, query_db: AsyncSession, env_id: int):
        """
        获取环境详细信息service

        :param query_db: orm对象
        :param env_id: 环境id
        :return: 环境id对应的信息
        """
        env = await EnvDao.get_env_detail_by_id(query_db, env_id=env_id)
        if env:
            result = EnvModel(**CamelCaseUtil.transform_result(env))
        else:
            result = EnvModel(**dict())

        return result

    @staticmethod
    async def export_env_list_services(env_list: List):
        """
        导出环境信息service

        :param env_list: 环境信息列表
        :return: 环境信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'envId': '岗位编号',
            'envCode': '岗位编码',
            'envName': '岗位名称',
            'envSort': '显示顺序',
            'status': '状态',
            'createBy': '创建者',
            'createTime': '创建时间',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'remark': '备注',
        }

        data = env_list

        for item in data:
            if item.get('status') == '0':
                item['status'] = '正常'
            else:
                item['status'] = '停用'
        new_data = [
            {mapping_dict.get(key): value for key, value in item.items() if mapping_dict.get(key)} for item in data
        ]
        binary_data = export_list2excel(new_data)

        return binary_data
