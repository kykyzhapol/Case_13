from datetime import timedelta, datetime
import math
import random
from ru_local import *

import support as sup


setup_data = sup.setup_data_input()
analyzing_data = sup.data_for_analyzing()
oil_price = sup.fresh_oil_price()


def refueling_speed(size: float) -> int:
    '''
    Calculate refueling time.
    Average refueling speed: 10 liters per minute.
    However, this value can be randomly increased or decreased by 1 minute,
    or remain unchanged.

    Args:
        size: Fuel volume to refuel (liters)

    Returns:
        minutes: Refueling time in minutes
    '''
    # Calculate base time (10 liters per minute)
    base_time = math.ceil(size / 10)

    # Random variation: -1, 0, or +1 minute
    variation = random.choice([-1, 0, 1])

    # Apply variation but ensure time is at least 1 minute
    final_time = max(1, base_time + variation)

    return final_time


def add_minutes_to_time(t: datetime, minutes: int) -> datetime:
    '''Add minutes to a datetime object and return a new datetime object'''
    return t + timedelta(minutes=minutes)


def find_available_pump(oil_type, current_queues, setup_data):
    '''Find a suitable pump for refueling'''
    available_pumps = []

    for pump_num, pump_info in setup_data.items():
        max_queue, available_oils = pump_info[0], pump_info[1]

        # Check if the required fuel type is available and if there are free queue slots
        if oil_type in available_oils:
            if current_queues[pump_num][0] < max_queue:
                available_pumps.append(pump_num)

    if available_pumps:
        # Select the pump with the shortest queue
        return min(available_pumps, key=lambda x: current_queues[x][0])
    else:
        return None


def print_pump_status(current_queues, setup_data):
    '''Display current status of all pumps'''
    for pump_num, pump_info in setup_data.items():
        max_queue = pump_info[0]
        available_oils = pump_info[1]
        current_queue_length = current_queues[pump_num][0]

        # Create string with fuel grades
        oils_str = ' '.join([f'{RU_TRANSLATION_1}-{oil}' for oil in available_oils])

        # Create queue indicator
        queue_indicator = '*' * current_queue_length
        out_str = f'{RU_TRANSLATION_2}{pump_num} {RU_TRANSLATION_3} {max_queue} {RU_TRANSLATION_4} {oils_str} ->{queue_indicator}'
        print(out_str)
        sup.output_modeling(out_str)


def main() -> None:
    # Create dictionary with arrival and departure times for each customer
    prepared_data = {}
    for slot in range(len(analyzing_data)):
        prepared_data[slot] = [*analyzing_data[slot],
                               add_minutes_to_time(analyzing_data[slot][0],
                                                   refueling_speed(analyzing_data[slot][1]))]

    # Create dictionary for current queue state
    # Format: {pump_number: [current_queue_length, max_queue, customer_list]}
    current_queues = {}
    for pump_num in setup_data.keys():
        current_queues[pump_num] = [0, setup_data[pump_num][0], []]  # [current_length, max_length, customer_list]

    # Statistics
    total_sold = {80: 0, 92: 0, 95: 0, 98: 0}
    total_revenue = 0
    rejected_customers = 0

    # List of all events (arrivals and departures)
    all_events = []

    # Prepare arrival events
    for car_num, car_data in prepared_data.items():
        arrival_time, volume, oil_type, departure_time = car_data
        all_events.append((arrival_time, 'arrival', car_num, volume, oil_type, departure_time))

    # Sort events by time
    all_events.sort(key=lambda x: x[0])

    # Main simulation loop
    for event in all_events:
        event_time, event_type, car_num, volume, oil_type, departure_time = event

        if event_type == 'arrival':
            # Check if there's a suitable pump available
            pump_num = find_available_pump(oil_type, current_queues, setup_data)

            if pump_num is not None:
                # Add customer to queue
                current_queues[pump_num][0] += 1
                current_queues[pump_num][1] = setup_data[pump_num][0]  # update max value
                current_queues[pump_num][2].append({
                    'car_num': car_num,
                    'arrival_time': event_time,
                    'volume': volume,
                    'oil_type': oil_type,
                    'departure_time': departure_time
                })

                out_str = f'\n{IN} {event_time.strftime('%H:%M')} {RU_TRANSLATION_5_1} {event_time.strftime('%H:%M')} {RU_TRANSLATION_1}-{oil_type} {volume} {car_num + 1} {RU_TRANSLATION_6}{pump_num}'
                print(out_str)
                sup.output_modeling(out_str)
                print_pump_status(current_queues, setup_data)

                # Add departure event
                all_events.append((departure_time, 'departure', car_num, volume, oil_type, pump_num))
            else:
                # Customer leaves
                rejected_customers += 1
                out_str = f'\n{IN} {event_time.strftime('%H:%M')} {RU_TRANSLATION_5_2} {event_time.strftime('%H:%M')} {RU_TRANSLATION_1}-{oil_type} {volume} {car_num + 1} {RU_TRANSLATION_7}'
                print(out_str)
                sup.output_modeling(out_str)
                print_pump_status(current_queues, setup_data)

            # Sort events again after adding new one
            all_events.sort(key=lambda x: x[0])

        elif event_type == 'departure':
            # Customer leaves gas station after refueling
            pump_num = departure_time  # this field now contains pump number

            # Update statistics
            total_sold[oil_type] = total_sold.get(oil_type, 0) + volume
            total_revenue += volume * oil_price.get(oil_type, 0)

            # Remove customer from queue
            for i, customer in enumerate(current_queues[pump_num][2]):
                if customer['car_num'] == car_num:
                    current_queues[pump_num][2].pop(i)
                    current_queues[pump_num][0] -= 1
                    break
            out_str = f'\n{IN} {event_time.strftime('%H:%M')} {RU_TRANSLATION_5_2} {prepared_data[car_num][0].strftime('%H:%M')} {RU_TRANSLATION_1}-{oil_type} {volume} {car_num + 1} {RU_TRANSLATION_8}'
            print(out_str)
            sup.output_modeling(out_str)
            print_pump_status(current_queues, setup_data)

    # Display final statistics
    print('\n' + '=' * 50,
          f'{RU_TRANSLATION_9}',
          '=' * 50)
    sup.output_modeling(f'{RU_TRANSLATION_9}')

    out_str = f'\n{RU_TRANSLATION_10}'
    print(out_str)
    for oil_type, liters in total_sold.items():
        if liters > 0:
            out_str = f'{RU_TRANSLATION_1}-{oil_type}: {liters} {RU_TRANSLATION_14}'
            print(out_str)
            sup.output_modeling(out_str)

    out_str = (f'\n{RU_TRANSLATION_11} {total_revenue} {RU_TRANSLATION_13}'
               f'\n{RU_TRANSLATION_12} {rejected_customers}')
    print(out_str)
    sup.output_modeling(out_str)


if __name__ == '__main__':
    main()
