import pymongo


conn = pymongo.MongoClient("mongodb://localhost:27017")

#Accessing the DB
mydb = conn['Data_Catalog']


def BD(name):
    mycol = mydb["Bases_de_données"]
    for x in mycol.find({"Nom de la BD" : name}) :
        for k,v in x.items() :
            if k == "_id" :
                continue
            else:
                print(k," : ", v )


def Table(name):
    mycol = mydb["Tables"]
    for x in mycol.find({"Nom" : name}) :
        for k,v in x.items() :
            if k == "_id" :
                continue
            elif k=="Champs":
                for i in v :
                    print(i)
            else:
                print(k," : ", v )



def Champs(name,table):
    mycol = mydb["Tables"]
    for x in mycol.find({"Nom" : table}) :
        for k,v in x.items() :
            if k == "Champs" :
                for i in v :          
                    for c,t in i.items() :
                        if t==name and c=="nom_champs":
                            for p,w in i.items():
                                print(p, ' : ',w)  
            else:
                continue

    
    
    
def source_BD(name):
    mycol = mydb["Bases_de_données"]
    for x in mycol.find({"Nom de la BD" : name}) :
        for k,v in x.items() :
            if k != "Source" :
                continue
            else:
                print(k," : ", v )
                
                
def frequence_BD(name):
    mycol = mydb["Bases_de_données"]
    for x in mycol.find({"Nom de la BD" : name}) :
        for k,v in x.items() :
            if k != "Fréquence d'alimentation" :
                continue
            else:
                print(k," : ", v )
                
                
def LastAlimentationDate(table):
    mycol = mydb["Tables"]
    for x in mycol.find({"Nom" : table}) :
        for k,v in x.items() :
            if k == "Date de la dernière alimentation" :
                print(k," : ", v )
            else:
                continue
            
            
def toJoin(champ,table):
    mycol = mydb["Tables"]
    for x in mycol.find({"Nom" : table}) :
        for k,v in x.items() :
            if k == "Champs" :
                for i in v :          
                    for c,t in i.items() :
                        if t==champ and c=="nom_champs":
                            for p,w in i.items():
                                if p == "toJoin":
                                    print(p, ' : ',w)  
            else:
                continue