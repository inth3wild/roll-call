import sys
import requests
import pendulum
import re
import time
import random

from settings.config import env, blue_colored_icon, red_colored_icon, green_colored_icon
from zk import ZK, const



s = requests.Session()


def get_user(reg_no, zk):
    ''' Get a particular user from list of users in the Machine '''
    try:
        # Connect to device
        conn = zk.connect()

        # Disable device, this method ensures no activity on the device while the process is run
        conn.disable_device()

        users = conn.get_users()

        for element in users:
            if element.user_id == reg_no:
                # print(element)  

                # Re-enable device after all commands already executed
                conn.enable_device()
                return element
        print(f"{red_colored_icon} Reg No not found, Please confirm your Reg No")
        close_script()
    except Exception as e:
        print(f"{red_colored_icon} Error: {e}")
        close_script()


def login(session, hall):
    ''' Login to the machine '''
    
    url = f'http://{hall}/'
    login_endpoint = f'http://{hall}/csl/check'
    non_existent_endpoint = f'http://{hall}/a'

    post_body = {
        'username': env.get('ROLL_CALL_USERNAME'),
        'userpwd': env.get('ROLL_CALL_PASSWORD'),
    }

    try:
        # Try to get session cookie assigned by visiting home route first
        r1 = session.get(url)
        
        if 'set-cookie' in r1.headers:
            pass
        else:
            print(f'{red_colored_icon} No Cookie Set, Retrying...\n', end=" ", flush=True)
            # Try to get session cookie again, this time by visiting a route that doesn't exist.
            r2 = session.get(non_existent_endpoint)
            # session.close()
            login(session, hall)

        response = session.post(login_endpoint, data=post_body, allow_redirects=False)
        return
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
        print(f"{red_colored_icon} Error: {e}")
        close_script()




def get_attendance(user_object, session, today, hall):
    ''' Get users roll call attendance for the week '''

    # Log in first to get an authenticated session
    login(session, hall)

    query_endpoint = f'http://{hall}/csl/query?action=run'

    post_body = {
        'sdate': f"{ today.start_of('week').format('YYYY-MM-DD') }",
        'edate': f"{ today.end_of('week').format('YYYY-MM-DD') }",
        'period': 3,
        'uid': user_object.uid
    }

    try:
        response = session.post(query_endpoint, data=post_body, allow_redirects=False)
        # print(response.text)
        return response.text
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
        print(f"{red_colored_icon} Error: {e}")
        close_script()



def calculate_date(attendance_response, today):
    ''' Calculate Days user has not signed roll call '''

    days_not_signed = []

    week_start = today.start_of('week')
    week_end = today.end_of('week')

    # Get all dates for the week
    week_range_dates = pendulum.period(week_start, week_end)

    # Regex to parse the days user signed roll call from machine response
    days_signed = re.findall(r'\d{4}-\d{2}-\d{2}', attendance_response)

    for day in week_range_dates:
        if day.format('YYYY-MM-DD') not in days_signed:
            days_not_signed.append( day.format('YYYY-MM-DD') )

    return days_not_signed


def display_info(days_not_signed, today, user_object):
    ''' Display Info on days user didn't sign '''

    days_before_today = {}
    days_after_today = {}

    print(f"\n{blue_colored_icon} Name: {user_object.name} \n\n{blue_colored_icon} Days you haven't signed Roll Call: ")

    for day in days_not_signed:
        # Parse day to be in datetime format
        parsed_day = pendulum.parse(day)
        # Check if date is before current date else it's after current date
        if parsed_day < today:
            days_before_today[parsed_day.format('YYYY-MM-DD')] = parsed_day.format(" dddd DD MMMM YYYY ")
        else:
            days_after_today[parsed_day.format('YYYY-MM-DD')] = parsed_day.format(" dddd DD MMMM YYYY ")
    
    print('\t --Today OR Before Today-- ')
    if days_before_today != []:
        for day in days_before_today:
            print(f'{green_colored_icon} {day} : {days_before_today.get(day)}')
    else:
        print(f'{blue_colored_icon} None')

    
    print('\n \t --After Today-- ')
    if days_after_today != []:
        for day in days_after_today:
            print(f'{green_colored_icon} {day} : {days_after_today.get(day)}')
    else:
        print(f'{red_colored_icon} None')
    

