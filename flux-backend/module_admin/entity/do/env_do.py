from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from config.database import Base


class AppEnv(Base):
    """
    环境信息表
    """

    __tablename__ = 'app_env'

    env_id = Column(Integer, primary_key=True, autoincrement=True, comment='环境ID')
    env_code = Column(String(64), nullable=False, comment='环境编码')
    env_name = Column(String(50), nullable=False, comment='环境名称')
    env_sort = Column(Integer, nullable=False, comment='显示顺序')
    status = Column(String(1), nullable=False, default='0', comment='状态（0正常 1停用）')
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')
    remark = Column(String(500), nullable=True, default=None, comment='备注')