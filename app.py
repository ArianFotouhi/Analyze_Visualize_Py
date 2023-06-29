from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from utils import load_data, filter_data_by_cl, dropdown_menu_filter, LoungeCounter, stream_on_off, active_inactive_lounges, active_clients_percent, volume_rate, filter_unique_val_dict, lounge_crowdedness, get_notifications, ParameterCounter, record_sum_calculator, record_lister, update_time_alert, update_plot_interval, crowdedness_alert, range_filter, order_clients
from config import Date_col, Lounge_ID_Col, CLName_Col, Volume_ID_Col,  users, Airport_Name_Col, City_Name_Col, Country_Name_Col
from authentication import Authentication
import numpy as np
import pandas as pd
from plotter import Plotter

authenticate = Authentication().authenticate


app = Flask(__name__)
app.secret_key = "!241$gc"


@app.route('/', methods=['GET'])
def index():
    if 'username' in session:
        return redirect('/home')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session["username"] = username
            return redirect('/home')
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")



@app.route('/home', methods=['GET','POST'])
def home():
    if 'username' not in session:
        return redirect('/login')

    client_name = request.args.get('clicked_image')
    print('CLIENT', client_name)
    if client_name:
        return redirect(url_for('client', client=client_name))
    
    df = load_data()

    username = session["username"]
    access_clients = users[username]["AccessCL"]

    accessed_df = filter_data_by_cl(session["username"], df, '', access_clients)

    data = accessed_df.to_dict(orient='records')
    crowdedness = lounge_crowdedness(date='latest', alert = crowdedness_alert)
    

    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
    volume_rates, vol_curr, vol_prev = volume_rate(access_clients, amount=7)

    cl_lounges_ = filter_unique_val_dict('lounges')
    airport_uq_list = filter_unique_val_dict('airport')
    city_uq_list = filter_unique_val_dict('city')
    country_uq_list = filter_unique_val_dict('country')

    notifications = get_notifications(inact_loung_num,inactive_clients,crowdedness)
    
    setting = {'time_alert':np.arange(1,30), 'plot_interval':np.arange(1,30)}

    stat_list = [act_loung_num, inact_loung_num,vol_curr, vol_prev, len(active_clients), len(inactive_clients),inactive_lounges, crowdedness]
    print("notifications", notifications)
    
    return render_template('index.html', data= data, clients= access_clients, stats= stat_list, cl_lounges_= cl_lounges_, 
                           airports = airport_uq_list, cities = city_uq_list, countries = country_uq_list, setting=setting)


  
    

