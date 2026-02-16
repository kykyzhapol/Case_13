'''
В этом файле будет располагаться основная часть кода.
В файле support
'''
import math
import random


setup_data = {1: [3, [80]], 2: [2, [92]], 3: [4, [92, 95, 98]]}
analyzing_data = [{'10:36', 15, 80}, {'10:55', 50, 92}, {'10:56', 100, 92}]
oil_price = {80: 45, 92: 50, 98: 55}


def refueling_speed(size: float) -> int:
    '''
    расчет скорости заправки
    Средняя скорость заправки: 10 литров в минуту.
    Однако, эта величина случайным образом может быть увеличена или уменьшена на 1 минуту,
    либо остаться неизменной.
    :param size: объем топлива для заправки (литры)
    :return minutes: время заправки в минутах
    '''
    # Calculate base time (10 liters per minute)
    base_time = math.ceil(size / 10)

    # Random variation: -1, 0, or +1 minute
    variation = random.choice([-1, 0, 1])

    # Apply variation but ensure time is at least 1 minute
    final_time = max(1, base_time + variation)

    return final_time


def main() -> None:
    for i in range(len(setup_data)):
        print(f'Автомат {i}, максимальная очередь {setup_data[i][1]}, марка бензина АИ-{setup_data[i][2]}')

