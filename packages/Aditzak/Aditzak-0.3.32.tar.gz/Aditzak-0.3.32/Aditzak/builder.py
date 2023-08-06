from json import loads
from os import path

def nori(args):
    verb = None
    if args["Nori"] == "niri":
        if args["Modua"] == "Indikatiboa":
            if args["Denbora"] == "Oraina":
                verb = args["Aditza"].replace("(nori)", "t")
            if args["Denbora"] == "Iragana":
                verb = args["Aditza"].replace("(nori)", "da")    
        if args["Modua"] == "Subjuntiboa":
            verb = args["Aditza"].replace("(nori)", "da")
        if args["Modua"] == "Agintera" or args["Modua"] == "Baldintza":
            if args["Aditza"].endswith("te"):
                verb = args["Aditza"].replace("(nori)", "da")
            else:
                verb = args["Aditza"].replace("(nori)", "t")
        print("HALF IMPLEMENTED")
    if args["Nori"] == "hiri":
        raise NotImplementedError("NOT IMPLEMENTED")
    if args["Nori"] == "hari":
        if (args["Modua"] == "Agintera" or args["Modua"] == "Ahalera") and not "i(nori)" in args["Aditza"]:
            verb = args["Aditza"].replace("(nori)", "io")
        else:
            verb = args["Aditza"].replace("(nori)", "o")
    if args["Nori"] == "guri":
        verb = args["Aditza"].replace("(nori)", "gu")
    if args["Nori"] == "zuri":
        verb = args["Aditza"].replace("(nori)", "zu")
    if args["Nori"] == "zuei":
        verb = args["Aditza"].replace("(nori)", "zue")
    if args["Nori"] == "haiei":
        if (args["Modua"] == "Subjuntiboa" and args["Kasua"] == "NOR-NORI-NORK") or (args["Modua"] == "Agintera") and not "i(nori)" in args["Aditza"]:
            verb = args["Aditza"].replace("(nori)", "ie")
        else:
            verb = args["Aditza"].replace("(nori)", "e")
    return verb

def nork(args):
    verb = None
    if args["Nork"] == "nik":
        verb = args["Aditza"].replace("(nork)", "t")
    """if args["Nork"] == "hik":
    """
    if args["Nork"] == "hark":
        verb = args["Aditza"].replace("(nork)", "")
    if args["Nork"] == "guk":
        verb = args["Aditza"].replace("(nork)", "gu")
    if args["Nork"] == "zuk":
        verb = args["Aditza"].replace("(nork)", "zu")
    if args["Nork"] == "zuek":
        verb = args["Aditza"].replace("(nork)", "zue")
    if args["Nork"] == "haiek":
        verb = args["Aditza"].replace("(nork)", "te")
    return verb


