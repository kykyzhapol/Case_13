from datetime import datetime


def setup_data_input() -> dict:
    '''
    Function for reading initial data for simulation.
    Example input file:
    1 3 AI-80
    2 2 AI-92
    3 4 AI-92 AI-95 AI-98

    Output: {1: [3, [80]], 2: [2, [92]], 3: [4, [92, 95, 98]]}

    AI-80, AI-92, AI-95, AI-98 are the only possible fuel grades.

    Data is read from setup.txt file
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


def data_for_analyzing() -> list[list]:
    '''
    During gas station simulation,
    service requests (i.e., cars arriving for refueling) are read from input.txt file.

    The file contains the following information, space-separated:
    <time> <liters of fuel> <fuel grade>

    Data is read from input.txt file
    Returns a list of lists
    '''

    with open('input.txt', 'r', encoding='utf-8') as r:
        text = r.read().split('\n')
        r.close()

    info = []
    for item in text:
        item = item.split(' ')
        t = datetime.strptime(item[0], '%H:%M')
        info.append([t, int(item[1]), int(item[2])])

    return info


def output_modeling(output_str: str) -> None:
    '''
    Function that appends a simulation output string to the output file

    Args:
        output_str: String to write to output file

    Returns:
        None

    Output is written to output.txt
    '''

    with open('output.txt', 'a', encoding='UTF-8') as a:
        a.write(output_str)
        a.write('\n')


def fresh_oil_price() -> dict:
    '''
    Fuel prices are used in calculations and should be represented as a dictionary.
    Returns current market price for each fuel grade.

    Dictionary key - octane number, value - price (up to 2 decimal places)

    Returns:
        price: Dictionary with fuel prices by octane number
    '''

    price = {80: 54.23, 92: 60.53, 95: 64.97, 98: 85.05}
    return price
