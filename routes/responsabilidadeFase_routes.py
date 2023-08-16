from flask import Blueprint, jsonify, request
from functools import wraps
from models import ResponsabilidadeFase
import pandas as pd

ResponsabilidadeFase_routes = Blueprint('ResponsabilidadeFase_routes', __name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function
@ResponsabilidadeFase_routes.route('/pcp/api/ResponsabilidadeFase', methods=['GET'])
@token_required
def get_Usuarios():
    usuarios = ResponsabilidadeFase.ObterFaseResponsais()
    # Obtém os nomes das colunas
    # Obtém os nomes das colunas
    column_names = usuarios.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in usuarios.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data),200