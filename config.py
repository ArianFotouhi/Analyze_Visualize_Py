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
plot_interval = 10



users = {
    "admin": {"password": "admin", "ClientID": 'admin', 'AccessCL':['STAR_AMS', 'CL2','CL3','CL4','CL5','CL6','CL7']},
    "user1": {"password": "pass1", "ClientID": 'user1', 'AccessCL':['CL6','CL7']},
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