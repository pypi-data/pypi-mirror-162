from ShynaDatabase import Shdatabase
from Shynatime import ShTime


class ClearHistory:
    s_data = Shdatabase.ShynaDatabase()
    s_time = ShTime.ClassTime()
    count_list = []
    result = s_time.subtract_date(s_time.now_date, how_many=30).date()
    count = []

    def clear_location_data(self):
        try:
            self.s_data.query = "Select count from shivam_device_location where new_date='"+str(self.result)+"'"
            self.count_list = self.s_data.select_from_table()
            if str(self.count_list[0]).lower().__contains__('empty'):
                pass
            else:
                for i in range(len(self.count_list)):
                    self.count.append(self.count_list[i][0])
                self.s_data.query = str("Delete from shivam_device_location where count in "+str(self.count)+"").replace('[', '(').replace(']', ')')
                print(self.s_data.query)
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)

    def clear_termux_connection_data(self):
        try:
            self.s_data.query = "Select count from connection_check where new_date='"+str(self.result)+"'"
            self.count_list = self.s_data.select_from_table()
            if str(self.count_list[0]).lower().__contains__('empty'):
                pass
            else:
                for i in range(len(self.count_list)):
                    self.count.append(self.count_list[i][0])
                self.s_data.query = str("Delete from connection_check where count in "+str(self.count)+"").replace('[', '(').replace(']', ')')
                print(self.s_data.query)
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)

    def clear_shivam_face_data(self):
        try:
            self.s_data.query = "Select count from shivam_face where task_date='"+str(self.result)+"'"
            self.count_list = self.s_data.select_from_table()
            if str(self.count_list[0]).lower().__contains__('empty'):
                pass
            else:
                for i in range(len(self.count_list)):
                    self.count.append(self.count_list[i][0])
                self.s_data.query = str("Delete from shivam_face where count in "+str(self.count)+"").replace('[', '(').replace(']', ')')
                print(self.s_data.query)
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)
    
    def clear_weather_data(self):
        try:
            self.s_data.query = "Select count from weather_table where task_date='"+str(self.result)+"'"
            self.count_list = self.s_data.select_from_table()
            if str(self.count_list[0]).lower().__contains__('empty'):
                pass
            else:
                for i in range(len(self.count_list)):
                    self.count.append(self.count_list[i][0])
                self.s_data.query = str("Delete from weather_table where count in "+str(self.count)+"").replace('[', '(').replace(']', ')')
                print(self.s_data.query)
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)

    def clear_master_notify_data(self):
        try:
            self.s_data.query = "Select count from master_notify where task_date='"+str(self.result)+"'"
            self.count_list = self.s_data.select_from_table()
            if str(self.count_list[0]).lower().__contains__('empty'):
                pass
            else:
                for i in range(len(self.count_list)):
                    self.count.append(self.count_list[i][0])
                self.s_data.query = str("Delete from master_notify where count in "+str(self.count)+"").replace('[', '(').replace(']', ')')
                print(self.s_data.query)
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)

    def clear_data(self):
        try:
            print("Cleaining Data is", self.result)
            print("clear_location_data")
            self.clear_location_data()
            print("clear_shivam_face_data")
            self.clear_shivam_face_data()
            print("clear_termux_connection_data")
            self.clear_termux_connection_data()
            print("clear_weather_data")
            self.clear_weather_data()
            print("clear_master_notify_data")
            self.clear_master_notify_data()
        except Exception as e:
            print(e)
        finally:
            self.s_data.set_date_system(process_name="clear_data")


