import pandas as pd
from conexoesDAO import ConexaoPostgreMPL


def Get_Consultar(plano):
    conn = ConexaoPostgreMPL.conexao()
    get = pd.read_sql('select plano, marca, "MetaR$", "Metapç" from pcp."planoMetas" '
                      'where plano = %s ',conn,params=(plano,))

    return get


def InserirMeta(plano):
    conn = ConexaoPostgreMPL.conexao()


def EditarMeta(plano):
    conn = ConexaoPostgreMPL.conexao()



