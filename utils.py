import pandas as pd
from flask import session
from PIL import Image
import os
from datetime import datetime, timedelta
import pytz
from config import Date_col, Lounge_ID_Col, CLName_Col, Volume_ID_Col, Refuse_Col, Ratio_Col, users, time_alert, crowdedness_alert, Airport_Name_Col, City_Name_Col, Country_Name_Col, plot_interval, plot_gradient_intensity
from conversion import convert_to_secure_name

def update_time_alert(new_value):
    global time_alert
    time_alert = new_value
def update_plot_interval(new_value):
    global plot_interval
    plot_interval = new_value
    
def logo_render(client):
    logo_path = 'static/image/'  # Path to your logo image
    secure_name = convert_to_secure_name(client)

    logo_file = f'{secure_name}.png'
    logo_full_path = os.path.join(logo_path, logo_file)

    if os.path.exists(logo_full_path):
        logo = Image.open(logo_full_path)
        return logo
    else:
        return None




def load_data():
    df = pd.read_csv('fake_data.txt')
    # df = pd.read_csv("real_data.txt")
    df[Date_col] = pd.to_datetime(df[Date_col])
    
    return df

def range_filter(df, from_, to_, column_name):
    if pd.notna(from_) and pd.notna(to_):
        df = df[(df[column_name] >= from_) & (df[column_name] <= to_)]
    elif pd.notna(from_):
        df = df[(df[column_name] >= from_)]
    elif pd.notna(to_):
        df = df[(df[column_name] <= to_)]

    return df


def filter_data_by_cl(username, df, selected_client, access_clients):
    
    if selected_client:

        if isinstance(selected_client, list):
            if selected_client == access_clients or set(selected_client).issubset(access_clients):
                filtered_df = df[df[CLName_Col].isin(selected_client)]
            else:
                filtered_df = None
        else:
            
            if selected_client in access_clients:
                filtered_df = df[df[CLName_Col] == str(selected_client)]
            else:
                filtered_df = None

    elif users[username]['ClientID'] == 'admin':
        return df
    else:
        # filtered_df = df[df[CLName_Col] == users[username]['AccessCL']]
        filtered_df = df[df[CLName_Col].isin(list(users[username]['AccessCL']))]

    return filtered_df


def dropdown_menu_filter(df, col_name,selected_val):    
    filtered_df = df[df[col_name] == selected_val]


    return filtered_df



def LoungeCounter(name, modality='cl'):
    df = load_data()
    if modality == 'cl':
        unique_count = df.loc[df[CLName_Col] == name, Lounge_ID_Col].nunique()
        return unique_count
    elif modality == 'lg':
        cl = df.loc[df[Lounge_ID_Col] == name][CLName_Col][-1:].values[0]
        unique_count = LoungeCounter(name=cl)
        return unique_count, cl

def ParameterCounter(name,base, to_be_counted):
    df = load_data()
    
    unique_vals = df.loc[df[base] == name, to_be_counted].unique()
    unique_count = len(unique_vals)
    return unique_vals, unique_count
  


def stream_on_off(scale='sec', length=10):
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    no_data = {}
    df = load_data()
    
    for i in access_clients:

        # Filter the DataFrame for the last record with id=X
        last_record = df[df[CLName_Col] == i].tail(1)
        # Get the timestamp of the last record
        last_time = last_record[Date_col].iat[0]

     

        # Calculate the time difference based on the specified scale and length
        if scale == 'sec':
            time_diff = datetime.now() - last_time
            threshold = timedelta(seconds=int(length))
        elif scale == 'min':
            time_diff = (datetime.now() - last_time) // timedelta(minutes=1)
            threshold = int(length)
        elif scale == 'hour':
            time_diff = (datetime.now() - last_time) // timedelta(hours=1)
            threshold = int(length)
        elif scale == 'day':
            time_diff = (datetime.now() - last_time) // timedelta(days=1)
            threshold = int(length)
        elif scale == 'mo':
            time_diff = (datetime.now() - last_time) // timedelta(days=30)
            threshold = int(length)
        elif scale == 'year':
            time_diff = (datetime.now() - last_time) // timedelta(days=365)
            threshold = int(length)
        else:
            raise ValueError("Invalid scale. Please choose one of 'sec', 'min', 'hour', 'day', 'min', or 'year'.")

        # Check if the time difference is more than the specified threshold

        # no_data[i] = [last_time-time_diff]

        if time_diff > threshold:
            # no_data[i].append(last_time)
            no_data[i] = last_time
        

    return no_data



