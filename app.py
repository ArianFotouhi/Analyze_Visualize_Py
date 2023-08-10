from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from utils import filter_data_by_cl, dropdown_menu_filter, LoungeCounter, stream_on_off, active_inactive_lounges, active_clients_percent, volume_rate, filter_unique_val, lounge_crowdedness, get_notifications, ParameterCounter, crowdedness_alert, range_filter, plot_arranger, update_time_alert, update_plot_interval, column_sum, plot_interval_handler, airport_loc, fetch_wikipedia_summary, logo_render, id2name, country_code_name
from config import Date_col, Lounge_ID_Col, CL_ID_Col, Volume_ID_Col,  users, Airport_Name_Col, City_Name_Col, Country_Name_Col
from authentication import Authentication
from database import load_data_2
import numpy as np
import pandas as pd
from plotter import Plotter
from conversion import convert_to_secure_name
from location import get_coordinates
from markupsafe import Markup
from execution_meter import measure_latency
import time


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
            return render_template("login.html", logo_path = logo_render('IEG', only_filename=True ),
                                    error="Invalid username or password")
    return render_template("login.html", 
                           logo_path = logo_render('IEG', only_filename=True ))

@app.route('/home', methods=['GET','POST'])
def home():
    if 'username' not in session:
        return redirect('/login')

    client_name = request.args.get('clicked_image')
    if client_name:
        return redirect(url_for('dashboard', client=client_name))
    
    # df = load_data()
    df = load_data_2()

    username = session["username"]
    access_clients = users[username]["AccessCL"]
    if len(access_clients)<2:
        single_client = True
    else:
        single_client = False

    accessed_df = filter_data_by_cl(session["username"], df, '', access_clients)

    data = accessed_df.to_dict(orient='records')
    # crowdedness = lounge_crowdedness(date='latest', alert = crowdedness_alert, access_clients=access_clients)
    

    # active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    # active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
    # _, vol_curr, vol_prev = volume_rate(access_clients, amount=7)

    cl_lounges_ = filter_unique_val(accessed_df, 'lounges')
    airport_uq_list = filter_unique_val(accessed_df, 'airport')
    city_uq_list = filter_unique_val(accessed_df, 'city')
    country_uq_list = filter_unique_val(accessed_df, 'country')

    # notifications = get_notifications(inact_loung_num,inactive_clients,crowdedness)
    
    setting = {'time_alert':np.arange(2,7), 'plot_interval':np.arange(2,7)}
    # stat_list = [act_loung_num, inact_loung_num,vol_curr, vol_prev, len(active_clients), len(inactive_clients),inactive_lounges, crowdedness]
    return render_template('index.html', data= data, clients= access_clients, cl_lounges_= cl_lounges_, 
                           airports = airport_uq_list, cities = city_uq_list, countries = country_uq_list, 
                           setting=setting, logo_path = logo_render(users[username]["ClientID"], only_filename=True ),
                           background_logo = logo_render(users[username]["ClientID"]+'_2', only_filename=True ),single_client=single_client)

