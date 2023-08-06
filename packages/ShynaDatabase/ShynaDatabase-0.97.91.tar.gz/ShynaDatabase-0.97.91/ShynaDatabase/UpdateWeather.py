from ShynaDatabase import Shdatabase
from Shynatime import ShTime
from ShynaProcess import ShynaWeather


class UpdateWeather:
    s_data = Shdatabase.ShynaDatabase()
    s_time = ShTime.ClassTime()
    s_process = ShynaWeather.ShynaWeather()
    update_weather = False
    result = []
    lat = ''
    lon = ''

    def update_weather_sentence(self):
        try:
            self.s_data.query = "SELECT new_latitude, new_longitude FROM shivam_device_location ORDER by count  " \
                                "DESC LIMIT 1;"
            self.result = self.s_data.select_from_table()
            for item in self.result:
                self.lat = item[0]
                self.lon = item[1]
            self.s_process.lon = self.lon
            self.s_process.lat = self.lat
            response = self.s_process.get_weather()
            speak_sentence = "I sense it is " + str(response['condition']) + " weather in " + str(
                response['name']) + ". Ask for more details"
            last_up_dt, last_up_time = self.s_time.get_date_and_time(text_string=response['last_updated'])
            self.s_data.query = "INSERT INTO weather_table (task_date, task_time, sunrise, sunset, weather_description, " \
                                "main_temp, main_feels_like, main_humidity, wind_gust, wind_speed, clouds, loc_name, " \
                                "speak_sentence, visibility, wind_direction, precipitation, moonrise, moonset," \
                                " last_update_date, last_update_time) VALUES('" + str(self.s_time.now_date) + "','" \
                                + str(self.s_time.now_time) + "','" \
                                + str(self.s_time.get_date_and_time(text_string=response['sunrise'])[1]) + "','" \
                                + str(self.s_time.get_date_and_time(text_string=response['sunset'])[1]) + "','" \
                                + str(response['condition']) + "','" + str(response['temp_c']) + "','" \
                                + str(response['feelslike_c']) + "','" + str(response['humidity']) + "','" \
                                + str(response['gust_kph']) + "','" + str(response['wind_kph']) + "','" \
                                + str(response['cloud']) + "','" + str(response['name']) + "','" + str(speak_sentence) \
                                + "','" + str(response['vis_km']) + "','" + str(response['wind_dir']) + "','" \
                                + str(response['precip_mm']) + "','" + str(response['moonrise']) + "','" \
                                + str(response['moonset']) + "','" + str(last_up_dt) + "','" \
                                + str(last_up_time) + "')"
            self.s_data.create_insert_update_or_delete()
            self.update_weather = True
        except Exception as e:
            self.update_weather = False
            print(e)
        finally:
            return self.update_weather


if __name__ == '__main__':
    UpdateWeather().update_weather_sentence()