def get_latest_lounge_status(df):
    current_date = datetime.now(pytz.UTC)
    latest_record = None
     
    for _, group_df in df.groupby([CLName_Col, Lounge_ID_Col]):
        group_df[Date_col] = pd.to_datetime(group_df[Date_col], format='%Y-%m-%d')
        # group_df[Date_col] = pd.to_datetime(group_df[Date_col], format='%Y-%m-%d %H:%M:%S')

        group_df = group_df.sort_values(Date_col, ascending=False)  # Sort by date in descending order
        latest_date = group_df.iloc[0][Date_col]

        # Ensure the latest date has the same timezone as current_date
        if latest_date.tzinfo is None:
            latest_date = pytz.UTC.localize(latest_date)
        else:
            latest_date = latest_date.astimezone(pytz.UTC)
        
        latest_record = group_df.iloc[0]
        break

    return latest_record


def convert_to_utc(date, time_difference, date_format, convert_option=None, local_timezone='EST', utc_timezone='UTC'):
    if convert_option is None:
        return date

    local_tz = pytz.timezone(local_timezone)
    utc_tz = pytz.timezone(utc_timezone)

    if isinstance(date, pd.Timestamp):
        # Convert pandas Timestamp to Python datetime object
        date = date.to_pydatetime()

    if convert_option == 'local':
        # Convert system local time to UTC
        local_dt = datetime.now(local_tz)
        local_dt -= timedelta(days=time_difference)
        utc_dt = local_tz.localize(local_dt).astimezone(utc_tz)

    elif convert_option == 'input_data':
        # Convert input data date from local timezone to UTC
        local_dt = datetime.strptime(date, date_format)
        local_dt = local_tz.localize(local_dt).astimezone(utc_tz)
        local_dt -= timedelta(days=time_difference)
        utc_dt = local_dt

    elif convert_option == 'both':
        # Convert both system local time and input data date from local timezone to UTC
        system_local_dt = datetime.now(local_tz)
        system_local_dt -= timedelta(days=time_difference)
        system_utc_dt = local_tz.localize(system_local_dt).astimezone(utc_tz)

        local_dt = datetime.strptime(date, date_format)
        local_dt = local_tz.localize(local_dt).astimezone(utc_tz)
        local_dt -= timedelta(days=time_difference)
        utc_dt = local_dt

        return system_utc_dt, utc_dt

    return utc_dt


def get_lounge_status(date, time_difference):
    current_date = datetime.now(pytz.UTC)
    date_diff = (current_date.date() - date.date()).days

    if date_diff <= time_difference:
        return 'active'
    else:
        return 'inactive'


def active_inactive_lounges(clients):
    time_difference= time_alert
    # date_format= '%Y-%m-%d %H:%M:%S'
    date_format= '%Y-%m-%d'
    convert_option=None
    df = load_data()
    active_lounges = {}
    inactive_lounges = {}
    act_loung_num = 0
    inact_loung_num = 0

    for client_id in clients:
        client_df = filter_data_by_cl(session["username"], df, client_id, clients)

        active_lounge_ids = set()
        inactive_lounge_ids = set()
        
        
        latest_record = get_latest_lounge_status(client_df)
        while latest_record is not None:
            lounge_id = latest_record[Lounge_ID_Col]
            received_date = latest_record[Date_col]
            utc_date = convert_to_utc(received_date, time_difference, date_format, convert_option)

            if isinstance(utc_date, tuple):
                # Both conversion options
                lounge_status = get_lounge_status(utc_date[0], time_difference)
                input_data_lounge_status = get_lounge_status(utc_date[1], time_difference)

                if lounge_status == 'active' or input_data_lounge_status == 'active':
                    active_lounge_ids.add(lounge_id)
                else:
                    inactive_lounge_ids.add(lounge_id)
            else:
                # Single conversion option
                lounge_status = get_lounge_status(utc_date, time_difference)

                if lounge_status == 'active':
                    active_lounge_ids.add(lounge_id)
                else:
                    inactive_lounge_ids.add(lounge_id)

            # Remove the latest record from the DataFrame
            client_df = client_df[client_df[Lounge_ID_Col] != lounge_id]
            latest_record = get_latest_lounge_status(client_df)

        if active_lounge_ids:
            act_loung_num += len(active_lounge_ids)
            active_lounges[client_id] = active_lounge_ids

        if inactive_lounge_ids:
            inact_loung_num += len(inactive_lounge_ids)
            inactive_lounges[client_id] = inactive_lounge_ids

    return active_lounges, inactive_lounges, act_loung_num, inact_loung_num




