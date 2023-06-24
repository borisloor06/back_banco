from flask import Flask, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
app = Flask(__name__)

mongo_hosts = [
    os.getenv('HOST1'),
    os.getenv('HOST2'),
    os.getenv('HOST3'),
    os.getenv('HOST4'),
    os.getenv('HOST5')
]

# Datos de autenticación
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

# Configuración de la conexión a MongoDB
MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION')

client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[MONGODB_DATABASE]
collection = db[MONGODB_COLLECTION]

# Rutas de la API
@app.route('/accounts', methods=['GET'])
def get_accounts():
    # Obtiene la lista de cuentas
    accounts = list(collection.find({}, {'_id': 0}))
    return jsonify(accounts)

@app.route('/accounts', methods=['POST'])
def create_account():
    # Crea una nueva cuenta
    data = request.get_json()
    account = {
        'user': data['user'],
        'balance': data['balance']
    }
    collection.insert_one(account)
    return jsonify(account), 201

@app.route('/accounts/<user>', methods=['GET'])
def get_account(user):
    # Obtiene los detalles de una cuenta específica
    account = collection.find_one({'user': user}, {'_id': 0})
    if account:
        return jsonify(account)
    else:
        return jsonify({'error': 'Cuenta no encontrada'}), 404

@app.route('/accounts/<user>/deposit', methods=['PUT'])
def deposit(user):
    # Realiza un depósito en una cuenta
    data = request.get_json()
    amount = data['amount']
    account = collection.find_one({'user': user})
    if account:
        new_balance = account['balance'] + amount
        collection.update_one({'user': user}, {'$set': {'balance': new_balance}})
        return jsonify({'message': 'Depósito realizado'})
    else:
        return jsonify({'error': 'Cuenta no encontrada'}), 404

@app.route('/accounts/<user>/withdraw', methods=['PUT'])
def withdraw(user):
    # Realiza un retiro de una cuenta
    data = request.get_json()
    amount = data['amount']
    account = collection.find_one({'user': user})
    if account:
        if account['balance'] >= amount:
            new_balance = account['balance'] - amount
            collection.update_one({'user': user}, {'$set': {'balance': new_balance}})
            return jsonify({'message': 'Retiro realizado'})
        else:
            return jsonify({'error': 'Saldo insuficiente'}), 400
    else:
        return jsonify({'error': 'Cuenta no encontrada'}), 404

# Ejecución de la aplicación
if __name__ == '__main__':
    app.run()