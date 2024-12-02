import random
import string
from typing import List


def generate_code(length=4) -> str:
    ascii_upp: List[str] = random.choices(string.ascii_uppercase, k=6)
    integer_list: List[int] = [random.randint(0, 9) for _ in range(7)]
    full_list = ascii_upp + [str(num) for num in integer_list]
    random.shuffle(full_list)
    return ''.join(full_list[:length])


