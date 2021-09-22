import os
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- FUNCTIONS ---


def exeTime(func):
    
    def countTime():
        print('---Buffering---')
        import time
        start = time.time()   
        func()
        time.sleep(1)
        end = time.time() - 1 #to avoid time is 0.0
        
        msg = f"Runtime of {func} is {end - start}"
        print(msg)
        file1 = open("RunTime.txt","a")
        file1.write(msg + "\n")
        file1.close() 
    return countTime


@exeTime
def test_exeTime():
    """test function"""
    L = [i for i in range(100)]
    return L[:-95]

@exeTime
def run_webapp_lab3():

    @st.cache(allow_output_mutation=True, 
              suppress_st_warning=True)
    def load_dataset(dataset):
        st.write(f'cache miss : {dataset} ')
        data = pd.read_csv(os.path.abspath(f"{dataset}.csv"))
        if dataset == 'hour_per_day':
            data.columns=['Monday','Tuesday','Wednesday','Thrusday','Friday','Saturday','Sunday']
        return data
        
    @st.cache(allow_output_mutation=True,
              suppress_st_warning=True)
    def df_head(d):
       st.write('cache miss : df_head')
       return d.head(10)
        
    @st.cache(allow_output_mutation=True,
              suppress_st_warning=True)
    def df_summary(d):
        st.write('cache miss : df_summary ')
        return d.describe()
        
    @st.cache(allow_output_mutation=True,
              suppress_st_warning=True)
    def rename_col(d):
        st.write('cache miss : rename_col ')
        return d.rename(columns={'Lat':'lat', 'Lon':'lon'})
    
    @st.cache(allow_output_mutation=True,
              suppress_st_warning=True)    
    def use_mask(selection, dataset):
        st.write('cache miss : use_mask ')
        mask_hour = dataset['hour'] == selection
        dataset = dataset[mask_hour]
        return dataset
    
    @st.cache(allow_output_mutation=True,
              suppress_st_warning=True)
    def df_base_process(df):
        df['Date/Time'] = df['Date/Time'].map(pd.to_datetime)
            
        def get_dom(dt): 
                return dt.day
        df['dom'] = df['Date/Time'].map(get_dom)
        def get_weekday(dt): 
            return dt.weekday() 

        df['weekday']= df['Date/Time'].map(get_weekday)

        def get_hour(dt): 
                return dt.hour
        df['hour']= df['Date/Time'].map(get_hour)
        return df
    
    
    
    # --- STREAMLITE PART ---
    
    # --- Select the dataset --- 
    dataset = st.selectbox(
        'Select the dataset to analyse',
       ('Uber april 2014','New York trips'),key=("dataset"))
    'You selected:', dataset
    
    if dataset == 'Uber april 2014':
        
        df_base = load_dataset('uber-raw-data-apr14')        
        df = df_base_process(df_base)
        print(df.head(10))

        st.title('Data analysis of Uber car - April 2014')
    
        st.text("Here are the first rows of the dataset :")
        df_head = df_head(df)
        st.write(df_head)
        
        st.subheader('Quick statistics summary')    
        df_summary = df_summary(df)
        st.write(df_summary)
        
        # --- Latitude, Longitude --- 
        
        map_data = rename_col(df)
        
        # --- See coordinates per hour / checkbox ---
        
        if st.checkbox('Show coordinates per hour'):
            # --- sidebar --- 
            option = st.sidebar.selectbox(
            'Select an hour',
            [i for i in range(24)],key=("aa"))
            'Map of the locations at the hour', option 
            
            # --- grp by hour --- 
            map_data_hour = use_mask(option, map_data)
            st.map(map_data_hour)
        else:
            st.map(map_data)
            
           # --- freq by hour by weekday --- 
        st.title('Frequencies per hour for each weekday')
        option = st.selectbox(
        'Select the hour',
        [i for i in range(24)],key=("ab"))
        'You selected:', option
        
        hour_per_day = load_dataset('hour_per_day')
        st.write(hour_per_day[option:option+1])
        st.line_chart(hour_per_day)
        
        
        # --- freq by hour by weekday ---
    
        # create figure and axis objects with subplots()
        fig,ax = plt.subplots()
        fig.set_size_inches(2, 2) 
        color = 'tab:red'
        ax.hist(df['Lon'], bins=10, alpha=0.5, label="Longitude", range=(-74.5,-73.5), color=color)
        ax.set_xlabel("Longitude",color=color,fontsize=3)
        ax.set_ylabel("frequency",fontsize=3)
        ax.tick_params(axis='x', labelcolor=color,labelsize=3)
        ax.tick_params(axis='y', labelsize=3)
        ax2 = ax.twiny()
        color = 'tab:blue'
        ax2.hist(df['Lat'], bins=10, alpha=0.5, label="Latitude", range=(40.5,41),color=color)
        ax2.set_xlabel("Latitude",color=color,fontsize=3)
        ax2.tick_params(axis='x', labelcolor=color,labelsize=3)
        
        # ---
            
        st.title("Histograms of Longitude and Latitude")
        st.write(fig)
        
    #display dataset 2
    elif dataset == 'New York trips':
    
        
        df2 = load_dataset('dataset2')
        hours = load_dataset('hours')
    
        st.title('Data analysis of New York car trips departing on 2015-01-15')
        
        df_head(df2)
        df_summary(df2)
        
        # --- sidebar --- 
        pickdrop = st.sidebar.selectbox(
        'Select what to observe on the map',
        ('pickup','dropoff'),key=("pickdrop"))
            
        # --- Latitude, Longitude --- 
        map_data2= df2.rename(columns={'pickup_latitude':'lat', 'pickup_longitude':'lon'})
        map_data3= df2.rename(columns={'dropoff_latitude':'lat', 'dropoff_longitude':'lon'})
        
            
        if pickdrop == 'pickup':
                st.title('Map of the pickup locations')
                st.map(map_data2)
        else:
            st.title('Map of the dropoff locations')
            st.map(map_data3)
            
        #histogram
        st.subheader('Number of pickups by hour')
        pickup_hist = np.histogram(
            df2['tpep_pickup_hour'], bins=24, range=(0,24))[0]
        st.bar_chart(pickup_hist)
        
        st.subheader('Price evolution within 24 hours')
        st.area_chart(hours['price/km'])

run_webapp_lab3()

# --- COMPONENTS ---

st.title(" Lab Part 2")

components.iframe("https://mraclassroom.files.wordpress.com/2016/03/images1.jpeg",
                  height=300)
components.iframe('https://i0.wp.com/ieltsliz.com/wp-content/uploads/2014/11/ielts-pie-chart-comparison.png?ssl=1',
                   height=500, scrolling=True)