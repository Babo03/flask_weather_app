from flask import Flask, render_template, request
import requests
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)

API_KEY = '212c345134a7a7e7df60148434a4974b'
AIR_QUALITY_API_KEY = '212c345134a7a7e7df60148434a4974b'

def get_weather_data(city):
    # 获取天气数据
    weather_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    # 获取空气质量数据
    lat = weather_data['city']['coord']['lat']
    lon = weather_data['city']['coord']['lon']
    air_quality_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={AIR_QUALITY_API_KEY}'
    air_quality_response = requests.get(air_quality_url)
    air_quality_data = air_quality_response.json()

    return weather_data, air_quality_data

def generate_temperature_chart(days):
    fig, ax = plt.subplots(figsize=(10, 6))
    dates = list(days.keys())
    max_temps = [days[date]['temp_max'] for date in dates]
    min_temps = [days[date]['temp_min'] for date in dates]
    ax.bar(dates, max_temps, width=0.4, label='Max Temp (°C)', align='center', color='red', alpha=0.6)
    ax.bar(dates, min_temps, width=0.4, label='Min Temp (°C)', align='center', color='blue', alpha=0.6)
    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Temperature Forecast')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart = io.BytesIO()
    plt.savefig(chart, format='png')
    chart.seek(0)
    return chart

def generate_humidity_chart(days):
    fig, ax = plt.subplots(figsize=(10, 6))
    dates = list(days.keys())
    humidities = [days[date]['humidity'] for date in dates]
    ax.plot(dates, humidities, marker='o', color='blue', linestyle='-', linewidth=2)
    ax.set_xlabel('Date')
    ax.set_ylabel('Humidity (%)')
    ax.set_title('Humidity Trend')
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart = io.BytesIO()
    plt.savefig(chart, format='png')
    chart.seek(0)
    return chart

@app.route('/', methods=['GET', 'POST'])
def weather():
    city = request.form.get('city', 'London')
    if request.method == 'POST' and city:
        weather_data, air_quality_data = get_weather_data(city)

        days = {}
        for item in weather_data['list']:
            date = item['dt_txt'].split(' ')[0]
            if date not in days:
                days[date] = {
                    'temp_max': item['main']['temp_max'],
                    'temp_min': item['main']['temp_min'],
                    'wind_speed': item['wind']['speed'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'air_quality': air_quality_data['list'][0]['main']['aqi'],  # Example; ensure correct key for AQI
                    'count': 1
                }
            else:
                days[date]['temp_max'] = max(days[date]['temp_max'], item['main']['temp_max'])
                days[date]['temp_min'] = min(days[date]['temp_min'], item['main']['temp_min'])
                days[date]['wind_speed'] += item['wind']['speed']
                days[date]['humidity'] += item['main']['humidity']
                days[date]['pressure'] += item['main']['pressure']
                days[date]['description'] = item['weather'][0]['description']
                days[date]['icon'] = item['weather'][0]['icon']
                days[date]['air_quality'] = air_quality_data['list'][0]['main']['aqi']  # Example; ensure correct key for AQI
                days[date]['count'] += 1

        for day in days:
            days[day]['wind_speed'] /= days[day]['count']
            days[day]['humidity'] /= days[day]['count']
            days[day]['pressure'] /= days[day]['count']
            days[day]['temp_max'] = round(days[day]['temp_max'], 1)
            days[day]['temp_min'] = round(days[day]['temp_min'], 1)
            days[day]['wind_speed'] = round(days[day]['wind_speed'], 1)
            days[day]['humidity'] = round(days[day]['humidity'], 1)
            days[day]['pressure'] = round(days[day]['pressure'], 1)
            days[day]['air_quality'] = round(days[day]['air_quality'])  # Make sure to format AQI appropriately

        # 生成图表
        temp_chart = generate_temperature_chart(days)
        humidity_chart = generate_humidity_chart(days)
        temp_chart_url = '/static/temp_chart.png'
        humidity_chart_url = '/static/humidity_chart.png'

        # 保存图表到文件
        if not os.path.exists('static'):
            os.makedirs('static')
        with open('static/temp_chart.png', 'wb') as f:
            f.write(temp_chart.getvalue())
        with open('static/humidity_chart.png', 'wb') as f:
            f.write(humidity_chart.getvalue())

        return render_template('weather.html', city=city, days=days, temp_chart_url=temp_chart_url, humidity_chart_url=humidity_chart_url)

    return render_template('weather.html', city='', days={}, temp_chart_url='', humidity_chart_url='')

if __name__ == '__main__':
    app.run(debug=True)



















