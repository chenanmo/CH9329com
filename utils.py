from __future__ import annotations


def get_packet(
    head: bytes, addr: bytes, cmd: bytes, length: bytes, data: bytes
):
    """
    累加和计算工具
    :param head:
    :param addr:
    :param cmd:
    :param length:
    :param data:
    :return: 返回累加和
    """
    head_hex_list = list(head)
    head_hex_sum = sum(head_hex_list)
    data_hex_list = list(data)
    data_hex_sum = sum(data_hex_list)
    checksum = (
        sum(
            [
                head_hex_sum,
                int.from_bytes(addr, byteorder="big"),
                int.from_bytes(cmd, byteorder="big"),
                int.from_bytes(length, byteorder="big"),
                data_hex_sum,
            ]
        )
        % 256
    )
    packet = head + addr + cmd + length + data + bytes([checksum])
    return packet
