# 导入依赖模块
import re
from sqlalchemy import text, MetaData  # SQLAlchemy 的执行原生 SQL 和元数据支持
from datetime import datetime, date    # 日期时间处理
from db import SessionLocal, engine    # 数据库连接和引擎
from models import DailySummary        # 导入每日汇总数据模型
from sqlalchemy import func            # 用于聚合函数（如 sum）
from typing import Optional
from fastapi import Request

# 获取今天的字符串格式（例如：20250415）
def get_today_str():
    return date.today().strftime("%Y%m%d")

# 获取今天的日期对象
def get_today_date():
    return date.today()

# 构造今天的检测记录表名（如：detect_log_20250415）
def get_today_table_name():
    return f"detect_log_{get_today_str()}"

# 确保今天的表存在，如果不存在就创建
def ensure_today_table_exists():
    table_name = get_today_table_name()
    metadata = MetaData()
    metadata.bind = engine

    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        detection_id VARCHAR(20),
        processed_file LONGTEXT,
        warning_count INT,
        timestamp DATETIME,
        conf FLOAT,
        bus INT, 
        trafficlight INT, 
        trafficsign INT, 
        person INT, 
        bike INT, 
        truck INT, 
        motor INT, 
        car INT, 
        train INT, 
        rider INT
    )"""

    # 使用 engine.begin 自动提交事务
    with engine.begin() as conn:
        conn.execute(text(create_sql))

# 插入今天的检测记录，并更新 daily_summary 表
def insert_today_detection_record(processed_file, warning_count):
    ensure_today_table_exists()
    table_name = get_today_table_name()
    now = datetime.now()

    # 查询已有的记录数量，用于生成 detection_id
    with engine.connect() as conn:
        count_result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}")).first()

        print(count_result)
        print("---------------------------------------")
        current_count = count_result[0] if count_result else 0
        detection_id = f"第{current_count + 1}次"

        # 插入新的检测记录
        insert_sql = f"""
        INSERT INTO {table_name} (detection_id, processed_file, warning_count, timestamp)
        VALUES (:detection_id,  :processed_file, :warning_count, :timestamp)
        """
        with engine.begin() as conn:
            conn.execute(
                text(insert_sql),
                {
                    "detection_id": detection_id,
                    "processed_file": processed_file,
                    "warning_count": warning_count,
                    "timestamp": now
                }
            )

    # 更新 daily_summary 表中的今日汇总信息
    db = SessionLocal()
    today = get_today_date()
    summary = db.query(DailySummary).filter(DailySummary.date == today).first()
    if summary:
        summary.total_count += 1
        summary.warning_total += warning_count
    else:
        new_summary = DailySummary(
            date=today,
            total_count=1,
            warning_total=warning_count,
            table_name=table_name
        )
        db.add(new_summary)
    db.commit()
    db.close()

# 更新今天最新一条记录的 warning_count 值，同时更新 daily_summary 总数
def update_today_warning_count(new_warning_count: int):
    table_name = get_today_table_name()
    with engine.connect() as conn:
        # 获取最新一条记录的 detection_id
        count_result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}")).first()
        current_count = count_result[0] if count_result else 0
        detection_id = f"第{current_count}次"
        query_sql = text(f"""
            SELECT warning_count FROM {table_name} WHERE detection_id = :detection_id
        """)
        result = conn.execute(query_sql, {"detection_id": detection_id}).first()
        print(result)
        if not result:
            return {"success": False, "message": "未找到指定的 detection_id"}

        old_warning_count = result[0]
        diff = new_warning_count - old_warning_count

        # 更新该记录
        update_sql = text(f"""
            UPDATE {table_name}
            SET warning_count = :new_warning_count
            WHERE detection_id = :detection_id
        """)
        with engine.begin() as conn:
            with engine.begin() as conn:
                conn.execute(update_sql, {
                    "new_warning_count": new_warning_count,
                    "detection_id": detection_id
                })

    # 更新 daily_summary 的 warning_total
    db = SessionLocal()
    summary = db.query(DailySummary).filter(DailySummary.date == get_today_date()).first()
    if summary:
        summary.warning_total += diff
        db.commit()
    db.close()

    return {"success": True, "message": f"{detection_id} 的 warning_count 已更新为 {new_warning_count}"}

# 获取总体检测汇总数据（总数 + 今日）
async def get_detection_summary():
    db = SessionLocal()
    try:
        # 总数统计
        total = db.query(
            func.sum(DailySummary.total_count).label("total_count"),
            func.sum(DailySummary.warning_total).label("warning_total")
        ).first()

        # 当日统计
        today = get_today_date()
        today_summary = db.query(DailySummary).filter(DailySummary.date == today).first()

        summary_data = {
            "total_detection_count": total.total_count or 0,
            "total_warning_count": total.warning_total or 0,
            "today_detection_count": today_summary.total_count if today_summary else 0,
            "today_warning_count": today_summary.warning_total if today_summary else 0
        }

        return summary_data

    finally:
        db.close()

# 更新今天最新记录的 processed_file 路径
def update_today_processed_file(processedfile):
    table_name = get_today_table_name()
    with engine.connect() as conn:
        # 找到最新一条记录
        count_result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}")).first()
        current_count = count_result[0] if count_result else 0
        detection_id = f"第{current_count}次"

        update_sql = text(f"""
            UPDATE {table_name}
            SET processed_file = :processedfile
            WHERE detection_id = :detection_id
        """)
        with engine.begin() as conn:
            conn.execute(update_sql, {
                "processedfile": processedfile,
                "detection_id": detection_id
            })

# 更新最新记录的 conf 参数及各类检测目标数量
def update_today_config(conf: float, detection_data: dict):
    table_name = get_today_table_name()
    with engine.connect() as conn:
        count_result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}")).first()
        current_count = count_result[0] if count_result else 0
        detection_id = f"第{current_count}次"

        # 默认初始化为 0
        class_counts = {
            "bus": 0,
            "trafficlight": 0,
            "trafficsign": 0,
            "person": 0,
            "bike": 0,
            "truck": 0,
            "motor": 0,
            "car": 0,
            "train": 0,
            "rider": 0
        }

        # 遍历 detection_data 来填充实际 count
        for data in detection_data.values():
            raw_class_name = data["class_name"]
            # 用正则去除括号和里面的内容，例如 "car (0.89)" -> "car"
            class_name = re.sub(r"\s*\(.*?\)", "", raw_class_name).strip()
            count = data["count"]
            if class_name in class_counts:
                class_counts[class_name] = count

        update_sql = text(f"""
            UPDATE {table_name}
            SET conf = :conf,
                bus = :bus,
                trafficlight = :trafficlight,
                trafficsign = :trafficsign,
                person = :person,
                bike = :bike,
                truck = :truck,
                motor = :motor,
                car = :car,
                train = :train,
                rider = :rider
            WHERE detection_id = :detection_id
        """)

        with engine.begin() as conn:
            conn.execute(update_sql, {
                "conf": conf,
                "detection_id": detection_id,
                **class_counts  # 解包 counts 作为参数
            })

# 获取指定日期的检测记录（用于历史查询）
def get_detection_results_by_date(date: Optional[str] = None):
    """
    查询指定日期的检测记录（不传则默认今天）
    参数格式：date='2025-04-14'
    """
    if date:
        table_name = f"detect_log_{date.replace('-', '')}"
    else:
        table_name = get_today_table_name()

    with engine.connect() as conn:
        query_sql = text(f"""
            SELECT detection_id, processed_file, bus, trafficlight, trafficsign, person, bike,
                   truck, motor, car, train, rider, conf
            FROM {table_name}
            ORDER BY id ASC
        """)
        try:
            result = conn.execute(query_sql).fetchall()

            # 转为可序列化的字典列表
            result_list = []
            new_detection_id = 1  # 或从0开始，看需求

            for row in result:
                processed_file = row[1]
                if processed_file:  # 只添加非空 processed_file 的记录
                    result_list.append({
                        "detection_id": new_detection_id,
                        "processed_file": processed_file,
                        "bus": row[2],
                        "trafficlight": row[3],
                        "trafficsign": row[4],
                        "person": row[5],
                        "bike": row[6],
                        "truck": row[7],
                        "motor": row[8],
                        "car": row[9],
                        "train": row[10],
                        "rider": row[11],
                        "conf": row[12] if row[12] is not None else None
                    })
                    new_detection_id += 1

            return {"success": True, "data": result_list}

        except Exception as e:
            return {"success": False, "error": str(e), "message": f"可能是没有名为 {table_name} 的表"}


# FastAPI 路由处理函数，用于获取检测汇总数据
async def get_detection_summary_endpoint(request: Request):
    # 从查询参数中获取日期
    print("________________________________")
    summary = await get_detection_summary()
    print("summary:{summary}",summary)
    return summary

# 获取某一天的检测数据封装函数
def get_detection_data_by_date(date: Optional[str] = None):
    data = get_detection_results_by_date(date)
    return data