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
    Calculate refueling time in minutes based on fuel volume.

    Average refueling speed is 10 liters per minute. The actual time
    can vary randomly by -1, 0, or +1 minute to simulate real-world
    variations in refueling speed.

    Args:
        size (float): Fuel volume to refuel in liters

    Returns:
        int: Refueling time in minutes, minimum 1 minute

    Example:
        refueling_speed(20)
        2  # May vary due to random variation
    '''
    # Calculate base time assuming 10 liters per minute
    base_time = math.ceil(size / 10)

    # Random variation: -1, 0, or +1 minute to simulate real conditions
    variation = random.choice([-1, 0, 1])

    # Ensure minimum refueling time of 1 minute
    final_time = max(1, base_time + variation)

    return final_time


def add_minutes_to_time(t: datetime, minutes: int) -> datetime:
    '''
    Add specified minutes to a datetime object.

    Creates a new datetime object by adding the given number of minutes
    to the input datetime. Original object remains unchanged.

    Args:
        t (datetime): Base datetime to add minutes to
        minutes (int): Number of minutes to add

    Returns:
        datetime: New datetime object with added minutes
    '''
    return t + timedelta(minutes=minutes)


def find_available_pump(oil_type: int, current_queues: dict,
                        setup_data: dict) -> int | None:
    '''
    Find suitable pump for refueling based on fuel type and queue status.

    Searches through all pumps to find one that:
    1. Supports the required fuel type
    2. Has available queue slots
    Then selects the pump with the shortest queue among available options.

    Args:
        oil_type (int): Type of fuel needed (80, 92, 95, or 98)
        current_queues (dict): Current state of all pumps with queues
        setup_data (dict): Pump configuration data with max queues and fuel types

    Returns:
        int | None: Pump number if available, None if no suitable pump found
    '''
    available_pumps = []

    for pump_num, pump_info in setup_data.items():
        max_queue, available_oils = pump_info[0], pump_info[1]

        # Check if pump supports required fuel and has free queue slots
        if oil_type in available_oils:
            if current_queues[pump_num][0] < max_queue:
                available_pumps.append(pump_num)

    if available_pumps:
        # Select pump with shortest queue for optimal customer distribution
        return min(available_pumps, key=lambda x: current_queues[x][0])
    else:
        return None


def print_pump_status(current_queues: dict, setup_data: dict) -> None:
    '''
    Display current status of all pumps with their queues.

    Prints for each pump:
    - Pump number
    - Maximum queue length
    - Available fuel types
    - Current queue visualization using asterisks

    Args:
        current_queues (dict): Current queue states for all pumps
        setup_data (dict): Pump configuration data
    '''
    for pump_num, pump_info in setup_data.items():
        max_queue = pump_info[0]
        available_oils = pump_info[1]
        current_queue_length = current_queues[pump_num][0]

        # Create readable string of available fuel grades
        oils_str = ' '.join([f'{RU_TRANSLATION_1}-{oil}' for oil
                             in available_oils])

        # Visual representation of queue length with asterisks
        queue_indicator = '*' * current_queue_length
        out_str = (f'{RU_TRANSLATION_2}{pump_num} {RU_TRANSLATION_3} '
                   f'{max_queue} {RU_TRANSLATION_4} {oils_str} '
                   f'->{queue_indicator}')
        print(out_str)
        sup.output_modeling(out_str)


def main() -> None:
    '''
    Main gas station simulation function.

    Simulates customer arrivals, refueling process, and departures:
    1. Prepares customer data with arrival times and required fuel
    2. Calculates refueling times for each customer
    3. Manages pump queues and customer assignments
    4. Tracks sales statistics and rejected customers
    5. Records all events (arrivals/departures) in chronological order
    '''
    # Create dictionary with arrival and departure times for each customer
    prepared_data = {}
    for slot in range(len(analyzing_data)):
        prepared_data[slot] = [*analyzing_data[slot],
                               add_minutes_to_time(analyzing_data[slot][0],
                               refueling_speed(analyzing_data[slot][1]))]

    # Initialize queue state for all pumps
    # Format: {pump_number: [current_queue_length, max_queue, customer_list]}
    current_queues = {}
    for pump_num in setup_data.keys():
        # Structure: [current_length, max_length, list_of_customers]
        current_queues[pump_num] = [0, setup_data[pump_num][0], []]

    # Statistics tracking
    total_sold = {80: 0, 92: 0, 95: 0, 98: 0}  # Liters sold per fuel type
    total_revenue = 0  # Total revenue in currency units
    rejected_customers = 0  # Number of customers who left due to no availability

    # Event queue for simulation
    all_events = []

    # Prepare initial arrival events for all customers
    for car_num, car_data in prepared_data.items():
        arrival_time, volume, oil_type, departure_time = car_data
        all_events.append((arrival_time, 'arrival', car_num, volume,
                           oil_type, departure_time))

    # Sort events chronologically for processing
    all_events.sort(key=lambda x: x[0])

    # Main simulation event loop
    for event in all_events:
        (event_time, event_type, car_num, volume, oil_type,
         departure_time) = event

        if event_type == 'arrival':
            # Handle customer arrival - find available pump
            pump_num = find_available_pump(oil_type, current_queues,
                                           setup_data)

            if pump_num is not None:
                # Customer can be served - add to pump queue
                current_queues[pump_num][0] += 1
                # Store max queue capacity (from setup)
                current_queues[pump_num][1] = setup_data[pump_num][0]
                # Add customer to pump's customer list
                current_queues[pump_num][2].append({
                    'car_num': car_num,
                    'arrival_time': event_time,
                    'volume': volume,
                    'oil_type': oil_type,
                    'departure_time': departure_time
                })

                out_str = (f'\n{IN} {event_time.strftime('%H:%M')} '
                           f'{RU_TRANSLATION_5_1} '
                           f'{event_time.strftime('%H:%M')} '
                           f'{RU_TRANSLATION_1}-{oil_type} {volume} '
                           f'{car_num + 1} {RU_TRANSLATION_6}{pump_num}')
                print(out_str)
                sup.output_modeling(out_str)
                print_pump_status(current_queues, setup_data)

                # Schedule departure event for this customer
                all_events.append((departure_time, 'departure', car_num,
                                   volume, oil_type, pump_num))
            else:
                # No available pump - customer leaves
                rejected_customers += 1
                out_str = (f'\n{IN} {event_time.strftime('%H:%M')} '
                           f'{RU_TRANSLATION_5_2}'
                           f'{event_time.strftime('%H:%M')} '
                           f'{RU_TRANSLATION_1}-{oil_type} {volume} '
                           f'{car_num + 1} {RU_TRANSLATION_7}')
                print(out_str)
                sup.output_modeling(out_str)
                print_pump_status(current_queues, setup_data)

            # Re-sort events after adding new departure event
            all_events.sort(key=lambda x: x[0])

        elif event_type == 'departure':
            # Handle customer departure after refueling
            pump_num = departure_time  # Parameter reuse: now contains pump number

            # Update sales statistics
            total_sold[oil_type] = total_sold.get(oil_type, 0) + volume
            total_revenue += volume * oil_price.get(oil_type, 0)

            # Remove customer from pump queue
            for i, customer in enumerate(current_queues[pump_num][2]):
                if customer['car_num'] == car_num:
                    current_queues[pump_num][2].pop(i)
                    current_queues[pump_num][0] -= 1
                    break

            out_str = (f'\n{IN} {event_time.strftime('%H:%M')} '
                       f'{RU_TRANSLATION_5_2} '
                       f'{prepared_data[car_num][0].strftime('%H:%M')}'
                       f' {RU_TRANSLATION_1}-{oil_type} {volume} {car_num + 1}'
                       f' {RU_TRANSLATION_8}')
            print(out_str)
            sup.output_modeling(out_str)
            print_pump_status(current_queues, setup_data)

    # Display final simulation statistics
    print('\n' + '=' * 50,
          f'{RU_TRANSLATION_9}',
          '=' * 50)
    sup.output_modeling(f'{RU_TRANSLATION_9}')

    # Show fuel sales by type
    out_str = f'\n{RU_TRANSLATION_10}'
    print(out_str)
    for oil_type, liters in total_sold.items():
        if liters > 0:
            out_str = (f'{RU_TRANSLATION_1}-{oil_type}: {liters} '
                       f'{RU_TRANSLATION_14}')
            print(out_str)
            sup.output_modeling(out_str)

    # Show total revenue and rejected customers
    out_str = (f'\n{RU_TRANSLATION_11} {total_revenue} {RU_TRANSLATION_13}'
               f'\n{RU_TRANSLATION_12} {rejected_customers}')
    print(out_str)
    sup.output_modeling(out_str)


if __name__ == '__main__':
    main()
