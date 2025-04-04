from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size
from typing import Literal, Optional
from module_admin.annotation.pydantic_annotation import as_query


class EnvModel(BaseModel):
    """
    环境信息表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    env_id: Optional[int] = Field(default=None, description='环境ID')
    env_code: Optional[str] = Field(default=None, description='环境编码')
    env_name: Optional[str] = Field(default=None, description='环境名称')
    env_sort: Optional[int] = Field(default=None, description='显示顺序')
    status: Optional[Literal['0', '1']] = Field(default=None, description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='env_code', message='环境编码不能为空')
    @Size(field_name='env_code', min_length=0, max_length=64, message='环境编码长度不能超过64个字符')
    def get_env_code(self):
        return self.env_code

    @NotBlank(field_name='env_name', message='环境名称不能为空')
    @Size(field_name='env_name', min_length=0, max_length=50, message='环境名称长度不能超过50个字符')
    def get_env_name(self):
        return self.env_name

    @NotBlank(field_name='env_sort', message='显示顺序不能为空')
    def get_env_sort(self):
        return self.env_sort

    def validate_fields(self):
        self.get_env_code()
        self.get_env_name()
        self.get_env_sort()


class EnvQueryModel(EnvModel):
    """
    环境管理不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


@as_query
class EnvPageQueryModel(EnvQueryModel):
    """
    环境管理分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteEnvModel(BaseModel):
    """
    删除环境模型
    """

    model_config = ConfigDict(alias_generator=to_camel)
    env_ids: str = Field(description='需要删除的岗位ID')