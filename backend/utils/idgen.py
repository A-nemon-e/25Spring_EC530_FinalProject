import uuid

def generate_uuid():
    """生成 UUID 字符串，用于文件/文件夹主键"""
    return str(uuid.uuid4())

# # 生成一个测试用 UUID 作为示例
# sample_id = generate_uuid()
# print(sample_id)



# 用法：

# from utils.idgen import generate_uuid

# file_id = generate_uuid()