@app.route('/update_plot', methods=['POST'])
def update_plot():

    username = session["username"]
    access_clients = users[username]["AccessCL"]


    try:
        selected_client = request.form['client']
    except:
        selected_client = ''
        
    selected_lounge = request.form['lounge_name']
    selected_airport = request.form['airport_name']
    selected_city = request.form['city_name']
    selected_country = request.form['country_name']

    time_alert = int(request.form['time_alert']) 
    plot_interval = int(request.form['plt_interval'])
    
    plot_gradient_intensity = float(request.form['plot_gradient_intensity'])
    plt_thickness = float(request.form['plt_thickness'])
    
    try:
        selected_client_order = request.form['client_order']
    except:
        selected_client_order = ''
        

    selected_start_date = request.form['start_date']
    selected_end_date = request.form['end_date']
    
    # print('selected_date', selected_start_date)
    update_time_alert(time_alert)
    update_plot_interval(plot_interval)
   
    # df = load_data()

    df = load_data_2()
    # df2 = load_data_2(
    #                 from_time= selected_start_date,
    #                 to_time= selected_end_date
    #                   )
    # print('df2',df2)

    if selected_start_date != '' or selected_end_date!= '':
        df = range_filter(df, pd.to_datetime(selected_start_date),pd.to_datetime(selected_end_date),Date_col)
    




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
            df = dropdown_menu_filter(df,CL_ID_Col ,selected_client)
            airport_list, airport_num = ParameterCounter(name = selected_client, base= CL_ID_Col, to_be_counted= Airport_Name_Col)

            # lounge_num = LoungeCounter(name = str(selected_client))
            

        if selected_lounge:
            df = dropdown_menu_filter(df,Lounge_ID_Col ,selected_lounge)
           
            # modality can be 'lg' or'cl'
            if selected_client == '':
                lounge_num, selected_client  = LoungeCounter(name = selected_lounge, modality='lg')
                airport_list, airport_num = ParameterCounter(name = selected_client, base= CL_ID_Col, to_be_counted= Airport_Name_Col)
        
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


    

     
        date_list, vol_sum_list = plot_interval_handler(df, plot_interval*1440)



        trace = {
            'x': date_list,
            'y': vol_sum_list,
            'text': vol_sum_list,
            'hovertemplate': '%{text}',
            'type': 'scatter',
            'mode': 'lines',
            'name': 'Passengers'
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

        
        if selected_client in list(no_data_dict.keys()):
            error_message = f"Last update {no_data_dict[selected_client]}"
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
        
        crowdedness = lounge_crowdedness(date='latest', alert = crowdedness_alert, access_clients=access_clients)
        notifications = get_notifications(inact_loung_num, inactive_clients, crowdedness)
        


        if len(access_clients) > 1:
            aggregate_plot= True
        else:
            aggregate_plot= False

        cl_info = {}       
        #0.6 seconds
        temp_cl_list = access_clients[:]
        temp_cl_list.insert(0, '')

        for client in temp_cl_list:
            client_df = filter_data_by_cl(session["username"], df, client, access_clients)
            date_list, vol_sum_list = plot_interval_handler(client_df, plot_interval*1440)
            
            if len(vol_sum_list)>1:
                if vol_sum_list[-2] != 0:
                    cl_growth_rate = 100*(vol_sum_list[-1] - vol_sum_list[-2]) / (vol_sum_list[-2])
                else:
                    cl_growth_rate = 100
            else:
                cl_growth_rate = 100

            cl_info[client] = [date_list, vol_sum_list, cl_growth_rate]
        if selected_client_order == 'alert':
            cl_data = cl_info
        else:
            cl_data = ''



        #0.08 seconds
        clients = plot_arranger(df,access_clients,selected_client_order, optional=['day',time_alert],plot_interval=plot_interval, extra_data=cl_data)
        image_list=[]
        
        temp_cl_list = clients[:]
        temp_cl_list.insert(0, '')

        #half latency of all route latency 1.4 seconds
        for client in temp_cl_list:

            client_df = filter_data_by_cl(session["username"], df, client, access_clients)
            date_list = cl_info[client][0]
            vol_sum_list = cl_info[client][1]
            growth_rate = cl_info[client][2]
            # lounge_num  = LoungeCounter(str(client))

            if client == '':
                plt_title = f'Aggregation Plot'
                no_data_error = None
                actives= 1
                inactives = 1
                airport_num = 1
                background_color = '#2D7FFA'

            else:

                if client in active_lounges:
                    actives = len(active_lounges[client])
                else:
                    actives = 0
                if client in inactive_lounges:
                    inactives = len(inactive_lounges[client])
                else:
                    inactives = 0
                airport_list, airport_num = ParameterCounter(name = client, base= CL_ID_Col, to_be_counted= Airport_Name_Col)
 
                if client in list(no_data_dict.keys()):
                    no_data_error = f"Last update {no_data_dict[client]}"
                else:
                    no_data_error = None
                
                plt_title = f'{id2name(id=client)}, Lounge {actives}/{actives + inactives}, AP No. {airport_num}'
                background_color = None
            

            pltr = Plotter(date_list, vol_sum_list, plt_title , plt_thickness= plt_thickness ,xlabel='',  ylabel='Passengers',growth_rate=growth_rate, no_data_error= no_data_error, 
                           client= client, plot_gradient_intensity=plot_gradient_intensity, background_color=background_color)
            # ss1 = time.time()
            image_info = pltr.save_plot()  
            # ee1 = time.time()
            # print(client,'latency in first:', ee1 - ss1)
            # ss2 = time.time()
            image_list.append(image_info)
            # ee2 = time.time()
            # print(client,'latency in second:', ee2 - ss2)


        
        
        return jsonify({'image':True,
                        'lounge_act_num':act_loung_num, 'lounge_inact_num':inact_loung_num,
                        'vol_curr':int(vol_curr),'vol_prev':int(vol_prev),
                        'active_clients_num':active_clients_num, 'inactive_clients_num':inactive_clients_num,
                        'cl':temp_cl_list, 'image_info':image_list,'notifications':notifications, 'aggregate_plot':aggregate_plot})

@app.route('/intelligence_hub', methods=['GET'])
def intelligence_hub():

    if 'username' not in session:
        return redirect('/login')
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]

    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
    crowdedness = lounge_crowdedness(date='latest',alert = crowdedness_alert, access_clients=access_clients)
    stat_list = [inactive_clients, inactive_lounges, crowdedness]
    
    return render_template('intelligence_hub.html', clients= access_clients, 
                           stats= stat_list, user=username, logo_path = logo_render(users[username]["ClientID"], only_filename=True ))

