from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import LoginService
from module_admin.service.app_env_service import EnvService
from module_admin.entity.vo.env_vo import DeleteEnvModel, EnvModel, EnvPageQueryModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


appEnvController = APIRouter(prefix='/deployment/environment', dependencies=[Depends(LoginService.get_current_user)])


@appEnvController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('deployment:environment:list'))]
)
async def get_app_env_list(
    request: Request,
    env_page_query: EnvPageQueryModel = Depends(EnvPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    env_page_query_result = await EnvService.get_env_list_services(query_db, env_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=env_page_query_result)


@appEnvController.post('', dependencies=[Depends(CheckUserInterfaceAuth('deployment:environment:add'))])
@ValidateFields(validate_model='add_env')
@Log(title='环境管理', business_type=BusinessType.INSERT)
async def add_app_env(
    request: Request,
    add_env: EnvModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_env.create_by = current_user.user.user_name
    add_env.create_time = datetime.now()
    add_env.update_by = current_user.user.user_name
    add_env.update_time = datetime.now()
    add_env_result = await EnvService.add_env_services(query_db, add_env)
    logger.info(add_env_result.message)

    return ResponseUtil.success(msg=add_env_result.message)


@appEnvController.put('', dependencies=[Depends(CheckUserInterfaceAuth('deployment:environment:edit'))])
@ValidateFields(validate_model='edit_env')
@Log(title='环境管理', business_type=BusinessType.UPDATE)
async def edit_app_env(
    request: Request,
    edit_env: EnvModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_env.update_by = current_user.user.user_name
    edit_env.update_time = datetime.now()
    edit_env_result = await EnvService.edit_env_services(query_db, edit_env)
    logger.info(edit_env_result.message)

    return ResponseUtil.success(msg=edit_env_result.message)


@appEnvController.delete('/{env_ids}', dependencies=[Depends(CheckUserInterfaceAuth('deployment:environment:remove'))])
@Log(title='环境管理', business_type=BusinessType.DELETE)
async def delete_app_env(request: Request, env_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_env = DeleteEnvModel(envIds=env_ids)
    delete_env_result = await EnvService.delete_env_services(query_db, delete_env)
    logger.info(delete_env_result.message)

    return ResponseUtil.success(msg=delete_env_result.message)


@appEnvController.get(
    '/{env_id}', response_model=EnvModel, dependencies=[Depends(CheckUserInterfaceAuth('deployment:environment:query'))]
)
async def query_detail_app_env(request: Request, env_id: int, query_db: AsyncSession = Depends(get_db)):
    env_detail_result = await EnvService.env_detail_services(query_db, env_id)
    logger.info(f'获取env_id为{env_id}的信息成功')

    return ResponseUtil.success(data=env_detail_result)


@appEnvController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('deployment:environment:export'))])
@Log(title='环境管理', business_type=BusinessType.EXPORT)
async def export_app_env_list(
    request: Request,
    env_page_query: EnvPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    env_query_result = await EnvService.get_env_list_services(query_db, env_page_query, is_page=False)
    env_export_result = await EnvService.export_env_list_services(env_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(env_export_result))
