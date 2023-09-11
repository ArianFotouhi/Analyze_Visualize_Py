Date_col ='Date_Time'
CLName_Col = 'CLIENT_NAME'
Lounge_ID_Col = 'Lounge_name'
Volume_ID_Col = 'PAX_Accept'
Airport_Name_Col = 'Airport_Code'
Country_Name_Col = 'Country'
City_Name_Col = 'City'
Refuse_Col='PAX_Reject'
Ratio_Col='REF2ALW'



#update them in index.html too
time_alert = 20
crowdedness_alert = 18
plot_interval = 1

plot_gradient_intensity = 0.5
num_samples_gradient = 200

users = {
    "IEG": {"password": "pass", "ClientID": 'IEG', 'AccessCL':['STR', 'AC','AV','EK1','LH','LX','UA1']},
    "STR": {"password": "pass", "ClientID": 'STR', 'AccessCL':['STR', 'AC','AV','EK1','LH']},
    "AC": {"password": "pass", "ClientID": 'AC', 'AccessCL':['AC']},
    "LH": {"password": "pass", "ClientID": 'LH', 'AccessCL':['LH','LX']},
}

# Date_col ='DATE_UTC'
# CLName_Col = 'CLIENT_NAME'
# Lounge_ID_Col = 'lounge_name'
# Volume_ID_Col = 'COUNT_PAX_ALLOWED'
# Refuse_Col='COUNT_PAX_REFUSED'
# Ratio_Col='REF2ALW'
# users = {
#     "admin": {"password": "admin", "ClientID": 'admin', 'AccessCL':['LH','LX', 'MAG']},

#     "user1": {"password": "pass", "ClientID": 1 , 'AccessCL':['MAG','LX']},
#     "user2": {"password": "pass", "ClientID": 2, 'AccessCL':['LH']},
#     "user3": {"password": "pass", "ClientID": 3, 'AccessCL':['LX']},
# }