@app.route('/dormant', methods=['GET'])
def dormant():

    if 'username' not in session:
        return redirect('/login')
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges(access_clients)
    active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
    inactive_cl_list = []

    for i in inactive_clients:
        inactive_cl_list.append([i ,logo_render(i, only_filename=True )])
        
    stat_list = [inactive_cl_list,inactive_lounges]
    
    return render_template('dormant.html', clients= access_clients, stats= stat_list,
                            logo_path = logo_render(users[username]["ClientID"], only_filename=True ))

@app.route('/dashboard/<client>/lounges', methods=['GET'])
def dashboard_lounge(client):   
    if 'username' not in session:
        return redirect('/login')
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    
    if str(client) not in access_clients:
        try:
            if int(client) not in access_clients:
                return redirect('/home')
        except:
            return redirect('/home')
   
    try:
        client = int(client)
    except:
        client = str(client)
    client_name = id2name(id = client)

    # df = load_data()
    df = load_data_2()
    
    filtered_df = dropdown_menu_filter(df,CL_ID_Col ,client)

    cl_lounges_ = filter_unique_val(filtered_df, 'lounges')
    airport_uq_list = filter_unique_val(filtered_df,'airport') #return an array
    city_uq_list = filter_unique_val(filtered_df, 'city') #return an array
    country_uq_list = filter_unique_val(filtered_df, 'country')

    cities_dict = get_coordinates(city_uq_list) #[lat, lon, city, country]
    cities_dict = Markup(cities_dict)


    setting = {'time_alert':np.arange(2,7), 'plot_interval':np.arange(2,7)}

    file_name = convert_to_secure_name(client)
    
     
    return render_template('lounge_monitor.html', client= client_name,cl_lounges_= cl_lounges_, 
                           airports = airport_uq_list, cities = city_uq_list, countries = country_uq_list,
                            setting=setting, logo_file_name=file_name, logo_path = logo_render(users[username]["ClientID"], only_filename=True ))  

@app.route('/dashboard/<client>/airports', methods=['GET'])
def dashboard_airport(client):   
    if 'username' not in session:
        return redirect('/login')
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    
    if str(client) not in access_clients:
        try:
            if int(client) not in access_clients:
                return redirect('/home')
        except:
            return redirect('/home')
    
    try:
        client = int(client)
    except:
        client = str(client)
    client_name = id2name(id = client)
    # df = load_data()
    df = load_data_2()
    filtered_df = dropdown_menu_filter(df,CL_ID_Col ,client)

    airport_uq_list = filter_unique_val(filtered_df,'airport') #return an array

    # dict_airport_info = {}
    # for i in airport_uq_list:
    #     temp_df = filtered_df[filtered_df[Airport_Name_Col]==i]
        

    file_name = convert_to_secure_name(client)
    airport_locs = airport_loc(client, airport_uq_list)
    airport_locs = Markup(airport_locs)
     
    return render_template('airport_monitor.html', client= client_name, 
                           airports = list(airport_uq_list),  
                           logo_file_name=file_name, airport_locs=airport_locs,
                            logo_path = logo_render(client, only_filename=True ))  

