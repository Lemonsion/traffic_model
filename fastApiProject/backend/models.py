# --------------导入SQLAlchemy模块-------------
from sqlalchemy.ext.declarative import declarative_base  # 导入declarative_base，用于定义数据模型的基类
from sqlalchemy import Column, Integer, String, Date  # 导入Column（用于定义列）、Integer（整数类型）、String（字符串类型）、Date（日期类型）

# --------------定义Base类-------------
# 使用declarative_base()创建基础类，所有模型类都需要继承该类
Base = declarative_base()

# --------------定义DailySummary模型类-------------
class DailySummary(Base):
    # 定义数据库表的名称
    __tablename__ = 'daily_summary'

    # --------------定义数据表的字段-------------
    date = Column(Date, primary_key=True)  # 日期字段，作为主键
    total_count = Column(Integer)  # 总计数字段，存储某一天的总检测数
    warning_total = Column(Integer)  # 预警总数字段，存储某一天的总预警数
    table_name = Column(String(50))  # 表名称字段，存储表的名称，最多50个字符
