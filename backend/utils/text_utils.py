

import hashlib
from typing import List, Union


def get_text_cache_key(text: Union[str, List[str]]) -> str:
    """生成文本的缓存键"""
    if isinstance(text, list):
        # 对于文本列表，连接所有文本再生成哈希
        combined = "".join(text)
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    else:
        # 对于单个文本字符串
        return hashlib.md5(text.encode('utf-8')).hexdigest()

