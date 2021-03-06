#!/usr/bin/python3

import decimal
import datetime
import mysql.connector
import pymongo

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
mongoDb = mongoClient["AlojamentoLocal"]

db = mysql.connector.connect(
    host = "localhost",
    user = "universidade",
    password  = "universidade",
    database = "AlojamentoLocal"
)

def migracao(tabela, atributos):
    cursor = db.cursor()
    cursor.execute(f"select * from {tabela}")
    res = []
    for row in cursor:
        print(row)
        obj = []
        for i in range(len(row)):
            if isinstance(row[i], decimal.Decimal):
                obj.append(float(row[i]))
            elif isinstance(row[i], datetime.date):
                obj.append(datetime.datetime(row[i].year, row[i].month, row[i].day))
            else:
                obj.append(row[i])
        res.append(tuple(obj))

    lista = []
    for el in res:
        lista.append({})
        for i in range(len(el)):
            lista[-1][atributos[i]] = el[i]
    return lista

##################################
# Edificio
##################################

atributos = ["_id", "Rua/Morada", "Localidade/Morada", "Codigo_Postal/Morada"]

edificio = migracao("Edificio", atributos)
mongoColection = mongoDb["Edificio"]
mongoColection.drop()
x = mongoColection.insert_many(edificio)
print("Coleção Edificio criada.")

##################################
# Alojamento
##################################

atributos = ["_id", "Numero", "Edificio", "Preco_Base", "Lotacao", "Numero_Quartos"]

alojamento = migracao("Alojamento", atributos)

##################################
# Funcionario
##################################

atributos = ["_id", "Nome", "Telemovel", "E-mail", "Salario", "Gerente"]

funcionario = migracao("Funcionario", atributos)
mongoColection = mongoDb["Funcionario"]
mongoColection.drop()
x = mongoColection.insert_many(funcionario)
print("Coleção Funcionario criada.")

##################################
# Cliente
##################################

atributos = ["_id", "Nome", "Data_Nascimento", "E-mail", "Telemovel"]

cliente = migracao("Cliente", atributos)
mongoColection = mongoDb["Cliente"]
mongoColection.drop()
x = mongoColection.insert_many(cliente)
print("Coleção Cliente criada.")

##################################
# Reserva
##################################

atributos = ["_id", "Funcionario", "Cliente", "Data_Inicio", "Data_Fim", "Adultos", "Criancas"]

reservas = migracao("Reserva", atributos)

##################################
# Reserva_Alojamento
##################################

atributos = ["Reserva", "Alojamento", "Preco"]

reserva_alojamento = migracao("Reserva_Alojamento", atributos)

##################################
# Adicionar relação Reserva/Alojamento
##################################

for x in reserva_alojamento:
    id_reserva = x["Reserva"]
    id_alojamento = x["Alojamento"]
    preco = x["Preco"]

    for reserva in filter(lambda e: e["_id"] == id_reserva, reservas):
        if "Alojamentos" not in reserva:
            reserva["Alojamentos"] = []
        reserva["Alojamentos"].append({"Alojamento": id_alojamento, "Preco": preco})

    for aloj in filter(lambda e: e["_id"] == id_alojamento, alojamento):
        if "Reservas" not in aloj:
            aloj["Reservas"] = []
        aloj["Reservas"].append({"Reserva": id_reserva, "Preco": preco})

mongoColection = mongoDb["Alojamento"]
mongoColection.drop()
x = mongoColection.insert_many(alojamento)
print("Coleção Alojamento criada.")

mongoColection = mongoDb["Reserva"]
mongoColection.drop()
x = mongoColection.insert_many(reservas)
print("Coleção Reserva criada.")

'''
Sugestão:

- Adicionar Alojamento à coleção de edificios (embedded)

'''