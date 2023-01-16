import numpy as np
import pandas as pd
import datetime
from datetime import timedelta

# Execute from terminal type the command below
# python calculator.py

def read_file(path):
    data=pd.read_csv(path, names=['Number', 'Start', 'End'])
    data['Start']=pd.to_datetime(data['Start'])
    data['End']=pd.to_datetime(data['End'])
    data['Duration'] = data['End']-data['Start']
    data['Duration in seconds']=data['Duration'].apply(lambda x: x.seconds)
    return data
    
def find_frequent_number(data):
    fav_number=int(data['Number'].mode())
    fav_number_rows=data[data['Number']==fav_number]
    for i in fav_number_rows.index:
        data.loc[i, 'Cost']=0
    return data

def define_tarifs(data):
    data['Bonus_rate'] = np.where(data['Duration in seconds']>300, True, False)
    data['Discounted rate to Main rate'] = np.where(( data['Start'].dt.hour < 8) & (data['End'].dt.hour >= 8), True, False) #bound cases2
    data['Main rate to Discounted rate'] = np.where(( data['Start'].dt.hour < 16) & (data['End'].dt.hour >= 16), True, False) #bound cases1
    
    data['Main rate'] = np.where((data['Start'].dt.hour >= 8) & (data['Start'].dt.hour < 16) & (data['End'].dt.hour < 16) & (data['Discounted rate to Main rate']==False) & (data['Main rate to Discounted rate']==False), True, False)
    data['Discounted rate'] = np.where((data['Main rate']==False) & (data['Discounted rate to Main rate']==False) & (data['Main rate to Discounted rate']==False), True, False)
    return data

def calculate_cost_discounted_to_main_rate(data):
    t1=timedelta(hours=8)
    t1.total_seconds()
    discounted_to_main=data[data['Discounted rate to Main rate']]

    time_start=discounted_to_main['Start'].dt.time
    t1.total_seconds()
    for i in discounted_to_main.index:
        
        time=str(time_start[i])
        date_time = datetime.datetime.strptime(time, "%H:%M:%S")
        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
        a=int(t1.seconds-a_timedelta.total_seconds()) #duration of call in seconds before 8 
        b=discounted_to_main['Duration in seconds'][i]-a #duration of call in seconds after 8
        if int(discounted_to_main['Duration in seconds'][i])<300:
            cost=(np.ceil(a/60))*0.5+(np.ceil((b-(((np.ceil(a/60))*60)-a))/60))*1
            #print(a, b, cost)
        else:
        # for calls more 5 min
            if a>=300:
                cost=np.ceil(((discounted_to_main['Duration in seconds'][i])-300)/60)*0.2+5*0.5
            else:
                # if 300 sec=5mins is between rates
                cost=(np.ceil(a/60))*0.5+(np.ceil((300-a-(((np.ceil(a/60))*60)-a))/60))*1+np.ceil(((discounted_to_main['Duration in seconds'][i])-300)/60)*0.2
        data.loc[i, 'Cost']=cost 
    
    return data


def calculate_cost_main_to_discounted_rate(data):

    t2=timedelta(hours=16)
    t2.total_seconds()
    main_to_discounted=data[data['Main rate to Discounted rate']]
    time_start=main_to_discounted['Start'].dt.time
    t2.total_seconds()
    for i in main_to_discounted.index:
        
        time=str(time_start[i])
        date_time = datetime.datetime.strptime(time, "%H:%M:%S")
        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
        a=int(t2.seconds-a_timedelta.total_seconds()) #duration of call in seconds before 8 
        b=main_to_discounted['Duration in seconds'][i]-a #duration of call in seconds after 8
        if int(main_to_discounted['Duration in seconds'][i])<300:
            #print(a, b, cost)
            cost=(np.ceil(a/60))*1+(np.ceil((b-(((np.ceil(a/60))*60)-a))/60))*0.5
        else:
        # for calls more 5 min
            if a>=300:
                cost=np.ceil(((main_to_discounted['Duration in seconds'][i])-300)/60)*0.2+5*1
            else:
                # if 300 sec=5mins is between rates
                cost=(np.ceil(a/60))*1+(np.ceil((300-a-(((np.ceil(a/60))*60)-a))/60))*0.5+np.ceil(((main_to_discounted['Duration in seconds'][i])-300)/60)*0.2
        data.loc[i, 'Cost']=cost
    return data

def calculate_cost_main_rate(data):
    main_rate=data[data['Main rate']]
    for i in main_rate.index:
        if main_rate['Bonus_rate'][i]==True:
            cost=np.ceil(((main_rate['Duration in seconds'][i])-300)/60)*0.2+5*1           
        else:
            cost=np.ceil(main_rate['Duration in seconds'][i]/60)*1
        data.loc[i, 'Cost']=cost
    #print(data['Cost'])
    return data

def calculate_cost_discounted_rate(data):
    discounted_rate=data[data['Discounted rate']]
    for i in discounted_rate.index:
        if discounted_rate['Bonus_rate'][i]==True:
            cost=np.ceil(((discounted_rate['Duration in seconds'][i])-300)/60)*0.2+5*0.5
        else:
            cost=np.ceil(discounted_rate['Duration in seconds'][i]/60)*0.5
        data.loc[i, 'Cost']=cost
    #print(data['Cost'])
    return data


def sum_costs(data):
    sum=data['Cost'].sum()
    print('Sum of cost: ', sum)
    return sum


if __name__ == "__main__":
    
    path='./homework_v3/generated_sample_2.csv'
    data_original=read_file(path)
    data=define_tarifs(data_original)
    data=calculate_cost_discounted_to_main_rate(data_original)
    data=calculate_cost_main_to_discounted_rate(data_original)
    data=calculate_cost_main_rate(data_original)
    data=calculate_cost_discounted_rate(data_original)
    data=find_frequent_number(data_original)
    cost=sum_costs(data)