"""SkyCast — a single-file Python Tkinter weather application.
Uses Open-Meteo's geocoding and forecast APIs; no API key required.
"""
import json
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search'
FORECAST_URL = 'https://api.open-meteo.com/v1/forecast'
WEATHER_CODES = {
    0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
    45: 'Fog', 48: 'Depositing rime fog', 51: 'Light drizzle',
    53: 'Moderate drizzle', 55: 'Dense drizzle', 56: 'Freezing drizzle',
    57: 'Dense freezing drizzle', 61: 'Slight rain', 63: 'Moderate rain',
    65: 'Heavy rain', 66: 'Freezing rain', 67: 'Heavy freezing rain',
    71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
    77: 'Snow grains', 80: 'Slight rain showers', 81: 'Rain showers',
    82: 'Violent rain showers', 85: 'Snow showers', 86: 'Heavy snow showers',
    95: 'Thunderstorm', 96: 'Thunderstorm with hail',
    99: 'Thunderstorm with heavy hail'
}


def get_json(url, params):
    address = url + '?' + urlencode(params)
    request = Request(address, headers={'User-Agent': 'SkyCast-College-Project/1.0'})
    try:
        with urlopen(request, timeout=12) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise ConnectionError('Cannot connect to the weather service. Check your internet connection.') from error
    except (json.JSONDecodeError, UnicodeError) as error:
        raise ValueError('Weather service returned invalid data.') from error


def get_coordinates(city):
    data = get_json(GEOCODING_URL, {'name': city, 'count': 1, 'language': 'en', 'format': 'json'})
    results = data.get('results') or []
    if not results:
        raise ValueError(f'City "{city}" was not found. Try another city.')
    place = results[0]
    label = ', '.join(part for part in [place.get('name'), place.get('admin1'), place.get('country')] if part)
    return place['latitude'], place['longitude'], label


def get_weather(latitude, longitude):
    data = get_json(FORECAST_URL, {
        'latitude': latitude,
        'longitude': longitude,
        'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m',
        'daily': 'weather_code,temperature_2m_max,temperature_2m_min',
        'timezone': 'auto',
        'forecast_days': 5,
        'wind_speed_unit': 'kmh',
    })
    if 'current' not in data or 'daily' not in data:
        raise ValueError('Weather information is temporarily unavailable.')
    return data


def condition(code):
    return WEATHER_CODES.get(code, 'Unknown conditions')


