# fetches currency quotations using API of NBP, stores full- and user-filtered data in CSV files, displays basic statistics,
# downloads data daily at 12:00pm
"""REFLECTION:
This was my thought process when doing this script:
    - first, I analyzed API documentation at api.nbp.pl and tried to understand possible data formats and available options.
    I've decided to use json format, as it is well accepted by Python and it works well with it's basic data sctructures like
    lists and dictionaries.
    - secondly, I've structured the script in such a way, that within "main()" there are three function calls: "fetch_data()",
    "pick_currency_pairs()" and "data_analysis()". They service basic functionalities of the script. They are also interlinked:
    please note how return value of one serves as an input for the another. First two of them also call "write-to-file()" function
    which was defined separately in order to save code space and for future reuse.
    - thirdly, within the "fetch_data()" function, I filtered the basic json file, which I was getting at each API call, with the use
     of temporary list ("temp_list"). Then, I've populated my basic-to-go data structure "fx_list" (a list of 60 dictionaries),
     with the currency rates from temp_list. Finally, I've written the data in the "all_currency_data.csv"
    - then, I've defined "pick_currency_pairs()" function. As an input, I've used the "fx_list", my basic list of dicts. Inside this
    function, I looped over user's input populating "filter", a list of selected currency pairs. I was wary of any improper user inputs,
    that's why you will find numerous data validation points and error handling inside the "while" loop. Then, the function iterates
    over the "fx_list", filtering the data with the use of "filter" list, which it uses as keys to the dictionaries stored there.
    All data is finally stored inside "filtered_fx_list" which is a filtered version of "fx_list" list of dicts. Finally, the filtered
    data is saved in the "selected_currency_data.csv"
    - finally, the function "data_analysis()" iterates over "filtered_fx_list" in order to access historical rates for each selected
    currency pair. This data is temporarily stored in "temp_list", which is then used to calcualte basic statistic measures.
    - last but not least, I've used "schedule" and "time" libriaries in order to make the "fetch_data()" function of the script
    run daily at 12:00PM.
My main consideration while implementing this script was to work out an optimal data structure. I wanted it to have an easy access to data,
to be relatively elastic and reusable. You can see that "fx_list" works fine for this purpose, as it is a list of 60 dicitonaries with keys
as currency pairs and values as historical rates.
"""
import json
import requests 
import sys
import csv
from statistics import mean, median
from schedule import every, repeat, run_pending
import time

# available currency pairs
currencies = ["EUR/PLN", "USD/PLN", "CHF/PLN", "EUR/USD", "CHF/USD"]
# dictionary of URLs
url_dict = {
    "EUR/PLN":"http://api.nbp.pl/api/exchangerates/rates/A/EUR/last/60",
    "USD/PLN":"http://api.nbp.pl/api/exchangerates/rates/A/USD/last/60",
    "CHF/PLN":"http://api.nbp.pl/api/exchangerates/rates/A/CHF/last/60"}
# list of user-selected currency pairs
filter = []

def main():
    fx_list = fetch_data()
    filtered_fx_list = pick_currency_pairs(fx_list)
    data_analysis(filtered_fx_list)
    while True:
        run_pending()
        time.sleep(1)

# fetches currency quotations for the last 60 days for 5 currency pairs using API of NBP
def fetch_data():
    # intializing list for 60 dictionaries (intermediate data struct between API calls and CSV writing)
    fx_list = []
    # making API calls
    for key in url_dict.keys():
        response = requests.get(url_dict[key])
        if response.status_code == 200:
            response_json = response.json()

            # shelling out list of 60 dictionaries from that API call
            temp_list_raw = response_json["rates"]
            temp_list = []
            for element in temp_list_raw:
                temp_list.append(element["mid"])

            # populate fx_list at key of an API call
            if not fx_list:
                for fx in temp_list:
                    temp_dict = {}
                    temp_dict[key] = fx
                    fx_list.append(temp_dict)
            else:
                for i, v in enumerate(fx_list):
                    v[key] = temp_list[i]
        else:
            print("There was an error when fetching data from API, status code: " + response.status_code)

    # appending EUR/USD and CHF/USD rates into fx_list
    for i in range(60):
        fx_list[i]["EUR/USD"] = round(float(fx_list[i]["EUR/PLN"]) / float(fx_list[i]["USD/PLN"]), 4)
        fx_list[i]["CHF/USD"] = round(float(fx_list[i]["CHF/PLN"]) / float(fx_list[i]["USD/PLN"]), 4)

    # writing to CSV file
    write_to_file(fx_list, "all_currency_data.csv", currencies)

    return fx_list

# writes selected currency pairs data into CSV
def pick_currency_pairs(fx_list):
    # looping for customer's input
    print("Choose currency pair(s) and hit ENTER, hit 0 when done: 1 - EUR/PLN, 2 - USD/PLN, 3 - CHF/PLN, 4 - EUR/USD, 5 - CHF/USD")
    while True:
        try:
            number = int(input("Your choice: "))
            if number < 0:
                print("Thas number was not valid, it must be between 1 and 5 or 0 when done.")
            elif (number == 0):
                break
            else:
                filter.append(currencies[number - 1])
        except ValueError:
            print("That was not a valid number. Please try again...")
        except IndexError:
            print("Thas number was not valid, it must be between 1 and 5 or 0 when done.")

    # when no currency pairs were selected...
    if not filter:
        print("No selection has been made.")
        return
    else:
        # filtering fx_list with help of temporary list
        filtered_fx_list = []
        for element in fx_list:
            temp_dict = {}
            for fx_pair in filter:
                temp_dict[fx_pair] = element[fx_pair]
            filtered_fx_list.append(temp_dict)

        # writing filtered data into CSV
        write_to_file(filtered_fx_list, "selected_currency_data.csv", filter)

        return filtered_fx_list

# diplays data analysis for the selected currency pairs
def data_analysis(filtered_fx_list):
    for fx_pair in filter:
        print()
        print("Statistics for " + fx_pair + ":")
        print("------------------------")
        temp_list = []
        for element in filtered_fx_list:
            temp_list.append(element[fx_pair])
        print("average rate: " + str(round(mean(temp_list), 4)))
        print("median rate: " + str(median(temp_list)))
        print("minimum rate: " + str(min(temp_list)))
        print("maximum rate: " + str(max(temp_list)))
    return

# writes from selected data source to CSV file:
def write_to_file(data_source, filename, columns):
    try:
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data_source)
        print("Data for {} has been saved!".format(columns))
    except csv.Error:
        print("There has been an error when writing to the file. Please try again...")
    return

# runs daily at 12:00 PM and automatically saves the data to the "all_currency_data.csv" file
@repeat(every(1).day.at("00:00"))
def job():
    fetch_data()

main()

