import streamlit as st
import datetime
import pandas as pd
#from openai import OpenAI
#from dotenv import load_dotenv
import os

def get_llm_response(prompt):
    """
        LLM model API ,where the LLM is defined to be a personal  help in weatherand to suggest weather 
        """
    #load_dotenv()
    open_api_key = st.secrets.get("openai_api_key") #os.getenv('openai_api_key')
    if not open_api_key:
        raise RuntimeError("openai_api_key is not configured")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1", api_key= open_api_key )
    # First API call with reasoning
    response = client.chat.completions.create(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
      messages=[
          {
            "role": "system",
            "content": "Send the past 7 days of weather data from the .csv file to an LLM to generate a natural-language summary, outfit suggestions, or local activity recommendations based on upcoming conditions."
          },
          {
            "role": "user",
            "content": (prompt)
          },
        ],
        max_tokens = 2000,
        extra_body={"reasoning": {"enabled": True}}
    )

    # Extract the assistant message with reasoning_details
    message = response.choices[0].message
    
    return message.content
    
st.title("Weather Tracker ")

video_file=open("project1fatimajawad.mp4","rb")
video_bytes=video_file.read()
st.video(video_bytes)


df = pd.read_csv('Weather_Dataset.csv')
option=st.sidebar.radio("select:",[
    "1.record a new weather observation",
    "2.view weather statistics",
    "3.search observations by data",
    "4.view all observations",
    "5.stretch goals "])

if option.startswith('1.'):
    st.header('record a new observation')
    event_time= st.time_input("write the time", value=None)
    event_date=st.date_input("write the date", value=None)
    st.write("write the date", event_time,event_date)
    wather_temperature=st.text_input('The temperature in degrees Celsius ')
    wather_conditions=st.text_input('Weather conditions (Sunny, Cloudy, Rainy, Snowy, etc.)')
    wather_Humidity=st.text_input('Humidity percentage ')
    wather_wind=st.text_input('Wind speed in km/h ')
    

    if st.button('save observation'):
        new_data={'Date/Time':event_time,
           'Temp_C':wather_temperature,
            'Weather':wather_conditions,
            'Rel Hum_%':wather_Humidity,
            'Wind Speed_km/h':wather_wind
            }
        df.loc[len(df)]=new_data
        df.to_csv('Weather_Dataset.csv',index=False)
        st.dataframe(df)

    
    
elif option.startswith('2.'):
    st.header('View weather statistics')
    df=pd.read_csv("Weather_Dataset.csv")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Temp", f"{df['Temp_C'].mean()}")
    col2.metric("Max Temp", f"{df['Temp_C'].max()}")
    col3.metric("Min Temp",f"{df['Temp_C'].min()}")

    avg_temp=df['Temp_C'].mean()
    min_temp=df['Temp_C'].min()
    max_temp=df['Temp_C'].max()

    most_commonly_recorded_weather_condition = df['Weather'].mode()[0]
    st.info(f'the most commonly recorded weather condition**{most_commonly_recorded_weather_condition}**')

elif option.startswith('3.'):
    st.header('Search observations by date')
    event_date= st.date_input("write the date to search for ", value=None)
    if event_date:
        the_filt = df['Date/Time'] == event_date
        i=df.loc[the_filt]
        if i.empty:
         st.warning("no data for that date")
        else: 
         i=i.iloc[0]
         user_temp=i['Temp_C']
         user_wind=i['Wind Speed_km/h']
    
         a, b = st.columns(2)
         a.metric("Temperature", f"{user_temp}")
         b.metric("Wind", f"{user_wind}")
   
   
elif option.startswith('4.'):  

    st.header('View all observations')
    df=pd.read_csv('Weather_Dataset.csv')
    st.dataframe(df)

