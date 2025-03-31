# -*- coding:utf-8 -*-

from typing import List
from datetime import datetime, time
from module_admin.entity.do.role_do import SysRoleDept
from sqlalchemy import and_, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.student_info_do import StudentInfo
from module_admin.entity.vo.student_info_vo import StudentInfoPageModel, StudentInfoModel
from module_gen.constants.gen_constants import GenConstants
from utils.page_util import PageUtil, PageResponseModel


class StudentInfoDao:

    @classmethod
    async def get_by_id(cls, db: AsyncSession, student_info_id: int) -> StudentInfo:
        """根据主键获取单条记录"""
        student_info = (((await db.execute(
                            select(StudentInfo)
                            .where(StudentInfo.id == student_info_id)))
                       .scalars())
                       .first())
        return student_info

    """
    查询
    """
    @classmethod
    async def get_student_info_list(cls, db: AsyncSession,
                             query_object: StudentInfoPageModel,
                             data_scope_sql: str = None,
                             is_page: bool = False) -> [list | PageResponseModel]:

        query = (
            select(StudentInfo)
            .where(
                StudentInfo.gender == query_object.gender if query_object.gender else True,
                StudentInfo.name == query_object.name if query_object.name else True,
                StudentInfo.phone_number == query_object.phone_number if query_object.phone_number else True,
                StudentInfo.del_flag == '0',
                eval(data_scope_sql) if data_scope_sql else True,
            )
            .order_by(desc(StudentInfo.create_time))
            .distinct()
        )
        student_info_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)
        return student_info_list


    @classmethod
    async def add_student_info(cls, db: AsyncSession, add_model: StudentInfoModel, auto_commit: bool = True) -> StudentInfo:
        """
        增加
        """
        student_info =  StudentInfo(**add_model.model_dump(exclude_unset=True))
        db.add(student_info)
        await db.flush()
        if auto_commit:
            await db.commit()
        return student_info

    @classmethod
    async def edit_student_info(cls, db: AsyncSession, edit_model: StudentInfoModel, auto_commit: bool = True) -> StudentInfo:
        """
        修改
        """
        edit_dict_data = edit_model.model_dump(exclude_unset=True, exclude={*GenConstants.DAO_COLUMN_NOT_EDIT})
        await db.execute(update(StudentInfo), [edit_dict_data])
        await db.flush()
        if auto_commit:
            await db.commit()
        return await cls.get_by_id(db, edit_model.id)

    @classmethod
    async def del_student_info(cls, db: AsyncSession, student_info_ids: List[str], soft_del: bool = True, auto_commit: bool = True):
        """
        删除
        """
        if soft_del:
            await db.execute(update(StudentInfo).where(StudentInfo.id.in_(student_info_ids)).values(del_flag='2'))
        else:
            await db.execute(delete(StudentInfo).where(StudentInfo.id.in_(student_info_ids)))
        await db.flush()
        if auto_commit:
            await db.commit()