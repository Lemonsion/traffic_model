# --------------导入模块-------------
from sqlalchemy import create_engine  # 导入SQLAlchemy的create_engine函数，用于创建数据库连接
from sqlalchemy.orm import sessionmaker  # 导入sessionmaker，用于创建会话对象

# --------------数据库连接参数-------------
# 定义数据库连接所需的参数
host = 'localhost'  # 数据库主机地址
port = 3306  # 数据库端口号（MySQL默认端口为3306）
user = 'root'  # 数据库用户名
password = 'yx220111'  # 数据库密码
database = 'traffic_db'  # 使用的数据库名称

# --------------构建数据库连接URL-------------
# 使用以上参数构建数据库连接URL，适用于MySQL数据库
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

# --------------创建数据库引擎-------------
# 使用SQLAlchemy的create_engine函数创建数据库引擎对象，'echo=True'表示输出SQL日志
engine = create_engine(DATABASE_URL, echo=True)

# --------------创建会话对象-------------
# 创建SessionLocal对象，用于后续数据库会话的操作，autocommit=False表示关闭自动提交
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