def active_clients_percent(clients,actdict, inactdict):
    active_cli=[]
    inact_cli=[]

    for i in clients:
        if i in  actdict:
            active_cli.append(i)
        else:
            inact_cli.append(i)
    return active_cli, inact_cli

def volume_rate(clients, amount=5):
    rates = {}
    df = load_data()
   
   
    volume_sum_x = 0
    volume_sum_2x = 0
    current_vol = 0
    prev_vol = 0
    for client_id in clients:
        client_df = df[df[CLName_Col] == client_id]  # Filter the DataFrame for a particular client
        
       
        latest_record = client_df.iloc[-1]  # Get the latest record for the client
        
        last_date = latest_record[Date_col]
        start_date_x = last_date - pd.DateOffset(days=amount)
        start_date_2x = last_date - pd.DateOffset(days=2 * amount)
        


        volume_sum_x = client_df[(client_df[Date_col] > start_date_x) & (client_df[Date_col] <= last_date)][Volume_ID_Col].sum()
        volume_sum_2x = client_df[(client_df[Date_col] > start_date_2x) & (client_df[Date_col] <= start_date_x)][Volume_ID_Col].sum()
        

        current_vol += volume_sum_x
        prev_vol += volume_sum_2x

        rates[client_id] = [volume_sum_x, volume_sum_2x]
    

            


    return rates, current_vol,  prev_vol


def filter_unique_val_dict(df, column):
    if column =='lounges':
        username = session["username"]
        cl_list = users[username]["AccessCL"]
        
        actives, inactives, _, _ = active_inactive_lounges(users[username]["AccessCL"])

        
        output = {}
        for i in cl_list:
            
            if i in actives and i in inactives:
                actives[i] = list(actives[i])
                actives[i].extend(list(inactives[i]))
                output[i] = list(set(actives[i]))
            elif i in actives:
                output[i] = actives[i]
            else:
                output[i] = inactives[i]
        
        output[''] = []
        for i in output:
            if i != '':
                output[''].extend(output[i])

        return output
    
    elif column == 'airport':
        unqiue_vals = df[Airport_Name_Col].unique()
        
        return unqiue_vals
    
    elif column == 'city':
        unqiue_vals = df[City_Name_Col].unique()
        
        return unqiue_vals
    
    elif column == 'country':
        unqiue_vals = df[Country_Name_Col].unique()
    
        return unqiue_vals




def lounge_crowdedness(access_clients, date='latest', selected_client='', alert=crowdedness_alert):


    df = load_data()

    df  = filter_data_by_cl(session["username"], df, selected_client, access_clients)

    rates = {'very_crowded':{}, 'crowded':{}, 'normal':{}, 'uncrowded':{}, 'open_to_accept':{}}
   
    very_crowded_df = df[df[Ratio_Col]>=0.5]
    crowded_df = df[(df[Ratio_Col] < 0.5) & (df[Ratio_Col] >= 0.4)]
    normal_df = df[(df[Ratio_Col] < 0.4) & (df[Ratio_Col] >= 0.2)]
    uncrowded_df = df[(df[Ratio_Col] < 0.2) & (df[Ratio_Col] >= 0.1)]
    open_to_accept_df = df[df[Ratio_Col] == 0]

    key_list = list(rates.keys())
    for i,dataframe in enumerate([very_crowded_df, crowded_df, normal_df, uncrowded_df,open_to_accept_df]):
        selected_key = key_list[i]
    
        clients = dataframe[CLName_Col].unique()
        for j in clients:

            if date =='latest':
                client_df = filter_data_by_cl(session["username"], dataframe, j, access_clients)
                latest_date = get_latest_date_time(client_df)


            if (datetime.now() - latest_date) > timedelta(days=alert):
                continue

            client_df = client_df[client_df[Date_col] == latest_date]

            filtered_df = client_df

            if len(filtered_df[Lounge_ID_Col].values) != 0:
                rates[selected_key][j] = []

                for i in range(len(filtered_df[Lounge_ID_Col].values)):
                    if not rates[selected_key][j]:
                        rates[selected_key][j].append([filtered_df[Lounge_ID_Col].values[i],filtered_df[Volume_ID_Col].values[i], filtered_df[Refuse_Col].values[i], filtered_df[Ratio_Col].values[i], latest_date])
                    elif filtered_df[Lounge_ID_Col].values[i] not in rates[selected_key][j][0]:
                        rates[selected_key][j].append([filtered_df[Lounge_ID_Col].values[i],filtered_df[Volume_ID_Col].values[i], filtered_df[Refuse_Col].values[i], filtered_df[Ratio_Col].values[i], latest_date])


    return rates

