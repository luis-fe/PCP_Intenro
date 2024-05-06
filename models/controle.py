### Esse arquivo contem as funcoes de salvar as utimas consulta no banco de dados do POSTGRE , com o
#objetivo especifico de controlar as requisicoes
import ConexaoPostgreMPL
from datetime import datetime
import pytz
import pandas as pd


# Funcao Para obter a Data e Hora
def obterHoraAtual():
    fuso_horario = pytz.timezone('America/Sao_Paulo')  # Define o fuso horário do Brasil
    agora = datetime.now(fuso_horario)
    agora = agora.strftime('%d/%m/%Y %H:%M:%S.%f')[:-3]
    return agora

def salvar(rotina, ip,datahoraInicio):
    datahorafinal = obterHoraAtual()

    # Converte as strings para objetos datetime
    data1_obj = datetime.strptime(datahoraInicio, "%d/%m/%Y %H:%M:%S.%f")
    data2_obj = datetime.strptime(datahorafinal,  "%d/%m/%Y %H:%M:%S.%f")

    # Calcula a diferença entre as datas
    diferenca = data1_obj - data2_obj

    # Obtém a diferença em dias como um número inteiro
    diferenca_em_dias = diferenca.days

    # Obtém a diferença total em segundos
    diferenca_total_segundos = diferenca.total_seconds()
    tempoProcessamento = float(diferenca_total_segundos)


    conn = ConexaoPostgreMPL.conexao2()

    consulta = 'insert into "Reposicao".configuracoes.controle_requisicao_csw (rotina, fim, inicio, ip_origem, "tempo_processamento(s)") ' \
          'values (%s , %s , %s , %s, %s )'

    cursor = conn.cursor()

    cursor.execute(consulta,(rotina,datahorafinal, datahoraInicio, ip, tempoProcessamento ))
    conn.commit()
    cursor.close()

    conn.close()

# Funcao que retorna a utima atualizacao
def UltimaAtualizacao(classe, dataInicial):

    conn = ConexaoPostgreMPL.conexao2()

    consulta = pd.read_sql('Select max(datahora_final) as ultimo from "Reposicao".automacao_csw.atualizacoes where classe = %s ', conn, params=(classe,))

    conn.close()

    datafinal = consulta['ultimo'][0]

    # Converte as strings para objetos datetime
    data1_obj = datetime.strptime(dataInicial, "%d/%m/%Y %H:%M:%S.%f")
    data2_obj = datetime.strptime(datafinal, "%d/%m/%Y %H:%M:%S.%f")

    # Calcula a diferença entre as datas
    diferenca = data1_obj - data2_obj

    # Obtém a diferença em dias como um número inteiro
    diferenca_em_dias = diferenca.days

    # Obtém a diferença total em segundos
    diferenca_total_segundos = diferenca.total_seconds()


    return float(diferenca_total_segundos)


def ExcluirHistorico(diasDesejados):
    conn = ConexaoPostgreMPL.conexao()

    deletar = "DELETE FROM pcp.controle_requisicao_csw crc " \
              "WHERE rotina = 'Portal Consulta OP' " \
              "AND ((SUBSTRING(fim, 7, 4)||'-'||SUBSTRING(fim, 4, 2)||'-'||SUBSTRING(fim, 1, 2))::date - now()::date) < -%s"

    cursor = conn.cursor()

    cursor.execute(deletar, (diasDesejados,))
    conn.commit()
    cursor.close()
    conn.close()


def TempoUltimaAtualizacao(dataHoraAtual, rotina):
    conn = ConexaoPostgreMPL.conexao2()

    consulta = pd.read_sql('select max(fim) as "ultimaData" from "Reposicao".configuracoes.controle_requisicao_csw crc '
                          "where rotina = %s ", conn, params=(rotina,) )



    conn.close()
    utimaAtualizacao = consulta['ultimaData'][0]
    if utimaAtualizacao != None:

        if len(utimaAtualizacao) < 23:
            print(utimaAtualizacao)
            utimaAtualizacao = utimaAtualizacao + '.001'
        else:
            utimaAtualizacao = utimaAtualizacao

    else:
        print('segue o baile')


    if utimaAtualizacao != None:

        # Converte as strings para objetos datetime
        data1_obj = datetime.strptime(dataHoraAtual, "%d/%m/%Y %H:%M:%S.%f")
        data2_obj = datetime.strptime(utimaAtualizacao, "%d/%m/%Y %H:%M:%S.%f")

        # Calcula a diferença entre as datas
        diferenca = data1_obj - data2_obj

        # Obtém a diferença em dias como um número inteiro
        diferenca_em_dias = diferenca.days

        # Obtém a diferença total em segundos
        diferenca_total_segundos = diferenca.total_seconds()

        return diferenca_total_segundos


    else:
        diferenca_total_segundos = 9999
        return diferenca_total_segundos