class SkyCastApp:
    def __init__(self, root):
        self.root = root
        root.title('SkyCast | Live Weather Application')
        root.geometry('790x650')
        root.minsize(640, 570)
        root.configure(bg='#0c1830')
        self.city = tk.StringVar(value='Patna')
        self.status = tk.StringVar(value='Enter a city and select Get Weather.')
        self.location = tk.StringVar(value='Search for a city')
        self.temperature = tk.StringVar(value='--°C')
        self.description = tk.StringVar(value='Weather conditions will appear here')
        self.feels_like = tk.StringVar(value='--°C')
        self.humidity = tk.StringVar(value='--%')
        self.wind = tk.StringVar(value='-- km/h')
        self.busy = False
        self.build_ui()
        root.bind('<Return>', lambda event: self.search())

    def label(self, parent, text, size=12, color='#d9e7ff', bold=False, **kwargs):
        return tk.Label(parent, text=text, bg=kwargs.pop('bg', '#0c1830'),
                        fg=color, font=('Segoe UI', size, 'bold' if bold else 'normal'), **kwargs)

    def build_ui(self):
        outer = tk.Frame(self.root, bg='#0c1830', padx=25, pady=20)
        outer.pack(fill='both', expand=True)
        self.label(outer, '☀  SkyCast', 26, '#38d9f5', True).pack(anchor='w')
        self.label(outer, 'LIVE WEATHER APPLICATION  •  PYTHON + TKINTER + OPEN-METEO', 10, '#9bb4d8').pack(anchor='w', pady=(0, 20))

        search = tk.Frame(outer, bg='#0c1830')
        search.pack(fill='x')
        self.entry = tk.Entry(search, textvariable=self.city, font=('Segoe UI', 15),
                              bg='#f3f8ff', fg='#0c1830', relief='flat', insertbackground='#0c1830')
        self.entry.pack(side='left', fill='x', expand=True, ipady=9)
        self.button = tk.Button(search, text='Get Weather', command=self.search,
                                bg='#19c9e7', fg='#061527', activebackground='#69e7f6',
                                relief='flat', font=('Segoe UI', 12, 'bold'), padx=15, pady=8, cursor='hand2')
        self.button.pack(side='left', padx=(10, 0))

        current = tk.Frame(outer, bg='#142744', padx=20, pady=16)
        current.pack(fill='x', pady=(18, 14))
        self.label(current, '', 17, '#ffffff', True, bg='#142744', textvariable=self.location).pack(anchor='w')
        self.label(current, '', 42, '#38d9f5', True, bg='#142744', textvariable=self.temperature).pack(anchor='w')
        self.label(current, '', 13, '#e3edff', bg='#142744', textvariable=self.description).pack(anchor='w')

        metrics = tk.Frame(outer, bg='#0c1830')
        metrics.pack(fill='x', pady=(0, 16))
        for title, variable in [('Feels like', self.feels_like), ('Humidity', self.humidity), ('Wind speed', self.wind)]:
            card = tk.Frame(metrics, bg='#142744', padx=13, pady=12)
            card.pack(side='left', expand=True, fill='both', padx=3)
            self.label(card, title, 10, '#9bb4d8', bg='#142744').pack(anchor='w')
            self.label(card, '', 17, '#ffffff', True, bg='#142744', textvariable=variable).pack(anchor='w', pady=(5, 0))

        self.label(outer, '5-DAY FORECAST', 13, '#ffffff', True).pack(anchor='w', pady=(0, 8))
        forecast = tk.Frame(outer, bg='#0c1830')
        forecast.pack(fill='x')
        self.cards = []
        for _ in range(5):
            card = tk.Frame(forecast, bg='#142744', padx=7, pady=12)
            card.pack(side='left', fill='both', expand=True, padx=3)
            day = self.label(card, '---', 10, '#b5c7e6', True, bg='#142744')
            day.pack()
            desc = self.label(card, '--', 9, '#e3edff', bg='#142744', wraplength=95)
            desc.pack(pady=8)
            temp = self.label(card, '-- / --', 11, '#38d9f5', True, bg='#142744')
            temp.pack()
            self.cards.append((day, desc, temp))

        self.label(outer, '', 10, '#a8bad5', textvariable=self.status,
                   wraplength=680, justify='left').pack(anchor='w', pady=(16, 0))
        self.label(outer, 'Weather data: Open-Meteo  |  Internet connection required', 9, '#8299bc').pack(anchor='w', pady=(5, 0))

    def search(self):
        city = self.city.get().strip()
        if not city:
            messagebox.showwarning('SkyCast', 'Please enter a city name.')
            return
        if self.busy:
            return
        self.busy = True
        self.button.config(state='disabled', text='Loading...')
        self.status.set(f'Fetching latest available weather for {city}...')
        threading.Thread(target=self.fetch, args=(city,), daemon=True).start()

    def fetch(self, city):
        try:
            lat, lon, label = get_coordinates(city)
            data = get_weather(lat, lon)
        except (ValueError, ConnectionError, KeyError, TypeError) as error:
            self.root.after(0, lambda msg=str(error): self.finish_error(msg))
        else:
            self.root.after(0, lambda: self.show_weather(label, data))

    def finish_error(self, message):
        self.busy = False
        self.button.config(state='normal', text='Get Weather')
        self.status.set(message)
        messagebox.showerror('SkyCast', message)

    def show_weather(self, label, data):
        try:
            current = data['current']
            daily = data['daily']
            forecast = []
            for i in range(5):
                date = datetime.strptime(daily['time'][i], '%Y-%m-%d')
                forecast.append((date.strftime('%a %d %b'),
                                 condition(daily['weather_code'][i]),
                                 f"{daily['temperature_2m_max'][i]:.0f}° / {daily['temperature_2m_min'][i]:.0f}°"))
            self.location.set(label)
            self.temperature.set(f"{current['temperature_2m']:.0f}°C")
            self.description.set(condition(current['weather_code']))
            self.feels_like.set(f"{current['apparent_temperature']:.0f}°C")
            self.humidity.set(f"{current['relative_humidity_2m']:.0f}%")
            self.wind.set(f"{current['wind_speed_10m']:.0f} km/h")
            for (day, desc, temp), (day_text, desc_text, temp_text) in zip(self.cards, forecast):
                day.config(text=day_text)
                desc.config(text=desc_text)
                temp.config(text=temp_text)
            self.status.set('Weather updated successfully. Data: Open-Meteo.')
        except (KeyError, IndexError, ValueError, TypeError) as error:
            self.status.set('Unexpected weather response. Please try again.')
            messagebox.showerror('SkyCast', 'Weather data could not be displayed. Please try again.')
        finally:
            self.busy = False
            self.button.config(state='normal', text='Get Weather')


if __name__ == '__main__':
    root = tk.Tk()
    SkyCastApp(root)
    root.mainloop()
