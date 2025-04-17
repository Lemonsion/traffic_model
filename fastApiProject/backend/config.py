class Config:
    # --------------全局配置参数-------------
    global_conf = 0.7  # 全局配置的默认置信度阈值，决定检测结果是否有效（0.7为默认值）

    global_iou = 0.7  # 默认IOU阈值，决定目标框是否匹配（0.7为默认值）

    warning_or_not = 0  # 是否警告过，0表示否，1表示是

    warning_count = 0  # 警告计数器，用于记录触发警告的次数

    video_or_not = 0  # 视频流状态，0表示非视频流，1表示是视频流

    reset_thread_running = False  # 线程重置标志，表示是否正在重置线程