@app.route('/update_airports', methods=['POST'])
def update_airports():
    airport_info = None
    selected_airport = request.form['selected_airport']
    
    if selected_airport:
        airport_info  = fetch_wikipedia_summary(selected_airport+' Airport')
    
    return jsonify({'airport_info': airport_info})

@app.route('/dashboard/<client>', methods=['GET'])
def dashboard(client):
    if 'username' not in session:
        return redirect('/login')
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]
   
    try:
        client = int(client)
    except:
        client = str(client)

    client_name = id2name(id = client)

    if str(client) not in access_clients:
        try:
            if int(client) not in access_clients:
                return redirect('/home')
        except:
            return redirect('/home')
    
    # df = load_data()
    df = load_data_2()
    filtered_df = dropdown_menu_filter(df,CL_ID_Col ,client)

    cl_lounges_ = filter_unique_val(filtered_df, 'lounges')
    # airport_uq_list = filter_unique_val(filtered_df,'airport') #return an array
    airport_uq_dict = ParameterCounter(name=None,base=Airport_Name_Col, to_be_counted = Lounge_ID_Col, df=filtered_df)
    city_uq_list = filter_unique_val(filtered_df, 'city') #return an array
    country_uq_list = filter_unique_val(filtered_df, 'country')

    cities_dict = get_coordinates(city_uq_list) #[lat, lon, city, country]
    cities_dict = Markup(cities_dict)

    setting = {'time_alert':np.arange(2,7), 'plot_interval':np.arange(2,7)}

    file_name = convert_to_secure_name(client)

    crowdedness = lounge_crowdedness(date='latest', alert = crowdedness_alert, access_clients=access_clients)
    

    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges([client])
    # active_clients, inactive_clients = active_clients_percent(access_clients, active_lounges, inactive_lounges)
    # volume_rates, vol_curr, vol_prev = volume_rate(access_clients, amount=7)
    if client in inactive_lounges:
        inact_lg_list = list(inactive_lounges[client])
        
    else:
        inact_lg_list = None

    stat_list = [inact_lg_list, crowdedness]
    return render_template('dashboard.html', client= client,client_name= client_name,cl_lounges_= cl_lounges_, 
                           airports = airport_uq_dict, cities = city_uq_list, countries = country_uq_list,
                             stats=stat_list, setting=setting, logo_file_name = file_name, cities_dict=cities_dict,
                             logo_path = logo_render(users[username]["ClientID"], only_filename=True ))

