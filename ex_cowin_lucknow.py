import datetime
from os import truncate
from time import sleep
import requests

# State and districts code can be taken from following
# https://cdn-api.co-vin.in/api/v2/admin/location/states
# https://cdn-api.co-vin.in/api/v2/admin/location/districts/<state_code>
districts = [
        # {
        #     "district_id": 294,
        #     "district_name": "BBMP",
        #     "tg_chat_id": "-1001237906147",
        #     "to_whatsapp_numbers": [
        #         "whatsapp:+919986974206",
        #         "whatsapp:+919936744534",
        #         "whatsapp:+919795872306"
        #     ],
        #     "prev_dump_data": None,
        # },
        # {
        #     "district_id": 265,
        #     "district_name": "Bangalore Urban",
        #     "tg_chat_id": "-1001237906147",
        #     "to_whatsapp_numbers": [
        #         "whatsapp:+919986974206",
        #         "whatsapp:+919936744534",
        #         "whatsapp:+919795872306"
        #     ],
        #     "prev_dump_data": None,
        # },
        # {
        #     "district_id": 276,
        #     "district_name": "Bangalore Rural",
        #     "tg_chat_id": "-1001237906147",
        #     "to_whatsapp_numbers": [
        #         "whatsapp:+919986974206",
        #         "whatsapp:+919936744534",
        #         "whatsapp:+919795872306"
        #     ],
        #     "prev_dump_data": None,
        # },
        {
            "district_id": 670,
            "district_name": "Lucknow",
            "tg_chat_id": "-1001470620240",
            "to_whatsapp_numbers": [
                "whatsapp:+919795872306",
                "whatsapp:+919628522574",
                "whatsapp:+919451972971",
                "whatsapp:+919591945839",
                "whatsapp:+919794311592",
            ],
            "prev_dump_data": None,
        },              
]

# Define Global Variables
payload={}
headers = {"User-Agent":"Chrome/90.0.4430.93"}
max_whatsapp_char_limit=1500
max_tg_char_limit=4000
timeout_multiplier = 1
date_from = datetime.datetime.today().date().strftime("%d-%m-%Y")
avail_data_file_name = "avail_data.txt"
dump_data = None
timeout_list = [1]

MIN_AGE_LIMIT = 18
SESSION_AVAILABLE_CAPACITY = 1
MIN_AVAILABLE_CAPACITY = 1
TIME_SLEEP_PER_LOOP = 15

while True:
    try:
        for district in districts:
            
            url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district['district_id']}&date={date_from}"
            response = requests.get(url, headers=headers, data=payload)
            dump_data = response.json()

        if(dump_data != district['prev_dump_data']):
                district['prev_dump_data'] = dump_data
                    
                avail_data = {}
                centre_data = {}
                centre_data["sessions"] = []
                total_available_capacity = 0

                for center in dump_data["centers"]:
                    centre_data = {}
                    centre_data["name"] = center["name"]
                    centre_data["address"] = center["address"]
                    centre_data["pincode"] = center["pincode"]
                    centre_data["sessions"] = []
                    centre_available_capacity = 0

                    for session in center["sessions"]:
                        if(session["available_capacity"] >= SESSION_AVAILABLE_CAPACITY and session["min_age_limit"] == MIN_AGE_LIMIT ):
                            total_available_capacity += session["available_capacity"]
                            centre_available_capacity += session["available_capacity"]
                            centre_data["sessions"].append(session)
                    centre_data["available_capacity"] = centre_available_capacity
                    if(len(centre_data["sessions"]) > 0):
                        avail_data[center["center_id"]] = centre_data

                # empty the file before writing.
                with open(avail_data_file_name,"r+") as f:
                    f.truncate(0)

                if(len(avail_data.keys()) > 0):
                    with open(avail_data_file_name,"w") as f:
                        f.write(f"\n For age group : {MIN_AGE_LIMIT} plus")
                        f.write(f"\n Total available capacity in {district['district_name']} = {total_available_capacity}")
                        for capacity in avail_data.keys():
                            f.write("\n\n")
                            f.write(f"\n Total slots --> {avail_data[capacity]['available_capacity']}")
                            f.write(f"\n Center Name --> {avail_data[capacity]['name']}")
                            f.write(f"\n Center Address --> {avail_data[capacity]['address']}")
                            f.write(f"\n Center Pincode --> {avail_data[capacity]['pincode']}")
                            f.write(f"\n Vaccine --> {avail_data[capacity]['sessions'][0]['vaccine']}")
                            for session in  avail_data[capacity]["sessions"]:
                                f.write(f"\n      {session['date']} -> {session['available_capacity']}")


                all_text = ""
                with open(avail_data_file_name,"r") as f:
                    all_text = f.read()
                print(all_text)
            
                print("TOTAL AVAILABLE CAPACITY = ",total_available_capacity)
                out_text = [(all_text[i:i+max_tg_char_limit]) for i in range(0, len(all_text), max_tg_char_limit)]
                print(len(out_text))

                # Send Telegram Message

                if(total_available_capacity >= MIN_AVAILABLE_CAPACITY):
                    for line in out_text:     
                        response = requests.get(f"https://api.telegram.org/bot1657544193:AAEs6-oCF3g7HnVlH_wMR7Ao-TBsR1-q3EE/sendMessage?chat_id={district['tg_chat_id']}&text={line}")    
                        if(response.status_code != 200):
                            print(response.text)

        else:
            print(f"\nPrevious data is same as current data for District {district['district_name']}")

        # Sleep for 15 seconds in case no centers are found. 
        # Sleep for 15 * timeout_multiplier, in case centers are found. 
        # timeout_multiplier = max(timeout_list)
        # time_sleep = timeout_multiplier * 15
        time_sleep = TIME_SLEEP_PER_LOOP
        print(f"MIN_AGE_LIMIT : {MIN_AGE_LIMIT}, MIN_AVAILABLE_CAPACITY : {MIN_AVAILABLE_CAPACITY}")
        print(f"Sleeping for {time_sleep} seconds at {datetime.datetime.now()}")
        sleep(time_sleep)

    except Exception as e:
        print(str(e))
        print('Sleeping for 5 Minutes')
        sleep(360)
