from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class GenTableOptionModel(BaseModel):

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    parent_menu_id: Optional[int] = Field(default=None, description='所属父级分类')

    tree_code: Optional[str] = Field(default=None, description='tree_code')

    tree_name: Optional[str] = Field(default=None, description='tree_name')

    tree_parent_code: Optional[str] = Field(default=None, description='tree_parent_code')