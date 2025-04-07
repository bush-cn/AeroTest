import logging
import os
from datetime import datetime

from config import LOG_DIR


# 创建一个日志器
logger = logging.getLogger('AeroTest')
logger.setLevel(logging.DEBUG)  # 设置日志级别

# 创建一个日志文件处理器
log_dir = LOG_DIR
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 获取当前日期并格式化为 YYYYMMDD 的形式
current_date = datetime.now().strftime("%Y%m%d")

# 将日期加入到日志文件名中
log_file = os.path.join(log_dir, f'{current_date}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# 创建一个控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 控制台输出设置为INFO级别

# 定义日志输出的格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将处理器添加到日志器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# logger.info("Logging is configured!")
