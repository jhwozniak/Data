*REFLECTION:*
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
    function, I looped over user's input populating "filtered", a list of selected currency pairs. I was wary of any improper user inputs,
    that's why you will find numerous data validation points and error handling inside the "while" loop. Then, the function iterates
    over the "fx_list", filtering the data with the use of "filtered" list, which it uses as keys to the dictionaries stored there.
    All data is finally stored inside "filtered_fx_list" which is a filtered version of "fx_list" list of dicts. Finally, the filtered
    data is saved in the "selected_currency_data.csv"
    - finally, the function "data_analysis()" iterates over "filtered_fx_list" in order to access historical rates for each selected
    currency pair. This data is temporarily stored in "temp_list", which is then used to calcualte basic statistic measures.
    - last but not least, I've used "schedule" and "time" libriaries in order to make the "fetch_data()" function of the script
    run daily at 12:00PM.

My main consideration while implementing this script was to work out an optimal data structure. I wanted it to have an easy access to data,
to be relatively elastic and reusable. You can see that "fx_list" works fine for this purpose, as it is a list of 60 dicitonaries with keys
as currency pairs and values as historical rates.
