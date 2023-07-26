import math

import pandas as pd
import ConexaoCSW

def GetColecoes(pagina, itensPag):
    conn = ConexaoCSW.Conexao()

    contagem = pd.read_sql("select COUNT(c.codcolecao) as cont from tcp.Colecoes c WHERE c.codEmpresa = 1 ", conn)

    totalPgs = contagem['cont'][0] /itensPag
    totalPgs = math.ceil(totalPgs)
    totalPgs = int(totalPgs)

    data = pd.read_sql("select codColecao , nome  from tcp.Colecoes c WHERE c.codEmpresa = 1 ",conn)
    conn.close()
    final = pagina * itensPag
    inicial = (pagina - 1) * itensPag

    data = data.iloc[inicial:final]

    data = {
        '0- Numerero de Paginas':totalPgs,
        '1- Detalhamento da Consulta:': data.to_dict(orient='records')
    }
    print('novo')
    return [data]

