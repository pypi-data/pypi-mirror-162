from Shynatime import ShTime
from haversine import haversine
from ShynaDatabase import Shdatabase


class UpdateDistanceSpeed:
    s_data = Shdatabase.ShynaDatabase()
    s_time = ShTime.ClassTime()
    result = []
    latitude_List = []
    longitude_list = []
    count = []
    time_list = []

    def update_distance_with_haversine(self):

        try:
            self.s_data.query = "SELECT count, new_time, new_latitude, new_longitude FROM shivam_device_location where " \
                                "status = 'False' order by count DESC"
            self.result = self.s_data.select_from_table()
            for item in self.result:
                self.count.append(item[0])
                self.time_list.append(item[1])
                self.latitude_List.append(item[2])
                self.longitude_list.append(item[3])
            for i in range(len(self.count) - 1):
                distance_difference = haversine(point1=(float(self.latitude_List[i]),float(self.longitude_list[i])), point2=(float(self.latitude_List[i + 1]),float(self.longitude_list[i + 1])), unit='m')
                time_diff = (self.s_time.string_to_time_with_date(self.time_list[i]) - self.s_time.string_to_time_with_date(self.time_list[i + 1])).seconds
                speed = distance_difference/time_diff
                speed_km = 3.6*float(speed)
                print(distance_difference, speed, speed_km)
                self.s_data.query = "UPDATE shivam_device_location SET shivam_distance_from_previous='" \
                                    + str(distance_difference) + "' , shivam_speed='"+str(speed)+"', shivam_speed_in_km='"+str(speed_km)+"' , status='True' WHERE count='" + str(self.count[i]) + "';"
                self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    UpdateDistanceSpeed().update_distance_with_haversine()
