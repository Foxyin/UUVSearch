"""
UUVSearch - TensorBoard 日志工具
"""
from torch.utils.tensorboard import SummaryWriter

class Logger:
    def __init__(self, log_dir="experiments/logs"):
        self.writer = SummaryWriter(log_dir)

    def log_scalar(self, tag, value, step):
        self.writer.add_scalar(tag, value, step)

    def log_scalars(self, main_tag, tag_scalar_dict, step):
        self.writer.add_scalars(main_tag, tag_scalar_dict, step)

    def close(self):
        self.writer.close()