@app.route('/update_dashboard', methods=['POST'])
def update_dashboard():
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    # df = load_data()
    df = load_data_2()
    
    client = request.form['client']
    try:
        client = int(client)
    except:
        client = str(client)
        
    page_user = request.form['page_user']

    selected_lounge = request.form['lounge_name']
    selected_airport = request.form['airport_name']
    selected_city = request.form['city_name']
    selected_country = request.form['country_name']
    selected_client_order = request.form['client_order']

    time_alert = int(request.form['time_alert']) 
    plot_interval = int(request.form['plt_interval'])
    
    plot_gradient_intensity = float(request.form['plot_gradient_intensity'])
    plt_thickness = float(request.form['plt_thickness'])
    # selected_client_order = request.form['client_order']

    selected_start_date = request.form['start_date']
    selected_end_date = request.form['end_date']
    
    if selected_lounge:
        df = df[df[Lounge_ID_Col] == selected_lounge]
    if selected_airport:
        df = df[df[Airport_Name_Col] == selected_airport]

    if selected_city:
        df = df[df[City_Name_Col] == selected_city]

    if selected_country:
        df = df[df[Country_Name_Col] == selected_country]

    update_time_alert(time_alert)
    update_plot_interval(plot_interval)

    # df2 = load_data_2(
    #                 from_time= selected_start_date,
    #                 to_time= selected_end_date
    #                   )
    # print('df2',df2)
    if selected_start_date != '' or selected_end_date!= '':
        df = range_filter(df, pd.to_datetime(selected_start_date),pd.to_datetime(selected_end_date),Date_col)
    


    



    filtered_df = dropdown_menu_filter(df, CL_ID_Col, client)
    
    lg_list = filter_unique_val(filtered_df, 'lounges')



    if selected_start_date != '' or selected_end_date!= '':
        df = range_filter(df, pd.to_datetime(selected_start_date), pd.to_datetime(selected_end_date),Date_col)




    if page_user == 'dashboard':
        lg_list = list(lg_list)
        lg_list = lg_list[:3]



    #scales: sec, min, hour, day, mo, year
    no_data_dict = stream_on_off(scale='day', length=time_alert, level='lg', component_list = lg_list)
    #alphabet
    #pax_rate
    # clients = order_clients(df,access_clients,selected_client_order, optional=['day',time_alert],plot_interval=plot_interval)
    image_list=[]
    
    df = filter_data_by_cl(session["username"], df, client, access_clients)
    lg_data = [lg_list, no_data_dict]


    lg_info = {}       
    for lg in lg_list:
        
        filtered_df = dropdown_menu_filter(df,Lounge_ID_Col ,lg)

        date_list, vol_sum_list = plot_interval_handler(filtered_df, plot_interval*1440)
        if vol_sum_list:
            if len(vol_sum_list)>1:
                if vol_sum_list[-2] != 0:
                    lg_growth_rate = 100*(vol_sum_list[-1] - vol_sum_list[-2]) / (vol_sum_list[-2])
                else:
                    lg_growth_rate = 100
            else:
                lg_growth_rate = 100
            
            data_available = True
            lg_info[lg] = [date_list, vol_sum_list, lg_growth_rate, data_available]
        
        else:
            data_available = False
            lg_info[lg] = [None, None, None, data_available]




        
    lg_list = plot_arranger(df,data_package=lg_data, order = selected_client_order, 
                            level='lg', optional=['day',time_alert], 
                            plot_interval=plot_interval, extra_data=lg_info)



    for lounge in lg_list:
        date_list = lg_info[lounge][0]
        vol_sum_list = lg_info[lounge][1]
        lg_growth_rate = lg_info[lounge][2]    
        
        if lounge in list(no_data_dict.keys()):
            no_data_error = f"Last update {no_data_dict[lounge]}"
        else:
            no_data_error = None
        
        if not lg_info[lounge][3]:
            continue


        plt_title = f'Lounge {lounge}'
        pltr = Plotter(date_list, vol_sum_list, plt_title , plt_thickness= plt_thickness ,xlabel='',  ylabel='Passengers', no_data_error= no_data_error, 
                           client= client, plot_gradient_intensity=plot_gradient_intensity, growth_rate=lg_growth_rate)

        image_info = pltr.save_plot()  
        image_list.append(image_info)
       

    active_lounges, inactive_lounges, act_loung_num, inact_loung_num = active_inactive_lounges([client])
    
    return jsonify({'image_info': image_list, 'lounge_list': list(lg_list), 
                    'act_loung_num':act_loung_num, 'inact_loung_num':inact_loung_num})

@app.route('/map', methods=['GET'])
def map():

    if 'username' not in session:
        return redirect('/login')
    
    username = session["username"]
    return render_template('map.html', logo_path = logo_render(users[username]["ClientID"], only_filename=True ))

@app.route('/update_map', methods=['POST'])
def update_map():
    
    username = session["username"]
    access_clients = users[username]["AccessCL"]
    df = load_data_2()
    
    selected_start_date = request.form['start_date']
    
    # df2 = load_data_2(
    #                 from_time = selected_start_date
    #                   )
    # print('df2',df2)
    if selected_start_date != '':
        df = range_filter(df, pd.to_datetime(selected_start_date), None, Date_col)


    username = session["username"]
    access_clients = users[username]["AccessCL"]

    df = filter_data_by_cl(session["username"], df, access_clients, access_clients)

    #number of passengers not the received data records
    country_rates = column_sum(df, Country_Name_Col, Volume_ID_Col)
    for i in country_rates:
        
        key = i['name']        
        new_key = country_code_name(key)
        i['name'] = new_key

    return jsonify({'country_uq_dict': country_rates})

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/user_guide', methods=['GET'])
def user_guide():

    if 'username' not in session:
        return redirect('/login')
    username = session["username"]
    return render_template('user_guide.html', logo_path = logo_render(users[username]["ClientID"], only_filename=True ))

@app.route('/user_guide/<path:filename>')
def user_guide_page(filename):
    return render_template(f'user_guide/{filename}.html')


# @app.route('/<path:path>')
# def redirect_to_home(path):
    # return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
