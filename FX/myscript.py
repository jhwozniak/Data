# fetches currency quotations using API of NBP
# saves filtered data in CSV files
# displays basic stats
# downloads data daily at 12:00pm
# pylint: disable=missing-module-docstring

import csv
import time
from statistics import mean, median
import requests
from schedule import every, repeat, run_pending

# available currency pairs
currencies = ["EUR/PLN", "USD/PLN", "CHF/PLN", "EUR/USD", "CHF/USD"]
# dictionary of URLs
url_dict = {
    "EUR/PLN":"http://api.nbp.pl/api/exchangerates/rates/A/EUR/last/60",
    "USD/PLN":"http://api.nbp.pl/api/exchangerates/rates/A/USD/last/60",
    "CHF/PLN":"http://api.nbp.pl/api/exchangerafiltertes/rates/A/CHF/last/60"}
# list of user-selected currency pairs
filtered = []

def main():
    """main function"""
    fx_list = fetch_data()
    filtered_fx_list = pick_currency_pairs(fx_list)
    data_analysis(filtered_fx_list)
    while True:
        run_pending()
        time.sleep(1)

def fetch_data():
    """fetches quotes for the last 60D"""
    fx_list = []
    for key in url_dict.keys():
        response = requests.get(url_dict[key], timeout=100)

        if response.status_code == 200:
            response_json = response.json()
            temp_list_raw = response_json["rates"]
            temp_list = []
            for element in temp_list_raw:
                temp_list.append(element["mid"])
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
    write_to_file(fx_list, "all_currency_data.csv", currencies)
    return fx_list

def pick_currency_pairs(fx_list):
    """writes selected currency pairs into CSV"""
    # looping for customer's input
    print("Choose currency pair(s) and hit ENTER, hit 0 when done: 1 - EUR/PLN, 2 - USD/PLN, 3 - CHF/PLN, 4 - EUR/USD, 5 - CHF/USD")
    while True:
        try:
            number = int(input("Your choice: "))
            if number < 0:
                print("Thas number was not valid, it must be between 1 and 5 or 0 when done.")
            elif number == 0:
                break
            else:
                filtered.append(currencies[number - 1])
        except ValueError:
            print("That was not a valid number. Please try again...")
        except IndexError:
            print("Thas number was not valid, it must be between 1 and 5 or 0 when done.")

    # when no currency pairs were selected...
    if not filtered:
        return "No selection has been made."
    # filtering fx_list with help of temporary list
    filtered_fx_list = []
    for element in fx_list:
        temp_dict = {}
        for fx_pair in filtered:
            temp_dict[fx_pair] = element[fx_pair]
        filtered_fx_list.append(temp_dict)

    # writing filtered data into CSV
    write_to_file(filtered_fx_list, "selected_currency_data.csv", filtered)
    return filtered_fx_list


def data_analysis(filtered_fx_list):
    """diplays data analysis for the selected currency pairs"""
    for fx_pair in filtered:
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

def write_to_file(data_source, filename, columns):
    """writes from selected data source to CSV file:"""
    try:
        with open(filename, 'w', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data_source)
        print("Data for {} has been saved!".format(columns))
    except csv.Error:
        print("There has been an error when writing to the file. Please try again...")

@repeat(every(1).day.at("00:00"))
def job():
    """runs daily at 12:00 PM and automatically saves the data to CSV"""
    fetch_data()

main()