@app.route('/update_plot', methods=['POST'])
def update_plot():

    username = session["username"]
    access_clients = users[username]["AccessCL"]
    df = load_data()



    selected_client = request.form['client']
    selected_lounge = request.form['lounge_name']
    selected_airport = request.form['airport_name']
    selected_city = request.form['city_name']
    selected_country = request.form['country_name']

    time_alert = int(request.form['time_alert']) 
    plot_interval = int(request.form['plt_interval'])
    selected_client_order = request.form['client_order']

    selected_start_date = request.form['start_date']
    selected_end_date = request.form['end_date']
    
    if selected_start_date != '' or selected_end_date!= '':
        df = range_filter(df, pd.to_datetime(selected_start_date),pd.to_datetime(selected_end_date),Date_col)
    

    update_time_alert(time_alert)
    update_plot_interval(plot_interval)


    

    #scales: sec, min, hour, day, mo, year
    no_data_dict = stream_on_off(scale='day', length=time_alert)

    #to avoid strem monitoring
    # no_data_dict = {}

    if selected_client or selected_lounge or selected_airport or selected_city or selected_country:
        active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
        active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
        volume_rates, vol_curr, vol_prev = volume_rate(access_clients, amount=7)

        # lounge_num  = LoungeCounter(str(client))

                
        airport_num = 0

        if selected_client:
            df = dropdown_menu_filter(df,CLName_Col ,selected_client)
            airport_list, airport_num = ParameterCounter(name = selected_client, base= CLName_Col, to_be_counted= Airport_Name_Col)

            # lounge_num = LoungeCounter(name = str(selected_client))
            

        if selected_lounge:
            df = dropdown_menu_filter(df,Lounge_ID_Col ,selected_lounge)
           
            # modality can be 'lg' or'cl'
            if selected_client == '':
                lounge_num, selected_client  = LoungeCounter(name = str(selected_lounge), modality='lg')
                airport_list, airport_num = ParameterCounter(name = selected_client, base= CLName_Col, to_be_counted= Airport_Name_Col)
        
        if selected_airport:

            df = dropdown_menu_filter(df,Airport_Name_Col, selected_airport)
        if selected_city:
            df = dropdown_menu_filter(df,City_Name_Col, selected_city)
        
        if selected_country:
            df = dropdown_menu_filter(df,Country_Name_Col, selected_country)


        if selected_client in active_lounges:
                actives = len(active_lounges[selected_client])
        else:
                actives = 0
        if selected_client in inactive_lounges:
                inactives = len(inactive_lounges[selected_client])
        else:
                inactives = 0

        date_list = record_lister(df[Date_col].dt.strftime('%Y-%m-%d %H:%M:%S').unique().tolist(), plot_interval*24)
        vol_sum_list = record_sum_calculator(df.groupby(Date_col)[Volume_ID_Col].sum().to_list(), plot_interval*24)

        trace = {
            'x': date_list,
            'y': vol_sum_list,
            'text': vol_sum_list,
            'hovertemplate': '%{text}',
            'type': 'scatter',
            'mode': 'lines',
            'name': 'Rates'
        }

        layout = {
            'title': {
                'text': f'{selected_client} {selected_lounge} {selected_airport} {selected_city} {selected_country}',
                'font': {
                    'family': 'Roboto',
                    'weight': 'bold'

                }
            },
            'xaxis': {
                'title': {
                    'text': 'Date',
                    'font': {
                        'family': 'Roboto',
                        'weight': 'bold'

                    }
                }
            },
            'yaxis': {
                'title': {
                    'text': 'Rate',
                    'font': {
                        'family': 'Roboto',
                        'weight': 'bold'

                    }
                }
            }
        }

        
        if str(selected_client) in list(no_data_dict.keys()):
            error_message = f"Last update {no_data_dict[str(selected_client)]}"
        else:
            error_message = None
        
        active_clients_num = int(len(active_clients))
        inactive_clients_num = int(len(inactive_clients))


        return jsonify({'traces': [trace], 'layouts': [layout], 'error_messages': error_message, 
                        'lounge_act_num':act_loung_num, 'lounge_inact_num':inact_loung_num,
                        'vol_curr':int(vol_curr),'vol_prev':int(vol_prev),
                        'active_clients_num':active_clients_num, 'inactive_clients_num':inactive_clients_num})

    else:
        traces = []
        layouts = []
        errors = []
       

        active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
        active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
        volume_rates, vol_curr, vol_prev = volume_rate(access_clients, amount=7)
        active_clients_num = int(len(active_clients))
        inactive_clients_num = int(len(inactive_clients))
        
        crowdedness = lounge_crowdedness(date='latest', alert = crowdedness_alert)
        notifications = get_notifications(inact_loung_num,inactive_clients,crowdedness)
        
        #alphabet
        #pax_rate
        clients = order_clients(df,access_clients,selected_client_order, optional=['day',time_alert],plot_interval=plot_interval)
        image_list=[]
        # print('clients', clients)
        for client in clients:
            client_df = filter_data_by_cl(session["username"], df, client, access_clients)

            # lounge_num  = LoungeCounter(str(client))

            if str(client) in active_lounges:
                actives = len(active_lounges[str(client)])
            else:
                actives = 0
            if client in inactive_lounges:
                inactives = len(inactive_lounges[str(client)])
            else:
                inactives = 0
            airport_list, airport_num = ParameterCounter(name = client, base= CLName_Col, to_be_counted= Airport_Name_Col)
            


            
            date_list = record_lister(client_df[Date_col].dt.strftime('%Y-%m-%d %H:%M:%S').unique().tolist(), plot_interval*24)
            vol_sum_list = record_sum_calculator(client_df.groupby(Date_col)[Volume_ID_Col].sum().to_list(), plot_interval*24)

            if str(client) in list(no_data_dict.keys()):
                no_data_error = f"Last update {no_data_dict[str(client)]}"
            else:
                no_data_error = None

            plt_title = f'{client}, Lounge {actives}/{actives + inactives}, AP No. {airport_num}'
            pltr = Plotter(date_list, vol_sum_list, plt_title , '', 'Passebgers Rate', no_data_error=no_data_error)
            image_info = pltr.save_plot()  

            image_list.append(image_info)

            trace = {
                'x': date_list,
                'y': vol_sum_list,
                'text': vol_sum_list,
                'hovertemplate': '%{text}',
                'type': 'scatter',
                'mode': 'lines',
                'name': f'Rates'
            }
            traces.append(trace)

            layout = {
                'title': {
                        'text': f'{client} {actives}/{actives + inactives}, AP No. {airport_num}',
                        'font': {
                            'size': 10  # Adjust the font size as desired
                        }
                    },
                # 'title': f'{client} {actives}/{ actives + inactives}, AP No. {airport_num}',
                'xaxis': {'title': 'Date'},
                'yaxis': {'title': 'Rate'}
            }
           
            layouts.append(layout)
           
            if str(client) in list(no_data_dict.keys()):
                error_message = f"Last update {no_data_dict[str(client)]}"
            else:
                error_message = None

            errors.append(error_message)

      
        


    
        return jsonify({'traces': traces, 'layouts': layouts , 'errors': errors, 'image':True,
                        'lounge_act_num':act_loung_num, 'lounge_inact_num':inact_loung_num,
                        'vol_curr':int(vol_curr),'vol_prev':int(vol_prev),
                        'active_clients_num':active_clients_num, 'inactive_clients_num':inactive_clients_num,
                        'cl':clients, 'image_info':image_list,'notifications':notifications})



@app.route('/intelligence_hub', methods=['GET'])
def intelligence_hub():

    if 'username' not in session:
        return redirect('/login')
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]

    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
    crowdedness = lounge_crowdedness(date='latest',alert = crowdedness_alert)
    stat_list = [inactive_clients,inactive_lounges,crowdedness]
    
    return render_template('intelligence_hub.html', clients= access_clients, stats= stat_list)



@app.route('/dormant', methods=['GET'])
def dormant():

    if 'username' not in session:
        return redirect('/login')
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)

    stat_list = [inactive_clients,inactive_lounges]
    
    return render_template('dormant.html', clients= access_clients, stats= stat_list)

@app.route('/client/<client>', methods=['GET'])
def client(client):
    
    if 'username' not in session:
        return redirect('/login')
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]

    print(client)

    return render_template('client.html', clients= access_clients)



@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
