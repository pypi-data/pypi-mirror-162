def check_case(args):
    if (args["Nor"] != None) and (args["Nori"] == None) and (args["Nork"] == None):
        return "NOR"
    elif (args["Nor"] != None) and (args["Nori"] != None) and (args["Nork"] == None):
        return "NOR-NORI"  
    elif (args["Nor"] != None) and (args["Nori"] == None) and (args["Nork"] != None):
        return "NOR-NORK"
    elif (args["Nor"] != None) and (args["Nori"] != None) and (args["Nork"] != None):
        return "NOR-NORI-NORK"
    else:
        raise ValueError(('Incorrect value for Kasua. Read README.md or the documentation at https://github.com/HCook86/Aditzak/blob/heroku/README.md for more information'))

def analyze():
    return None

#analyze({"Aditza":None, "Kasua":"NOR-NORK", "Modua":"Ahalera","Denbora":"Oraina", "Nor":"zuek", "Nori":None, "Nork":"hark"})