def change_time(days_not_signed, proceed_input, today, zk):
    ''' Change time and date for roll call machine '''
    try:
        conn = zk.connect()

        if proceed_input == 'a':
            for day in days_not_signed:
                # Generate random number so user signs roll call between 9:10 and 9:50
                random_minute = random.randint(10,50)
                parsed_day = pendulum.parse(day + f'T21:{random_minute}:40+01:00')
                
                # Wait some seconds before changing the time again
                time.sleep(5)

                print(f'\n{blue_colored_icon} Changing date and time to: {parsed_day.format("YYYY-MM-DD @ HH:mm A")}')
                # conn.set_time(parsed_day)
            # Wait some seconds before changing the time again
            time.sleep(5)
            print(f'\n{blue_colored_icon} Resetting date and time...')
            conn.set_time(today)
        elif proceed_input == 'p':
            for day in days_not_signed:
                # Parse day to be in datetime format
                parsed_day = pendulum.parse(day)
                # Check if date is before current date
                if parsed_day < today:
                    random_minute = random.randint(10,50)
                    parsed_day = pendulum.parse(day + f'T21:{random_minute}:40+01:00')
                
                    # Wait some seconds before changing the time again
                    time.sleep(5)

                    print(f'\n{blue_colored_icon} Changing date and time to: {parsed_day.format("YYYY-MM-DD @ HH:mm A")}')
                    # conn.set_time(parsed_day)
            # Wait some seconds before changing the time again
            time.sleep(5)
            print(f'\n{blue_colored_icon} Resetting date and time...')
            conn.set_time(today)
        else:
            print(f"{red_colored_icon} Input should either be a OR p")
            close_script()


        # conn = zk.connect()
        # zktime = conn.get_time()
        # print(zktime)
    except Exception as e:
        print(f'{red_colored_icon} Error: {e}')
        close_script()


def close_script():
    ''' Exit the program Gracefully '''
    sys.exit()



def start():

    reg_no = input(f'{blue_colored_icon} Enter your reg no: ')

    print(f'''{blue_colored_icon} Halls:
    1) Daniel Hall \t 2) Dorcas Hall

    3) Abraham Hall \t 4) Sarah Hall

    5) Isaac Hall \t 6) Abigail Hall

    7) Joseph Hall
    ''')

    hall_input = input(f'{blue_colored_icon} Enter your Hall no: ')

    if hall_input == '1':
        hall = env.get('DANIEL_ROLL_CALL_IP')

    elif hall_input == '2':
        hall = env.get('DORCAS_ROLL_CALL_IP')

    elif hall_input == '3':
        print(f"{red_colored_icon} Sorry, don't have the address for Abraham hall yet 😞")
        close_script()
        # hall = env.get('ABRAHAM_ROLL_CALL_IP')

    elif hall_input == '4':
        hall = env.get('SARAH_ROLL_CALL_IP')

    elif hall_input == '5':
        hall = env.get('ISAAC_ROLL_CALL_IP')

    elif hall_input == '6':
        hall = env.get('ABIGAIL_ROLL_CALL_IP')

    elif hall_input == '7':
        hall = env.get('JOSEPH_ROLL_CALL_IP')
    
    else:
        print(f'{red_colored_icon} Enter a valid hall no')
        close_script()


    # Create ZK instance
    zk = ZK(hall, port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)


    user_object = get_user(reg_no, zk)

    #  Get today's date
    today = pendulum.now()
    # today = pendulum.datetime(2022, 3, 17)
 
    attendance_response = get_attendance(user_object, s, today, hall)

    days_not_signed = calculate_date(attendance_response, today)

    display_info(days_not_signed, today, user_object)

    if days_not_signed != []:
        proceed_input = input(f'\n{blue_colored_icon} Do you want to sign for all days (a) OR Past days (p) (a/p): ')

        if proceed_input and days_not_signed != []:
            change_time(days_not_signed, proceed_input.lower(), today, zk)
        else:
            print(f'{red_colored_icon} Closing...')
            close_script()
    else:
        print(f"\n{blue_colored_icon}  You didn't miss any day, Pele oh good student 🙄")
        close_script()

    print(f'{blue_colored_icon} Done 🤖')
    close_script()



if __name__ == "__main__":
    start()