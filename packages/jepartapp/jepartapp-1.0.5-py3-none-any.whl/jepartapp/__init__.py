from os import system,getcwd,listdir
from json import load,dumps
from time import sleep



__version__ = '1.0.5'
class AlegriaDeBrincar:
    def __init__(self):
        self.c = {}
        self.packed = ["firebirdsql", "requests","mysql-connector-python"]
        
        print("\nChecando atualizanção do APP")
        AlegriaDeBrincar.configAPP(self)
        AlegriaDeBrincar.checkVersion(self)
        print("Inicializando")
        AlegriaDeBrincar.startPacked(self)
        while True:
            AlegriaDeBrincar.checkVersion(self)
            print("\nChecando atualização dos modulos")
            print("Enviando Vendas")
            AlegriaDeBrincar.insertSell(self)
            print("Enviando Dia")
            AlegriaDeBrincar.insertDay(self)
            print("Checando produtos")
            AlegriaDeBrincar.insertProduto(self)
            AlegriaDeBrincar.insertStatus(self)
            print("Aguardando proxima rodada")
            sleep(self.c["check"])

    def startPacked(self):
        for i in self.packed:
            system('pip install '+i+' --upgrade')

    def checkVersion(self):
        import requests
        headersList = {"Accept": "*/*",}
        response = requests.request("GET", 'https://api.jepart.online/version',headers=headersList)
        if response.text != __version__:
            print("APP desatualizado")
            system('pip install jepartapp --upgrade')
            return False
    def configAPP(self):
        check = listdir(getcwd())
        if "config.json" not in check:
            json = '{ "idLoja": 0, "cacheDay": 0,"check": 1, "firebird": { "dbLoja": "", "dbUser": "", "dbPass": "" }, "mysql": { "sqlIp": "", "sqluser": "", "sqlPass": "", "sqlDb": "" } }'
            AlegriaDeBrincar.updateConfig(self,json)
            AlegriaDeBrincar.startPacked(self)
        c = load(open("{}/config.json".format(getcwd()), 'r'))
        if c["idLoja"] == 0:
            print("--Primeira configuração--")
            value = input("Digite o ID da loja:")
            c["idLoja"] = int(value)
            value = input("Tempo em dias para puxar vendas:")
            c["cacheDay"] = int(value)
            print("\n--Configurar Banco de dados do programa da loja--")
            value = input("Local do arquivo FDB:")
            c["firebird"]["dbLoja"] = value
            value = input("Usuario do banco de dados:")
            c["firebird"]["dbUser"] = value
            value = input("Senha do banco de dados:")
            c["firebird"]["dbPass"] = value
            print("\n--Configurar Banco de dados Online--")
            value = input("Ip do servidor MYSQL:")
            c["mysql"]["sqlIp"] = value
            value = input("Usuario do servidor MYSQL:")
            c["mysql"]["sqluser"] = value
            value = input("Senha do servidor MYSQL:")
            c["mysql"]["sqlPass"] = value
            value = input("Banco do servidor MYSQL:")
            c["mysql"]["sqlDb"] = value
            AlegriaDeBrincar.updateConfig(self,dumps(c))
            print("Fim da Configuração!")

        self.c = load(open("{}/config.json".format(getcwd()), 'r'))
        
        pass
    
    def updateConfig(self,string):
        jsonFile = open("{}/config.json".format(getcwd()), 'w+')
        jsonFile.writelines(string)
        jsonFile.close()

    def selectFDB(self,string):
        import firebirdsql
        db = self.c["firebird"]
        con = firebirdsql.connect(database=db["dbLoja"], user=db["dbUser"], password= db["dbPass"])
        cur = con.cursor()
        cur.execute(string)
        result = cur.fetchall()
        return result

    def getLastDataInsert(self,db):
        import mysql.connector
        myDb = self.c["mysql"]
        string = "select data FROM {} WHERE loja = {} order by data DESC limit 1 ".format(db,self.c["idLoja"])
        mydb = mysql.connector.connect(
            host=myDb["sqlIp"],
            user= myDb["sqluser"],
            password= myDb["sqlPass"],
            database=myDb["sqlDb"],
            port=3306
            )
        mycursor = mydb.cursor()
        mycursor.execute(string)
        for (data) in mycursor:
            return data[0]

    def connectDB(self):
        import mysql.connector
        myDb = self.c["mysql"]
        result = mysql.connector.connect(
        host=myDb["sqlIp"],
        user= myDb["sqluser"],
        password= myDb["sqlPass"],
        database=myDb["sqlDb"],
        port=3306
        )
        return result

    def insertDB(self,string):
        sql =  AlegriaDeBrincar.connectDB(self)
        mycursor = sql.cursor()
        mycursor.execute(string)
        sql.commit()
        sql.close()

    def insertSell(self):
        string = "SELECT TV.DATAEHORACADASTRO,TV.CONTROLE,TV.NUMERONFCCE,TP.CODESPECIE,cast((replace(TP.VALORPAGOVARCHAR,',','.')) as float) as total FROM TVENDANFCE AS TV INNER JOIN TFORMAPAGAMENTONFCE AS TP on TP.CODNFCE = TV.NUMERONFCCE WHERE TV.DATAEHORACADASTRO > '" + str(AlegriaDeBrincar.getLastDataInsert(self,"vendas")) + "' and TV.DATAEHORACADASTRO >= dateadd (-"+ str(self.c["cacheDay"])+" day to current_date) and TP.VALORPAGOVARCHAR <> '0,00'"
        
        result = AlegriaDeBrincar.selectFDB(self,string)

        while len(result) > 0:
            sql = "REPLACE INTO vendas(loja,data,ticket,nfc,credito,debito) VALUES "
            stringSession = ""
            count = 1
            for i in result:
                if len(stringSession) > 1:
                    stringSession += ','
                debito = "0.00"
                credito = "0.00"
                if i[3] == 3 or i[3] == 8:
                    credito = i[4]
                    credito = round(credito,2)
                elif i[3] == 9:
                    debito = i[4]
                    debito = round(debito,2)

                stringSession += '({},"{}",{},{},{},{})'.format(self.c["idLoja"],i[0],i[1],i[2],credito,debito)
                result.remove(i)
                count += 1
                if count == 20:
                    break
            AlegriaDeBrincar.insertDB(self,sql+stringSession)
            if len(result) == 0:
                break
    def insertStatus(self):
        string = "UPDATE `lojas` SET `status` = now() WHERE `id` = {}".format(self.c["idLoja"])
        AlegriaDeBrincar.insertDB(self,string)

    def insertDay(self):
        string = "SELECT cast(TV.DATAEHORACADASTRO as date),TP.CODESPECIE,cast((replace(TP.VALORPAGOVARCHAR,',','.')) as float) as total FROM TVENDANFCE AS TV INNER JOIN TFORMAPAGAMENTONFCE AS TP on TP.CODNFCE = TV.NUMERONFCCE WHERE cast(TV.DATAEHORACADASTRO as date) < cast('Now' as date) AND cast(TV.DATAEHORACADASTRO as date) >= '" + str(AlegriaDeBrincar.getLastDataInsert(self,"vendas_mes")) + "'"
        
        result = AlegriaDeBrincar.selectFDB(self,string)
        
        temp = {}
        for i in result:
            dataTemp = str(i[0])
            if dataTemp not in temp:
                temp[dataTemp] = {"data":dataTemp,"credito":0.00,"debito":0.00}
            if i[1] == 3 or i[1] == 8:
                temp[dataTemp]["credito"] += i[2]
            elif i[1] == 9:
                temp[dataTemp]["debito"] += i[2]
            temp[dataTemp]["credito"] = round(temp[dataTemp]["credito"],2)
            temp[dataTemp]["debito"] = round(temp[dataTemp]["debito"],2)
        stringInsert = ""
        count = 0
        print(temp)
        sql = "REPLACE INTO vendas_mes(loja,data,credito,debito) VALUES "
        
        for i in temp:
            if count > 0:
                stringInsert += ","
            t = temp[i]
            stringInsert += '({},"{}",{},{})'.format(self.c["idLoja"],t["data"],t["credito"],t["debito"])
            count += 1
            if count == 2 or i == len(temp)-1:
                AlegriaDeBrincar.insertDB(self,sql+stringInsert)
                
                stringInsert = ""
                count = 0

    def insertProduto(self):
        string = "select CONTROLE,produto,precocusto,precovenda,QTDE from TESTOQUE WHERE ATIVO = 'sim'"
        result = AlegriaDeBrincar.selectFDB(self,string)
        temp = {}
        print("Coletando informações")
        for i in result:
            temp[i[0]] = {"sku":i[0],"nome":i[1],"custo":i[2],"venda":i[3],"estoque":i[4]}
        print("Baixando informações")
        conLoja = "LOJA_"+str(self.c["idLoja"])
        conValor = "VALOR_"+str(self.c["idLoja"])
        sql = "SELECT PR.SKU,PR.NOME,PR.CUSTO,PE.{},PV.{} FROM produtos AS PR INNER JOIN produto_estoque as PE ON PE.SKU = PR.SKU AND PE.NOME = PR.NOME INNER JOIN produto_valor as PV ON PV.SKU = PR.SKU AND PV.NOME = PR.NOME".format(conLoja,conValor)
        con = AlegriaDeBrincar.connectDB(self)
        cursor = con.cursor(self)
        cursor.execute(sql)
        result =  cursor
        
        dbOnline = {}
        for (sku, nome, custo,conLoja,conValor) in result:
            dbOnline[sku] = {"sku":sku,"nome":nome,"custo":custo,"venda":conValor,"estoque":conLoja}

        custoP = {}
        valorP = {}
        estoqueP = {}
        custoIN = {}
        valorIN = {}
        estoqueIN = {}
        for t in temp:
            dT = temp[t]
            if t in dbOnline:
                dO = dbOnline[t]
                if round(dT['custo'],2) != dO['custo']:
                    custoP[len(custoP)] ={"sku":dT['sku'],"nome":dT['nome'],"update":dT['custo']}
                if round(dT['venda'],2) != dO['venda']:
                    valorP[len(valorP)] ={"sku":dT['sku'],"nome":dT['nome'],"update":dT['venda']}
                if round(dT['estoque'],2) != dO['estoque']:
                    estoqueP[len(estoqueP)] ={"sku":dT['sku'],"nome":dT['nome'],"update":dT['estoque']}
                next
            else:
                custoIN[len(custoIN)+1] = {"sku":dT['sku'],"nome":dT['nome'],"insert":dT['custo']}
                valorIN[len(valorIN)+1] = {"sku":dT['sku'],"nome":dT['nome'],"insert":dT['venda']}
                estoqueIN[len(estoqueIN)+1] = {"sku":dT['sku'],"nome":dT['nome'],"insert":dT['estoque']}
        # INSERT
        envio = 75
        count = 0
        percent = 0
        sql = "REPLACE INTO produtos(sku,nome,custo) VALUES "
        stringInsert = ""
        for c in custoIN:
            t = custoIN[c]
            if count > 0:
                stringInsert += ","
            stringInsert += '({},"{}",{})'.format(t["sku"],t["nome"],t["insert"])
            count += 1
            if count == envio or c == len(custoIN):
                percent += count
                print("Enviando {} de {}".format(percent,len(custoIN)))
                AlegriaDeBrincar.insertDB(self,sql+stringInsert)
                count = 0
                stringInsert = ""            

        count = 0
        percent = 0
        sql = "REPLACE INTO produto_valor(sku,nome,valor_"+str(self.c["idLoja"])+") VALUES "
        stringInsert = ""
        for v in valorIN:
            t = valorIN[v]
            if count > 0:
                stringInsert += ","
            stringInsert += '("{}","{}",{})'.format(t["sku"],t["nome"],t["insert"])
            count += 1
            if count == envio or v == len(valorIN):
                percent += count
                print("Enviando {} de {}".format(percent,len(valorIN)))
                AlegriaDeBrincar.insertDB(self,sql+stringInsert)
                count = 0
                stringInsert = ""            

        count = 0
        percent = 0
        sql = "REPLACE INTO produto_estoque(sku,nome,loja_"+str(self.c["idLoja"])+") VALUES "
        stringInsert = ""
        for e in estoqueIN:
            t = estoqueIN[e]
            if count > 0:
                stringInsert += ","
            stringInsert += '("{}","{}",{})'.format(t["sku"],t["nome"],t["insert"])
            count += 1
            if count == envio or e == len(estoqueIN):
                percent += count
                print("Enviando {} de {}".format(percent,len(estoqueIN)))
                AlegriaDeBrincar.insertDB(self,sql+stringInsert)
                count = 0
                stringInsert = ""            


        # UPDATE
        for c in custoP:
            t = custoP[c]
            sql = "INSERT INTO produtos(sku,nome,custo) VALUES "
            stringInsert = '("{}","{}",{})'.format(t["sku"],t["nome"],t["update"])
            stringInsert += ' ON DUPLICATE KEY UPDATE custo = ' +  str(t["update"])
            AlegriaDeBrincar.insertDB(self,sql+stringInsert)
        for v in valorP:
            t = valorP[v]
            sql = "INSERT INTO produto_valor(sku,nome,valor_"+str(self.c["idLoja"])+") VALUES "
            stringInsert = '("{}","{}",{})'.format(t["sku"],t["nome"],t["update"])
            stringInsert += ' ON DUPLICATE KEY UPDATE valor_'+str(self.c["idLoja"])+' = ' +  str(t["update"])
            AlegriaDeBrincar.insertDB(self,sql+stringInsert)
        for e in estoqueP:
            t = estoqueP[e]
            sql = "INSERT INTO produto_estoque(sku,nome,loja_"+str(self.c["idLoja"])+") VALUES "
            stringInsert = '("{}","{}",{})'.format(t["sku"],t["nome"],t["update"])
            stringInsert += ' ON DUPLICATE KEY UPDATE loja_'+str(self.c["idLoja"])+' = ' +  str(t["update"])
            AlegriaDeBrincar.insertDB(self,sql+stringInsert)