elif option.startswith('5.'):
#######################################################################
 #1. The program can display temperature trends using text-based graphs
   #I use line chart
    from numpy.random import default_rng as rng

    df = pd.DataFrame(rng(0).standard_normal((20, 3)), columns=["Temp_C", "Date/Time", "Weather"])

    st.line_chart(
    df,
    x="Temp_C",
    y=["Date/Time", "Weather"],
    color=["#FF0000", "#0000FF"],
)
###########################################################################
# 2. The program allows filtering observations by month or season 
    def m(mon):
        if mon in[12,1,2]:
            return"winter"
        elif mon in[3,4,5]:
            return"spring"
        elif mon in[6,7,8]:
            return"summer"
        else:
            return"autumn"

    df = pd.read_csv('Weather_Dataset.csv')
    df['Date/Time']=pd.to_datetime(df['Date/Time'],format='mixed',errors='coerce')
    df['month']=df['Date/Time'].dt.month      
    filters=st.radio("filter by:",["mon","sea"])
    if filters=="mon":
        month=st.selectbox("month",list(range(1,13)))
        i=df[df['month']==month]
    else:
        df['season']=df['month'].apply(m)
        season=st.selectbox("season",["winter","spring","summer","autumn"])
        i=df[df['season']==season]
    st.dataframe(i)
        
############################################################################
#3. The program can predict tomorrow's weather based on historical patterns  
    st.header("predict")
    recent=df.tail(24)
    predict_temp=recent['Temp_C'].mean()
    predict_wind=recent['Wind Speed_km/h'].mean()
    predict_hum=recent['Rel Hum_%'].mean()
    a, b ,c= st.columns(3)
    a.metric("predict_temp",f"{predict_temp}")
    b.metric("predict_wind",f"{predict_wind}")
    c.metric("predict_hum",f"{predict_hum}")
  #############################################################################
 #4. The program can compare current year data with previous years  
    df['year']=df['Date/Time'].dt.year
    year=df['year'].unique()
    years=st.multiselect("years",year, default=list( year))
    filtered=df[df['year'].isin(years)]
    avg=filtered.groupby('year')['Temp_C'].mean()
    st.bar_chart(avg)
#############################################################################

#5. The program can track and display record-breaking temperatures or conditions

    st.header('record_breaking_temperatures')
    max_temp=df['Temp_C'].max()
    min_temp=df['Temp_C'].min()
    max_wind=df['Wind Speed_km/h'].max()
    a, b, c=st.columns(3)
    a.metric("Hott",f"{max_temp}C")
    b.metric("Cold",f"{min_temp}C")
    c.metric("Wind",f"{max_wind}km/h")
    test_temp=df['Temp_C'].iloc[-1]
    if test_temp==max_temp:
        st.success("record high")
    elif test_temp==min_temp:
        st.success("record low")
    else:
        st.write("no record")


    ################################################################################3
    
    st.header('API Weather')
    if st.button("API"): 
        import requests
        key = st.secrets.get("weather_api_key")
        city = "Manama"
        url = f"https://api.weatherapi.com/v1/current.json?key={key}&q={city}"
        data = requests.get(url).json()
        temp = data["current"]["temp_c"]
        humidity = data["current"]["humidity"]
        weather = data["current"]["condition"]["text"]
        st.write("Temperature:", temp)
        st.write("Humidity:", humidity)
        st.write("Weather:", weather)
        
        with open("weather_log.csv", "a") as file:
            file.write(f"{city},{temp},{humidity},{weather}\n")


#####################################################
    if st.button("LLM"):
      st.header('LLM Weather')
      
      # get 7 days data
      st.header('Weekly Summary (Last 7 Days)')
      daily = df.set_index('Date/Time').resample('D').mean(numeric_only=True)
      last_7_days = daily.tail(7)
      st.dataframe(last_7_days)
      st.line_chart(last_7_days['Temp_C'])
      recent_data = df.tail(7 * 24)
      s_text = recent_data[['Date/Time', 'Temp_C', 'Weather', 'Rel Hum_%', 'Wind Speed_km/h']].to_string(index=False)
      data_7days = last_7_days.to_csv(index=False)
    
    data_7days = df.tail(7)

    prompt_to_llm = f"""Analyze the following 7 days of weather data.Data:{data_7days.to_string(index=False)}Provide:1. A natural-language weather summary
    2. Outfit suggestions
    3. Local activity recommendations

    Upcoming conditions:
    """
    response = get_llm_response(prompt_to_llm)

    st.write(response)
    df = pd.read_csv('Weather_Dataset.csv')
    df['Date/Time'] = pd.to_datetime(df['Date/Time'], format='mixed', errors='coerce')
        
    
    
    
 
