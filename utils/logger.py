"""
UUVSearch - TensorBoard 日志工具
"""
import os
import socket
from torch.utils.tensorboard import SummaryWriter


class Logger:
    def __init__(self, log_dir="experiments/logs"):
        # 避免 Windows 中文主机名导致的文件名编码问题
        saved_hostname = socket.gethostname()
        try:
            socket.gethostname = lambda: 'localhost'
            os.makedirs(log_dir, exist_ok=True)
            self.writer = SummaryWriter(log_dir)
        finally:
            socket.gethostname = lambda: saved_hostname

    def log_scalar(self, tag, value, step):
        self.writer.add_scalar(tag, value, step)

    def log_scalars(self, main_tag, tag_scalar_dict, step):
        self.writer.add_scalars(main_tag, tag_scalar_dict, step)

    def close(self):
        self.writer.close()