def TempoUltimaAtualizacaoPCP(dataHoraAtual, rotina):
    conn = ConexaoPostgreMPL.conexao()

    consulta = pd.read_sql('select max(fim) as "ultimaData" from "Reposicao".configuracoes.controle_requisicao_csw crc '
                          "where rotina = %s ", conn, params=(rotina,) )



    conn.close()
    utimaAtualizacao = consulta['ultimaData'][0]
    if utimaAtualizacao != None:

        if len(utimaAtualizacao) < 23:
            print(utimaAtualizacao)
            utimaAtualizacao = utimaAtualizacao + '.001'
        else:
            utimaAtualizacao = utimaAtualizacao

    else:
        print('segue o baile')


    if utimaAtualizacao != None:

        # Converte as strings para objetos datetime
        data1_obj = datetime.strptime(dataHoraAtual, "%d/%m/%Y %H:%M:%S.%f")
        data2_obj = datetime.strptime(utimaAtualizacao, "%d/%m/%Y %H:%M:%S.%f")

        # Calcula a diferença entre as datas
        diferenca = data1_obj - data2_obj

        # Obtém a diferença em dias como um número inteiro
        diferenca_em_dias = diferenca.days

        # Obtém a diferença total em segundos
        diferenca_total_segundos = diferenca.total_seconds()

        return diferenca_total_segundos


    else:
        diferenca_total_segundos = 9999
        return diferenca_total_segundos
def conversaoData(data):
    data1_obj = datetime.strptime(data, "%d/%m/%Y %H:%M:%S.%f")

    return data1_obj

def InserindoStatus(rotina, ip,datahoraInicio):
    datahorafinal = obterHoraAtual()

    # Converte as strings para objetos datetime
    data1_obj = datetime.strptime(datahoraInicio, "%d/%m/%Y %H:%M:%S.%f")
    data2_obj = datetime.strptime(datahorafinal,  "%d/%m/%Y %H:%M:%S.%f")

    # Calcula a diferença entre as datas
    diferenca = data1_obj - data2_obj

    # Obtém a diferença em dias como um número inteiro
    diferenca_em_dias = diferenca.days

    # Obtém a diferença total em segundos
    diferenca_total_segundos = diferenca.total_seconds()
    tempoProcessamento = float(diferenca_total_segundos)


    conn = ConexaoPostgreMPL.conexao2()

    consulta = 'insert into "Reposicao".configuracoes.controle_requisicao_csw (rotina, fim, inicio, ip_origem, status, "tempo_processamento(s)" )' \
          ' values (%s , %s , %s , %s, %s , %s )'

    cursor = conn.cursor()

    cursor.execute(consulta,(rotina,datahorafinal, datahoraInicio, ip,'em andamento', tempoProcessamento ))
    conn.commit()
    cursor.close()

    conn.close()

def salvarStatus(rotina, ip,datahoraInicio):
    datahorafinal = obterHoraAtual()

    # Converte as strings para objetos datetime
    data1_obj = datetime.strptime(datahoraInicio, "%d/%m/%Y %H:%M:%S.%f")
    data2_obj = datetime.strptime(datahorafinal,  "%d/%m/%Y %H:%M:%S.%f")

    # Calcula a diferença entre as datas
    diferenca = data1_obj - data2_obj

    # Obtém a diferença em dias como um número inteiro
    diferenca_em_dias = diferenca.days

    # Obtém a diferença total em segundos
    diferenca_total_segundos = diferenca.total_seconds()
    tempoProcessamento = float(diferenca_total_segundos)


    conn = ConexaoPostgreMPL.conexao2()

    consulta = 'update "Reposicao".configuracoes.controle_requisicao_csw set fim = %s, "tempo_processamento(s)" = %s , status = %s' \
               ' where  rotina = %s and inicio = %s and ip_origem = %s '

    cursor = conn.cursor()

    cursor.execute(consulta,(datahorafinal, tempoProcessamento,'concluido',rotina,datahoraInicio, ip,  ))
    conn.commit()
    cursor.close()

    conn.close()

