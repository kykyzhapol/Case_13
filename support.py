from datetime import datetime


def setup_data() -> dict:
    '''
    TODO:
    Функция для считывания первоначальных данный для моделирования.
    Пример файла на вход:
    1 3 АИ-80
    2 2 АИ-92
    3 4 АИ-92 АИ-95 АИ-98

    выход: {1: [3, [80]], 2: [2, [92]], 3: [4, [92, 95, 98]]}

    АИ-80, АИ-92, АИ-95, АИ-98 - единственные возможные варианты бензина.

    Данные поступают из файла setup.txt
    '''

    setup = {}
    with open('setup.txt', 'r', encoding='utf-8') as r:
        text = r.read().split('\n')
        r.close()

    for info in text:
        info_list = info.split(' ')

        num = info_list[0]
        info_list.remove(info_list[0])

        long = info_list[0]
        info_list.remove(info_list[0])

        for index in range(len(info_list)):
            info_list[index] = int(info_list[index][-2:])

        setup[int(num)] = [int(long), info_list]

    return setup


def data_for_analyzing() -> list[tuple]:
    '''
    TODO:
    При моделировании работы автозаправочной станции,
    заявки на обслуживание (т.е. приезд автомашин на заправку) поступают из файла input.txt

    Файл содержит следующие сведения, разделенные пробелом:
    <время> <количество литров бензина> <марка бензина>

    Данные поступают из файла input.txt
    На вывод идет список множеств
    '''

    with open('input.txt', 'r', encoding='utf-8') as r:
        text = r.read().split('\n')
        r.close()

    info = []
    for item in text:
        item = item.split(' ')
        t = datetime.strptime(item[0], '%H:%M')
        info.append((t, int(item[1]), int(item[2])))

    return info


def output_modeling(output_str: str) -> None:
    '''
    TODO:
    Функция, которая добавляет в файл вывода строку из моделирования
    :param output_str:
    :return:
    Вывод в output.txt
    '''

    with open('output.txt', 'a') as a:
        a.write(output_str)
        a.write('\n')
        a.close()


def oil_price() -> dict:
    '''
    TODO:
    При расчетах используется цена бензина, которая должна быть представлена в виде словаря.
    Установите текущую рыночную стоимость бензина каждой марки.

    Было бы круто, если цена подгружалась из интернета в реальном времени, но вообще можно просто взять
    и вернуть фиксированные значения.
    Ключ словаря - цифра октанового числа, значение - цена (до 2х знаков после запятой)
    :return price:
    '''

    price = {80: 54.23, 92: 60.53, 95: 64.97, 98: 85.05}
    return price
