# ShynaDatabase

***Suggested: Not to use***

This package will take care of cleaning the database and querying the database. More functionality will be added as I process.

***_Note_***: Make sure to update the default_database before running any query otherwise it won't work at all.
User , host and password are as per environment variable. 
```
Shdatabase
    1) check_connectivity : Check database connectivity
    2) create_insert_update_or_delete: as per name, no return
    3) select_from_table : return output as list
    4) set_date_system: update last run in status_db
    5) insert_or_update_or_delete_with_status: as per name, return will True or False
    
ShynaIs
    Is_Shivam table is created for now but not connected
    Looking out for below details to crosscheck the environment health
    For Mobile:
    1)  is_location_received_from_primary_mobile?
    2)  is_this_is_the_first_alarm?
    3)  is_shivam__still_walking_driving?
    4)  is_mobile_device_offline?
    5)  is_shivam_at_home?
    6)  is_shivam_in_front_of_any_cam?
    7)  is_there_alarm_to_set?
    8)  is_shivam_working_for_more_than_4_hour?
    9)  is_shivam_working_for_more_than_6_hour?
    10) is_shivam_working_for_more_than_8_hour?
    11) is_this_is_first_time_on_cam?
    12) is_shivam_working_late_night?
    13) is_shivam_dead?
    14) is_PC_online?
    15) is_termux_device_online?
    16) is_rasp_online?
    17) is_cam_online?
    18) speak_device_is

    For now if the data is received, we are good, if not then create a task for rasp to speak where the data is not received.
    ==========================================================================================================================
    Future Plan

    1) Is there anything shivam should be aware about
    2) Is last bill costly then last one
    3) Is Shivam watching movies?
    4) Is there item in buying list
    5) Is there a buying list
````