def distinctStatus(rotina):
    conn = ConexaoPostgreMPL.conexao2()
    consulta = pd.read_sql('select distinct status from "Reposicao".configuracoes.controle_requisicao_csw'
               ' where rotina = %s ',conn,params=(rotina,))


    conn.close()

    if not consulta.empty:
        return 'em andamento'
    else:
        return 'nao iniciado'
def salvarStatus_porEtapas(rotina, ip,datahoraInicio,etapa,netapa):
    datahorafinal = obterHoraAtual()

    # Converte as strings para objetos datetime
    data1_obj = datetime.strptime(datahoraInicio, "%d/%m/%Y %H:%M:%S.%f")
    data2_obj = datetime.strptime(datahorafinal,  "%d/%m/%Y %H:%M:%S.%f")

    # Calcula a diferença entre as datas
    diferenca = data1_obj - data2_obj

    # Obtém a diferença total em segundos
    diferenca_total_segundos = diferenca.total_seconds()
    tempoProcessamento = float(diferenca_total_segundos)


    conn = ConexaoPostgreMPL.conexao2()

    etapaUsar = str(netapa)
    etapaRegistro = f'"etapa{etapaUsar}"'
    etapaTempo = f'"etapa{etapaUsar}_tempo"'


    consulta = f'update "Reposicao".configuracoes.controle_requisicao_csw set {etapaRegistro} = %s, {etapaTempo} = %s , "tempo_processamento(s)" = %s ' \
               " where  rotina = %s  and ip_origem = %s and status = 'em andamento' "
    cursor = conn.cursor()

    cursor.execute(consulta,(etapa, tempoProcessamento,tempoProcessamento,rotina, ip,  ))
    conn.commit()
    cursor.close()

    conn.close()

    return datahorafinal


def salvarStatus_Etapa1(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip,datahoraInicio,etapa,1)
    return etapa
def salvarStatus_Etapa2(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip,datahoraInicio,etapa,2)
    return etapa
def salvarStatus_Etapa3(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip,datahoraInicio,etapa,3)
    return etapa
def salvarStatus_Etapa4(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip,datahoraInicio,etapa,4)
    return etapa
def salvarStatus_Etapa5(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip,datahoraInicio,etapa,5)
    return etapa
def salvarStatus_Etapa6(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip,datahoraInicio,etapa,6)
    return etapa
def salvarStatus_Etapa7(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip,datahoraInicio,etapa,7)
    return etapa
def salvarStatus_Etapa8(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 8)
    return etapa
def salvarStatus_Etapa9(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 9)
    return etapa
def salvarStatus_Etapa10(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 10)
    return etapa
def salvarStatus_Etapa11(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 11)
    return etapa
def salvarStatus_Etapa12(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 12)
    return etapa
def salvarStatus_Etapa13(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 13)
    return etapa
def salvarStatus_Etapa14(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 14)
    return etapa
def salvarStatus_Etapa15(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 15)
    return etapa
def salvarStatus_Etapa16(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 16)
    return etapa
def salvarStatus_Etapa17(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 17)
    return etapa
def salvarStatus_Etapa18(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 18)
    return etapa
def salvarStatus_Etapa19(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 19)
    return etapa
def salvarStatus_Etapa20(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 20)
    return etapa

def salvarStatus_Etapa21(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 21)
    return etapa
def salvarStatus_Etapa22(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 22)
    return etapa
def salvarStatus_Etapa23(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 23)
    return etapa
def salvarStatus_Etapa24(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 24)
    return etapa
def salvarStatus_Etapa25(rotina, ip,datahoraInicio,etapa):
    etapa = salvarStatus_porEtapas(rotina, ip, datahoraInicio, etapa, 25)
    return etapa

