import hashlib


def human_size(sz):
    """
    以人类可读的格式返回大小
    """
    if not sz:
        return False
    units = ('bytes', 'Kb', 'Mb', 'Gb')
    s, i = float(sz), 0
    while s >= 1024 and i < len(units) - 1:
        s /= 1024
        i += 1
    return "%0.2f %s" % (s, units[i])


def get_hash(file, block_size=65536):
    """
    获取文件的哈希信息

    :param file: 文件路径
    :param block_size: 读取缓存大小
    :return: {'md5', '', 'sha1', '', 'hash', '', }
    """

    calc_md5 = hashlib.md5()
    calc_sha1 = hashlib.sha1()
    calc_hash = hashlib.sha256()

    with open(file, 'rb') as fd:
        data_chunk = fd.read(block_size)
        while data_chunk:
            calc_md5.update(data_chunk)
            calc_sha1.update(data_chunk)
            calc_hash.update(data_chunk)
            data_chunk = fd.read(block_size)

    results = {
        'md5': calc_md5.hexdigest(),
        'sha1': calc_sha1.hexdigest(),
        'hash': f'sha256:{calc_hash.hexdigest()}',  # sha256[哈希算法名字，统一用小写]:[分隔符]128[哈希]，最多字符数 136
    }

    return results