def build(args):
    #If Aditza isn't None, raise an exception
    if args["Aditza"] != None:
        raise ValueError('Incorrect value for Aditza: Aditza always must have the value None. Read README.txt or the documentation at https://github.com/HCook86/Aditzak/blob/heroku/README.md for more information')
    else:
        args["Aditza"] = ""

    if args["Kasua"] == "NOR":
        if args["Nork"] != None or args["Nori"] != None:
            raise ValueError('Incorrect value for Nork and/or Nori: If Kasua = Nor, Nork and Nori must be = None. Read README.txt or the documentation at https://github.com/HCook86/Aditzak/blob/heroku/README.md for more information')
        handler = open(path.join(path.dirname(__file__), "nor.json"), "r")
        file = loads(handler.read())
        try:
            args["Aditza"] = file[args["Modua"]][args["Denbora"]][args["Nor"]]
        except:
            args["Aditza"] = None
            

    #If the case is NOR-NORI  
    elif args["Kasua"] == "NOR-NORI":
        if args["Modua"] == "Indikatiboa":
            if args["Denbora"] == "Oraina":
                if args["Nor"] == "ni":
                    args["Aditza"] = "natzai"
                if args["Nor"] == "hi":
                    args["Aditza"] = "hatzai"
                if args["Nor"] == "hura":
                    args["Aditza"] = "zai"
                if args["Nor"] == "gu":
                    args["Aditza"] = "gatzaizki"
                if args["Nor"] == "zu":
                    args["Aditza"] = "zatzaizki"
                if args["Nor"] == "zuek":
                    args["Aditza"] = "zatzaizki(zuek)"
                if args["Nor"] == "haiek":
                    args["Aditza"] = "zaizki"
                
                args["Aditza"] = args["Aditza"] + ("(nori)")
            
                if args["Aditza"].startswith("zatzaizki(zuek)"):
                    args["Aditza"] = args["Aditza"].replace("(zuek)", "")
                    args["Aditza"] = args["Aditza"] + "te"

            if args["Denbora"] == "Iragana":
                if args["Nor"] == "ni":
                    args["Aditza"] = "nintzai"
                if args["Nor"] == "hi":
                    args["Aditza"] = "hintzai"
                if args["Nor"] == "hura":
                    args["Aditza"] = "zintzai"
                if args["Nor"] == "gu":
                    args["Aditza"] = "gintzaizki"
                if args["Nor"] == "zu":
                    args["Aditza"] = "zintzaizki"
                if args["Nor"] == "zuek":
                    args["Aditza"] = "zintzaizki(zuek)"
                if args["Nor"] == "haiek":
                    args["Aditza"] = "zitzaizki"
    
                args["Aditza"] = args["Aditza"] + ("(nori)")
                
                if args["Aditza"].startswith("zintzaizki(zuek)"):
                    args["Aditza"] = args["Aditza"].replace("(zuek)", "")
                    args["Aditza"] = args["Aditza"] + "te"

                args["Aditza"] = args["Aditza"] + "n"
        
        if args["Modua"] == "Baldintza":
            args["Aditza"] = "ba"
            
            if args["Nor"] == "ni":
                args["Aditza"] = args["Aditza"] + "nintzai"
            if args["Nor"] == "hi":
                args["Aditza"] = args["Aditza"] + "hintzai"
            if args["Nor"] == "hura":
                args["Aditza"] = args["Aditza"] + "litzai"
            if args["Nor"] == "gu":
                args["Aditza"] = args["Aditza"] +  "gintzaizki"
            if args["Nor"] == "zu":
                args["Aditza"] = args["Aditza"] +  "zintzaizki"
            if args["Nor"] == "zuek":
                args["Aditza"] = args["Aditza"] +  "zintzaizki(zuek)"
            if args["Nor"] == "haiek":
                args["Aditza"] = args["Aditza"] +  "litzaizki"

            args["Aditza"] = args["Aditza"] + ("(nori)")

            if args["Aditza"].startswith("bazintzaizki(zuek)"):
                args["Aditza"] = args["Aditza"].replace("(zuek)", "")
                args["Aditza"] = args["Aditza"] + "te"
            
        if args["Modua"] == "Ondorioa":
            if args["Nor"] == "ni":
                args["Aditza"] = "nintzai"
            if args["Nor"] == "hi":
                args["Aditza"] = "hintzai"
            if args["Nor"] == "hura":
                args["Aditza"] = "litzai"
            if args["Nor"] == "gu":
                args["Aditza"] = "gintzaizki"
            if args["Nor"] == "zu":
                args["Aditza"] = "zintzaizki"
            if args["Nor"] == "zuek":
                args["Aditza"] = "zintzaizki(zuek)"
            if args["Nor"] == "haiek":
                args["Aditza"] = "litzaizki"

            args["Aditza"] = args["Aditza"] + ("(nori)")

            args["Aditza"] = args["Aditza"] + "ke"
            
            if args["Aditza"].startswith("zintzaizki(zuek)"):
                args["Aditza"] = args["Aditza"].replace("(zuek)", "")
                args["Aditza"] = args["Aditza"] + "te"

            if args["Denbora"] == "Iragana":
                if args["Aditza"].endswith("te"):
                    args["Aditza"] = args["Aditza"] + "n"
                else:
                    args["Aditza"] = args["Aditza"] + "en"


        if args["Modua"] == "Ahalera":
            if args["Denbora"] == "Oraina":
                if args["Nor"] == "ni":
                    args["Aditza"] = "naki"
                if args["Nor"] == "hi":
                    args["Aditza"] = "haki"
                if args["Nor"] == "hura":
                    args["Aditza"] = "daki"
                if args["Nor"] == "gu":
                    args["Aditza"] = "gakizki"
                if args["Nor"] == "zu":
                    args["Aditza"] = "zakizki"
                if args["Nor"] == "zuek":
                    args["Aditza"] = "zakizki(zuek)"
                if args["Nor"] == "haiek":
                    args["Aditza"] = "zaizki"
            
            if args["Denbora"] == "Iragana":
                if args["Nor"] == "ni":
                    args["Aditza"] = "nenki"
                if args["Nor"] == "hi":
                    args["Aditza"] = "henki"
                if args["Nor"] == "hura":
                    args["Aditza"] = "zeki"
                if args["Nor"] == "gu":
                    args["Aditza"] = "gakizki"
                if args["Nor"] == "zu":
                    args["Aditza"] = "zakizki"
                if args["Nor"] == "zuek":
                    args["Aditza"] = "zakizki(zuek)"
                if args["Nor"] == "haiek":
                    args["Aditza"] = "zekizki"

            if args["Denbora"] == "Hipotetikoa":
                if args["Nor"] == "ni":
                    args["Aditza"] = "nenki"
                if args["Nor"] == "hi":
                    args["Aditza"] = "henki"
                if args["Nor"] == "hura":
                    args["Aditza"] = "leki"
                if args["Nor"] == "gu":
                    args["Aditza"] = "gakizki"
                if args["Nor"] == "zu":
                    args["Aditza"] = "zakizki"
                if args["Nor"] == "zuek":
                    args["Aditza"] = "zakizki(zuek)"
                if args["Nor"] == "haiek":
                    args["Aditza"] = "lekizki"
                
            args["Aditza"] = args["Aditza"] + ("(nori)")

            args["Aditza"] = args["Aditza"] + "ke"

            if args["Aditza"].startswith("zakizki(zuek)"):
                args["Aditza"] = args["Aditza"].replace("(zuek)", "")
                args["Aditza"] = args["Aditza"] + "te"
            
            if args["Denbora"] == "Iragana":
                if args["Aditza"].endswith("te"):
                    args["Aditza"] = args["Aditza"] + "n"
                else:
                    args["Aditza"] = args["Aditza"] + "en"


        if args["Modua"] == "Subjuntiboa":
            if args["Denbora"] == "Oraina":
                if args["Nor"] == "ni":
                    args["Aditza"] = "naki"
                if args["Nor"] == "hi":
                    args["Aditza"] = "haki"
                if args["Nor"] == "hura":
                    args["Aditza"] = "daki"
                if args["Nor"] == "gu":
                    args["Aditza"] = "gakizki"
                if args["Nor"] == "zu":
                    args["Aditza"] = "zakizki"
                if args["Nor"] == "zuek":
                    args["Aditza"] = "zakizki(zuek)"
                if args["Nor"] == "haiek":
                    args["Aditza"] = "zaizki"

                args["Aditza"] = args["Aditza"] + ("(nori)")
                

            if args["Denbora"] == "Iragana":
                if args["Nor"] == "ni":
                    args["Aditza"] = "nenki"
                if args["Nor"] == "hi":
                    args["Aditza"] = "henki"
                if args["Nor"] == "hura":
                    args["Aditza"] = "zeki"
                if args["Nor"] == "gu":
                    args["Aditza"] = "genkizki"
                if args["Nor"] == "zu":
                    args["Aditza"] = "zenkizki"
                if args["Nor"] == "zuek":
                    args["Aditza"] = "zenkizki(zuek)"
                if args["Nor"] == "haiek":
                    args["Aditza"] = "zekizki"

                args["Aditza"] = args["Aditza"] + ("(nori)")

            if args["Aditza"].startswith("zakizki(zuek)") or args["Aditza"].startswith("zenkizki(zuek)"):
                args["Aditza"] = args["Aditza"].replace("(zuek)", "")
                args["Aditza"] = args["Aditza"] + "te"
            args["Aditza"] = args["Aditza"] + "n"


        if args["Modua"] == "Agintera":
            if args["Nor"] == "hi":
                args["Aditza"] = "haki"
            if args["Nor"] == "hura":
                args["Aditza"] = "beki"
            if args["Nor"] == "zu":
                args["Aditza"] = "zakizki"
            if args["Nor"] == "zuek":
                args["Aditza"] = "zakizki(zuek)"
            if args["Nor"] == "haiek":
                args["Aditza"] = "bekizki"

            args["Aditza"] = args["Aditza"] + ("(nori)")
            
            if args["Aditza"].startswith("zakizki(zuek)"):
                args["Aditza"] = args["Aditza"].replace("(zuek)", "")
                args["Aditza"] = args["Aditza"] + "te"

        args["Aditza"] = nori(args)
            

    elif args["Kasua"] == "NOR-NORK":
        handler = open(path.join(path.dirname(__file__), "nk3.json"), "r")
        file = loads(handler.read())
        try:
            if args["Nor"] == "hura":
                Denbora = "Singularra"
            if args["Nor"] == "haiek":
                Denbora = "Plurala"
            args["Aditza"] = file[args["Modua"]][args["Denbora"]][Denbora][args["Nork"]]
            return args["Aditza"]
        except:
            args["Aditza"] = ""
            print("ERROR. NO EXISTE")
            
        if args["Denbora"] == "Oraina" and args["Modua"] != "Baldintzak" and args["Modua"] != "Ondorioa":
            if args["Nor"] == "ni":
                args["Aditza"] = "na"
            if args["Nor"] == "hi":
                args["Aditza"] = "ha"
            if args["Nor"] == "hura":
                if args["Modua"] == "Subjuntiboa":
                    args["Aditza"] = "de"
                else:
                    args["Aditza"] = "d"
            if args["Nor"] == "gu":
                args["Aditza"] = "gait"    
            if args["Nor"] == "zu":
                args["Aditza"] = "zait"
            if args["Nor"] == "zuek":
                if args["Modua"] == "Ahalera":
                    args["Aditza"] = "zait"
                else:    
                    args["Aditza"] = "zait(zuek)"
            if args["Nor"] == "haiek":
                args["Aditza"] = "dit"
        
        if args["Modua"] == "Baldintza":
            args["Aditza"] = "ba"
            if args["Denbora"] == "Iragana":
                raise ValueError("Incorrect value for Denbora: Denbora only takes Oraina when Modua is  = Baldintza. Read README.txt or the documentation at https://github.com/HCook86/Aditzak/blob/heroku/README.md for more information")
        
        if args["Denbora"] == "Iragana" or args["Modua"] == "Baldintza" or args["Modua"] == "Ondorioa":
            if args["Nor"] == "ni":
                if args["Modua"] == "Subjuntiboa":
                    args["Aditza"] = args["Aditza"] + "nint"
                else:
                    args["Aditza"] = args["Aditza"] + "nind"
            if args["Nor"] == "hi":
                args["Aditza"] = args["Aditza"] + "hind"
            if args["Nor"] == "gu":
                args["Aditza"] = args["Aditza"] + "gint"    
            if args["Nor"] == "zu":
                args["Aditza"] = args["Aditza"] + "zint"
            if args["Nor"] == "zuek":
                args["Aditza"] = args["Aditza"] + "zint(zuek)"

        if args["Modua"] == "Indikatiboa" or args["Modua"] == "Baldintza" or args["Modua"] == "Ondorioa":
            args["Aditza"] = args["Aditza"] + "u"
        if args["Modua"] == "Subjuntiboa" or args["Modua"] == "Ahalera":
            args["Aditza"] = args["Aditza"] + "za"

        has_zte = ["Indikatiboa", "Baldintza", "Ahalera", "Baldintza", "Ondorioa"]
        if "(zuek)" in args["Aditza"] and args["Modua"] in has_zte:
            args["Aditza"] = args["Aditza"].replace("(zuek)", "") + "zte"
        elif "(zuek)" in args["Aditza"]:
            args["Aditza"] = args["Aditza"].replace("(zuek)", "") + "te"

        if args["Modua"] == "Ondorioa" and (args["Nor"] == "gu" or args["Nor"] == "zu"):
            args["Aditza"] = args["Aditza"] + "z"

        if args["Modua"] == "Ondorioa" or args["Modua"] == "Ahalera":
            args["Aditza"] = args["Aditza"] + "ke"

        if args["Modua"] == "Ahalera" and args["Nor"] == "zuek":
            args["Aditza"] = args["Aditza"] + "te"

        args["Aditza"] = args["Aditza"] + "(nork)"
        args["Aditza"] = nork(args)


        if args["Modua"] == "Subjuntiboa" or args["Denbora"] == "Iragana":    
            if args["Aditza"].endswith("u") or args["Aditza"].endswith("e"):
                args["Aditza"] = args["Aditza"] + "en"
            else: 
                args["Aditza"] = args["Aditza"] + "n"
        
        if args["Modua"] == "Agintera":
            if args["Denbora"] == "Iragana":
                raise ValueError("Incorrect value for Denbora: Denbora only takes Oraina when Kasua is Agintera. Read README.txt or the documentation at https://github.com/HCook86/Aditzak/blob/heroku/README.md for more information")
            else:
                if args["Nor"] == "ni":
                    args["Aditza"] = "naza"
                if args["Nor"] == "hura":
                    args["Aditza"] = "beza"
                if args["Nor"] == "gu":
                    args["Aditza"] = "gaitza"    
                if args["Nor"] == "haiek":
                    args["Aditza"] = "bitza"


    elif args["Kasua"] == "NOR-NORI-NORK":
        if args["Nor"] != "singularra" and args["Nor"] != "plurala":
            raise ValueError("Incorrect value for Nor: Nor only takes singularra or plurala when Kasua is NOR-NORI-NORK. Read README.txt or the documentation at https://github.com/HCook86/Aditzak/blob/heroku/README.md for more information")
        if args["Modua"] == "Baldintza":
            if args["Denbora"] != "Oraina":
                raise ValueError("Incorrect value for Denbora: Denbora only takes Oraina when Modua is Baldintza. Read README.txt or the documentation at https://github.com/HCook86/Aditzak/blob/heroku/README.md for more information")
            args["Aditza"] = "ba"
        if args["Modua"] == "Agintera":
            args["Aditza"] = "ieza"
        else:
            if args["Denbora"] == "Oraina" and args["Modua"] != "Baldintza":
                args["Aditza"] = "di"
        
        if args["Denbora"] == "Iragana" or args["Denbora"] == "Hipotetikoa" or args["Modua"] == "Baldintza":
            if args["Nork"] == "nik":
                args["Aditza"] = args["Aditza"] + "ni"
            if args["Nork"] == "hik":
                args["Aditza"] = args["Aditza"] + "hi"
            if args["Nork"] == "hark":
                if args["Denbora"] == "Hipotetikoa":
                    args["Aditza"] = args["Aditza"] + "li"    
                else:
                    args["Aditza"] = args["Aditza"] + "zi"  
            if args["Nork"] == "guk":
                args["Aditza"] = args["Aditza"] + "geni"
            if args["Nork"] == "zuk":
                args["Aditza"] = args["Aditza"] + "zeni"
            if args["Nork"] == "zuek":
                args["Aditza"] = args["Aditza"] + "zeni(zuek)"
            if args["Nork"] == "haiek":
                if args["Denbora"] == "Hipotetikoa":
                    args["Aditza"] = args["Aditza"] + "li(haiek)"    
                else:
                    args["Aditza"] = args["Aditza"] + "zi(haiek)"    
        

        if args["Modua"] == "Subjuntiboa" or args["Modua"] == "Ahalera":
            
            args["Aditza"] = args["Aditza"] + "eza"
            
            if args["Nor"] == "plurala":
                args["Aditza"] = args["Aditza"] + "zki"
        else:
            if args["Nor"] == "plurala":
                args["Aditza"] = args["Aditza"] + "zki" 
        args["Aditza"] = args["Aditza"] + "(nori)"

        args["Aditza"] = nori(args)

        if args["Modua"] == "Ahalera":
            args["Aditza"] = args["Aditza"] + "ke"

        if args["Denbora"] == "Oraina" and args["Modua"] != "Baldintza" and args["Modua"] != "Ondorioa":
            args["Aditza"] = args["Aditza"] + "(nork)"
            args["Aditza"] = nork(args)

        if args["Modua"] == "Ondorioa":
            args["Aditza"] = args["Aditza"] + "ke"

        try:
            if "(zuek)" in args["Aditza"]:
                args["Aditza"] = args["Aditza"].replace("(zuek)", "") + "te"
            if "(haiek)" in args["Aditza"]:
                args["Aditza"] = args["Aditza"].replace("(haiek)", "") + "te"
        except: pass

        if args["Denbora"] == "Iragana" or args["Modua"] == "Subjuntiboa":
            if (args["Modua"] == "Ondorioa" or args["Modua"] == "Ahalera") and args["Aditza"].endswith("te") == False:
                args["Aditza"] = args["Aditza"] + "en"
            else:    
                args["Aditza"] = args["Aditza"] + "n"
    
    #If Kasua does not have a correct value
    else: raise ValueError('Incorrect value for Kasua. Read README.txt or the documentation at https://github.com/HCook86/Aditzak/blob/heroku/README.md for more information')
    return args["Aditza"]

#print(build({"Aditza":None, "Kasua":"NOR-NORK", "Modua":"Ahalera","Denbora":"Oraina", "Nor":"zuek", "Nori":None, "Nork":"hark"}))