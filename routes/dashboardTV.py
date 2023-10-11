from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
from models import dashbordTVModel
import pandas as pd

dashboardTVroute = Blueprint('dashboardTVroute', __name__)
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function

@dashboardTVroute.route('/pcp/api/dashboarTV', methods=['GET'])
@token_required
def dashboarTV():
    ano = request.args.get('ano','2023')
    empresa = request.args.get('empresa', '1')

    usuarios = dashbordTVModel.Faturamento_ano(ano,empresa)



    # Obtém os nomes das colunas
    column_names = usuarios.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in usuarios.iterrows():
        op_dict = {}
        for index, row in usuarios.iterrows():
            op_dict = {}
            for column_name in column_names:
                op_dict[column_name] = row[column_name]
            OP_data.append(op_dict)
        return jsonify(OP_data)