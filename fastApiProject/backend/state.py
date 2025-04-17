from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

# --------------创建线程池执行器-------------
# 使用ThreadPoolExecutor来管理线程池，最大并发线程数为4
executor = ThreadPoolExecutor(max_workers=4)

# --------------存储 WebSocket 连接-------------
# 用字典来存储所有当前活动的WebSocket连接，键是连接的标识符，值是WebSocket对象
active_connections = {}


