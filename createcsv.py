#import json

#csv = open("citylist.csv", "w")
#with open("city.list.json", "r") as rf:
#        city_data = json.load(rf)


#        for s in range(len(city_data)):

#                csv.write( city_data[s]["name"] + ";" + 
#                   city_data[s]["state"] + ";" +
#                   city_data[s]["country"] + ";" +  str(city_data[s]["coord"]['lat']) + ";" + str(city_data[s]["coord"]['lon']) + '\n')

#csv.close()

#os.system('sort citylist.csv -o citylist.csv')

start = ''
print('{')
with open("citylist.csv", "r") as rf:
            line = rf.readline()
            while line:
                line = rf.readline()
                if line:
                 if line[0].lower() != start.lower():
                   print('\'' + line[0].lower() + '\': ' + str(rf.tell()) + ',', end='')
                   start = line[0]
print('}')
