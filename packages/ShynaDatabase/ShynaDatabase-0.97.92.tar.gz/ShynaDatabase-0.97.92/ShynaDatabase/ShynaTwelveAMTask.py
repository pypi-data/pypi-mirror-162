from ShynaDatabase import UpdateWeather, ShynaClearHistory


class RunAtTwelve:
    clear_history = ShynaClearHistory.ClearHistory()
    update_weather = UpdateWeather.UpdateWeather()

    def at_twelve(self):
        try:
            self.clear_history.clear_data()
            self.update_weather.update_weather_sentence()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    RunAtTwelve().at_twelve()


