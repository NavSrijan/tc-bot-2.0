import pdb

def load_countries(file="country_data.csv"):
    with open(file, "r") as f:
        data = f.readlines()
    countries = {}
    for i in data:
        j = i.split(",")
        countries[j[0][1:-1].lower()] = j[1][1:-1].lower()
    return countries

dd = load_countries()
pdb.set_trace()