# -*- coding:utf-8 -*-

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from utils.common_util import CamelCaseUtil, export_list2excel
from utils.page_util import PageResponseModel
from module_admin.dao.car_driver_dao import CarDriverDao
from module_admin.entity.do.car_driver_do import CarDriver
from module_admin.entity.vo.car_driver_vo import CarDriverPageModel, CarDriverModel


class CarDriverService:
    """
    用户管理模块服务层
    """

    @classmethod
    async def get_car_driver_list(cls, query_db: AsyncSession, query_object: CarDriverPageModel, data_scope_sql: str) -> [list | PageResponseModel]:
        car_driver_list = await CarDriverDao.get_car_driver_list(query_db, query_object, data_scope_sql, is_page=True)
        return car_driver_list

    @classmethod
    async def get_car_driver_by_id(cls, query_db: AsyncSession, car_driver_id: int) -> CarDriverModel:
        car_driver = await  CarDriverDao.get_by_id(query_db, car_driver_id)
        car_driver_model = CarDriverModel(**CamelCaseUtil.transform_result(car_driver))
        return car_driver_model


    @classmethod
    async def add_car_driver(cls, query_db: AsyncSession, query_object: CarDriverModel) -> CarDriverModel:
        car_driver = await CarDriverDao.add_car_driver(query_db, query_object)
        car_driver_model = CarDriverModel(**CamelCaseUtil.transform_result(car_driver))
        return car_driver_model


    @classmethod
    async def update_car_driver(cls, query_db: AsyncSession, query_object: CarDriverModel) -> CarDriverModel:
        car_driver = await CarDriverDao.edit_car_driver(query_db, query_object)
        car_driver_model = CarDriverModel(**CamelCaseUtil.transform_result(car_driver))
        return car_driver_model


    @classmethod
    async def del_car_driver(cls, query_db: AsyncSession, car_driver_ids: List[str]):
        await CarDriverDao.del_car_driver(query_db, car_driver_ids)


    @classmethod
    async def export_car_driver_list(cls, query_db: AsyncSession, query_object: CarDriverPageModel, data_scope_sql) -> bytes:
        car_driver_list = await CarDriverDao.get_car_driver_list(query_db, query_object, data_scope_sql, is_page=False)
        mapping_dict = {
            'age': '年龄 ',
            'carType': '车辆类型 ',
            'driverYears': '驾龄 ',
            'image': '图片 ',
            'location': '所在位置 ',
            'name': '司机名称 ',
            'price': '价格 ',
            'updateTime': '更新时间 ',
        }
        new_data = [
            {mapping_dict.get(key): value for key, value in item.items() if mapping_dict.get(key)} for item in car_driver_list
        ]
        binary_data = export_list2excel(new_data)
        return binary_data