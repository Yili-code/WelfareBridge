"""給人看的數字格式：整數加千分位，小數保留有效位數；不會輸出 6.5e+06 這種科學記號。"""


def fmt_num(value) -> str:
    number = float(value)
    return f"{int(number):,}" if number == int(number) else f"{number:g}"
