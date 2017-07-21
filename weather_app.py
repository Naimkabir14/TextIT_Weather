import requests, datetime
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
@app.route('/', methods = ['POST'])
def sms_reply():
    #Deals with proper formatting of states and cities in accordance to the WUnderground API
        city_state = request.values.get('Body', None)
        a = city_state.split(',')
        b = a[0].split(" ")
        state = a[1]
        city = "_".join(b)

        times , hr = get_coords(city, state)
        stmnt, wthr = get_forecast(city, state, current_time=times, hour=hr)

        resp = MessagingResponse()
        resp.message(stmnt+"\n"+wthr+"...")

        return str(resp)

def get_coords(city, state):
    # Finds specific latitude and longitude for each city and state from the Wunderground API using geolookup feature
    lat_n_long = requests.get("http://api.wunderground.com/api/53292b83ef5069b5/geolookup/q/%s/%s.json"%(state, city))
    location_resp = lat_n_long.json()
    lon = location_resp['location']['lon']
    lat = location_resp['location']['lat']

    # Finds specific time for each specific location based on the latitude and longitude information using geonames API
    timer = requests.get('http://api.geonames.org/timezoneJSON?lat=%s&lng=%s&username=naimk101'%(lat,lon))

    location_time = timer.json()
    extracted_time = location_time['time']
    split_time = str(extracted_time).split(" ")

    # Adjusts Time format
    current_time = datetime.datetime.strptime(split_time[1],"%H:%M").strftime('%I:%M %p').lstrip('0')
    hour = datetime.datetime.strptime(split_time[1],"%H:%M").hour

    return current_time, hour

def get_forecast(city, state, current_time, hour):
    r = requests.get("http://api.wunderground.com/api/53292b83ef5069b5/hourly/q/%s/%s.json"%(state, city))
    res = r.json()

    c = requests.get("http://api.wunderground.com/api/53292b83ef5069b5/conditions/q/%s/%s.json"%(state, city))
    current = c.json()

    deg=(u'\u00b0'+ "F")# Unicode for degree symbol
    place = str(current['current_observation']['display_location']['full'])
    weather_string = str(int(current['current_observation']['temp_f']))+deg

    time_of_day = "Good %s %s,\nIt is currently %s\nYour current temperature is %s\nYour current condition is %s\n"
    hourly_forecast = "Here is your hourly forecast:"

    weather = ""

    if 12 <= hour <= 18:
        clk_time = time_of_day % ('Afternoon', place, current_time, weather_string, str(current['current_observation']['weather']))
        for hours in res['hourly_forecast']:
            weather += "\nDay: "+hours['FCTTIME']['weekday_name']+"\tCondition: {cndt} ".format(cndt=hours['condition'])+"\n"\
                "Time: "+hours['FCTTIME']['civil']+" Temp: "+hours['temp']['english']+deg+" Feels: "+hours['feelslike']['english']+deg+"\n"
        for i in range(0, len(weather)):
            return clk_time + hourly_forecast, weather[i:i+1300] #Limits characters to deal with Twilio character restrictions

    elif 18 <= hour <= 24:
        clk_time = time_of_day % ('Evening', place, current_time, weather_string, str(current['current_observation']['weather']))
        for hours in res['hourly_forecast']:
            weather += "\nDay: "+hours['FCTTIME']['weekday_name']+"\tCondition: {cndt} ".format(cndt=hours['condition'])+"\n"\
                "Time: "+hours['FCTTIME']['civil']+" Temp: "+hours['temp']['english']+deg+" Feels: "+hours['feelslike']['english']+deg+"\n"
        for i in range(0, len(weather)):
            return clk_time + hourly_forecast, weather[i:i+1300]

    else:
        clk_time = time_of_day % ('Morning', place, current_time, weather_string, str(current['current_observation']['weather']))
        for hours in res['hourly_forecast']:
            weather += "\nDay: "+hours['FCTTIME']['weekday_name']+"\tCondition: {cndt} ".format(cndt=hours['condition'])+"\n"\
                "Time: "+hours['FCTTIME']['civil']+" Temp: "+hours['temp']['english']+deg+" Feels: "+hours['feelslike']['english']+deg+"\n"
        for i in range(0, len(weather)):
            return clk_time + hourly_forecast, weather[i:i+1300]

if __name__ == '__main__':
    app.run()