def get_notifications(inact_loung_num,inactive_clients,crowdedness):
    news=[]
    if inact_loung_num != 0:
        news.append('Inactive lounges😟')
    if inactive_clients:
        news.append('Inactive clients😟')
    
    if 'open_to_accept' in crowdedness:
        if len(crowdedness['open_to_accept']) > 0:
            news.append('Uncrowded lounges to offer😃')
    if 'very_crowded' in crowdedness:
            if len(crowdedness['very_crowded']) > 0:
                news.append('Chosen by many lounges🤔')
    return news

def get_latest_date_time(df):

    latest_rec = get_latest_lounge_status(df)
        
    latest_date= pd.to_datetime(latest_rec[Date_col])

    return latest_date

def record_sum_calculator(data,n, last_n=None):
    num_groups = len(data) // n
    
    result = []
    # Iterate over the groups and calculate the sum for each group
    if last_n:
        for i in range(num_groups-last_n,num_groups):
            start_index = i * n
            end_index = start_index + n
            group_sum = data[start_index:end_index]
            group_sum = sum(group_sum)
            result.append(group_sum)
        return result
    else:
        for i in range(num_groups):
            start_index = i * n
            end_index = start_index + n
            group_sum = data[start_index:end_index]
            group_sum = sum(group_sum)
            result.append(group_sum)
        return result


def record_lister(data, n):
    num_groups = len(data) // n
    
    result = []
    # Iterate over the groups and calculate the sum for each group
    for i in range(num_groups):
        start_index = i * n
        sliced_obj = data[start_index]
        
        result.append(sliced_obj)
    return result


def order_clients(df,clients, order, optional, plot_interval=1):
    if order =='alphabet':
        clients.sort()
        
    elif order =='pax_rate':
        
        username = session["username"]
        access_clients = users[username]["AccessCL"]

        cl_dict = {}
        for client in clients:
            client_df = filter_data_by_cl(session["username"], df, client, access_clients)

            vol_sum_list = record_sum_calculator(client_df.groupby(Date_col)[Volume_ID_Col].sum().to_list(), plot_interval*24)
            cl_dict[client] = sum(vol_sum_list)
        clients = sorted(cl_dict,key=cl_dict.get,reverse=True)
    
    elif order =='alert':
        username = session["username"]
        access_clients = users[username]["AccessCL"]
        

        no_date = stream_on_off(scale=optional[0],length=optional[1])
        #order based on the max of current_rec[px] - last_rec[px]
        #then do below to oreder (if applicable)
        clients_dict = {}
        for client in clients:
            client_df = filter_data_by_cl(session["username"], df, client, access_clients)
            vol_sum_list = record_sum_calculator(client_df.groupby(Date_col)[Volume_ID_Col].sum().to_list(), plot_interval*24, last_n=2)
            if vol_sum_list[-2] != 0:
                clients_dict[client] = (vol_sum_list[-1] - vol_sum_list[-2])/ vol_sum_list[-2]
            else:
                clients_dict[client] = 1000
        clients = sorted(clients_dict, key=lambda k: clients_dict[k], reverse=True)
        


        for client in clients:
            if client in no_date :
                clients.remove(client)
                clients.insert(0,client)


    return clients
