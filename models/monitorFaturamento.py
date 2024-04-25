import pandas as pd
import BuscasAvancadas
import ConexaoCSW
import ConexaoPostgreMPL
import datetime
import numpy
import locale
from models import controle
import pytz
import fastparquet as fp
def obterHoraAtual():
    fuso_horario = pytz.timezone('America/Sao_Paulo')  # Define o fuso horário do Brasil
    agora = datetime.datetime.now(fuso_horario)
    agora = agora.strftime('%d/%m/%Y')
    return agora


#Carregando a Capa de pedidos do CSW : BuscasAvancadas.CapaPedido (empresa, iniVenda, finalVenda, tiponota):
def Monitor_CapaPedidos(empresa, iniVenda, finalVenda, tiponota):
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.CapaPedido(empresa, iniVenda, finalVenda, tiponota), conn)

    conn.close()
    return consulta

def Monitor_CapaPedidosDataPrev(empresa, iniVenda, finalVenda, tiponota):
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.CapaPedidoPelaDataPrevOriginal(empresa, iniVenda, finalVenda, tiponota), conn)

    conn.close()
    return consulta

# Verfiicando se o pedido nao está bloqueado :
def Monitor_PedidosBloqueados():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.SituacaoPedidos(), conn)

    conn.close()
    return consulta


#Carregando os Pedidos a nivel Sku
def Monitor_nivelSku(datainicio):
    # Carregar o arquivo Parquet
    parquet_file = fp.ParquetFile('/home/grupompl/Automacao_WMS_InternoMPL/pedidos.parquet')

    # Converter para DataFrame do Pandas
    df_loaded = parquet_file.to_pandas()

    df_loaded['dataEmissao']= pd.to_datetime(df_loaded['dataEmissao'],errors='coerce', infer_datetime_format=True)
    teste = datainicio
    df_loaded['filtro'] = df_loaded['dataEmissao'] >= teste
    df_loaded = df_loaded[df_loaded['filtro']==True].reset_index()
    df_loaded = df_loaded.loc[:, ['codPedido', 'codProduto', 'qtdePedida', 'qtdeFaturada', 'qtdeCancelada','qtdeSugerida',#'StatusSugestao',
                                   'PrecoLiquido']]
    #consultar = consultar.rename(columns={'StatusSugestao': 'Sugestao(Pedido)'})

    df_loaded['qtdeSugerida'] = pd.to_numeric(df_loaded['qtdeSugerida'], errors='coerce').fillna(0)
    df_loaded['qtdePedida'] = pd.to_numeric(df_loaded['qtdePedida'], errors='coerce').fillna(0)
    df_loaded['qtdeFaturada'] = pd.to_numeric(df_loaded['qtdeFaturada'], errors='coerce').fillna(0)
    df_loaded['qtdeCancelada'] = pd.to_numeric(df_loaded['qtdeCancelada'], errors='coerce').fillna(0)


    return df_loaded

def Monitor_nivelSkuPrev(datainicio):
    # Carregar o arquivo Parquet
    parquet_file = fp.ParquetFile('/home/grupompl/Automacao_WMS_InternoMPL/pedidos.parquet')

    # Converter para DataFrame do Pandas
    df_loaded = parquet_file.to_pandas()

    df_loaded['dataPrevFat']= pd.to_datetime(df_loaded['dataPrevFat'],errors='coerce', infer_datetime_format=True)
    teste = datainicio
    df_loaded['filtro'] = df_loaded['dataPrevFat'] >= teste
    df_loaded = df_loaded[df_loaded['filtro']==True].reset_index()
    df_loaded = df_loaded.loc[:, ['codPedido', 'codProduto', 'qtdePedida', 'qtdeFaturada', 'qtdeCancelada','qtdeSugerida',#'StatusSugestao',
                                   'PrecoLiquido']]
    #consultar = consultar.rename(columns={'StatusSugestao': 'Sugestao(Pedido)'})

    df_loaded['qtdeSugerida'] = pd.to_numeric(df_loaded['qtdeSugerida'], errors='coerce').fillna(0)
    df_loaded['qtdePedida'] = pd.to_numeric(df_loaded['qtdePedida'], errors='coerce').fillna(0)
    df_loaded['qtdeFaturada'] = pd.to_numeric(df_loaded['qtdeFaturada'], errors='coerce').fillna(0)
    df_loaded['qtdeCancelada'] = pd.to_numeric(df_loaded['qtdeCancelada'], errors='coerce').fillna(0)


    return df_loaded

#EstoquePorSku
def EstoqueSKU():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.ConsultaEstoque(), conn)

    conn.close()
    return consulta

#ObtendoEntregasSolicitadas
def ObtendoEntregasSolicitadas():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.ObtendoEmbarqueUnico(), conn)

    conn.close()
    return consulta


#Entregas_Enviados
def ObtendoEntregas_Enviados():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.Entregas_Enviados(), conn)

    conn.close()

    return consulta

#Obtendo os Sku - estrutura
def EstruturaSku():
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql("""Select "codSKU" as "codProduto", "codItemPai", "codCor", "nomeSKU" from pcp."SKU" """,conn)

    conn.close()

    return consultar

def CapaSugestao():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.CapaSugestaoSituacao(), conn)

    conn.close()

    return consulta


def MonitorDePreFaturamento(empresa, iniVenda, finalVenda, tiponota,rotina, ip, datainicio,parametroClassificacao, tipoData):
    # 1 - Carregar Os pedidos (etapa 1)
    if tipoData == 'DataEmissao':
        pedidos = Monitor_CapaPedidos(empresa, iniVenda, finalVenda, tiponota)
    else:
        pedidos = Monitor_CapaPedidosDataPrev(empresa, iniVenda, finalVenda, tiponota)

    statusSugestao = CapaSugestao()
    pedidos = pd.merge(pedidos,statusSugestao,on='codPedido',how='left')
    pedidos["StatusSugestao"].fillna('Nao Sugerido', inplace=True)
    pedidos["codSitSituacao"].fillna('0', inplace=True)
    etapa1 = controle.salvarStatus_Etapa1(rotina, ip, datainicio, 'Carregar Os pedidos ') #Registrar etapa no controlador


    # 2 - Filtrar Apenas Pedidos Não Bloqueados
    pedidosBloqueados = Monitor_PedidosBloqueados()
    pedidos = pd.merge(pedidos,pedidosBloqueados,on='codPedido',how='left')
    pedidos['situacaobloq'].fillna('Liberado',inplace=True)
    pedidos = pedidos[pedidos['situacaobloq'] == 'Liberado']
    etapa2 = controle.salvarStatus_Etapa2(rotina, ip, etapa1, ' Filtrar Apenas Pedidos Não Bloqueados') #Registrar etapa no controlador


    # 3- Consulta de Embarques Enviados do pedido , utilizando a consulta de notas fiscais do ERP
    entregasFaturadas = ObtendoEntregas_Enviados()
    pedidos = pd.merge(pedidos,entregasFaturadas,on='codPedido',how='left')
    pedidos['entregas_enviadas'].fillna(0,inplace=True)
    etapa3 = controle.salvarStatus_Etapa3(rotina, ip, etapa2, 'Consulta de Embarques Enviados do pedido') #Registrar etapa no controlador


    # 4- Consulta de Embarques Solicitado pelo Cliente , informacao extraida do ERP
    entregasSolicitadas = ObtendoEntregasSolicitadas()
    pedidos = pd.merge(pedidos,entregasSolicitadas,on='codPedido',how='left')
    pedidos['entregas_Solicitadas'].fillna(0,inplace=True)
    etapa4 = controle.salvarStatus_Etapa4(rotina, ip, etapa3, 'Consulta de Embarques Solicitado pelo Cliente') #Registrar etapa no controlador


    # 5 - Explodir os pedidos no nivel sku
    if tipoData == 'DataEmissao':
        sku = Monitor_nivelSku(iniVenda)
    else:
        sku = Monitor_nivelSkuPrev(iniVenda)

    estruturasku = EstruturaSku()
        # 5.1 - Considerando somente a qtdePedida maior que 0
    pedidos = pd.merge(pedidos,sku,on='codPedido',how='left')
    pedidos = pd.merge(pedidos,estruturasku,on='codProduto',how='left')
    pedidos['QtdSaldo'] = pedidos['qtdePedida']- pedidos['qtdeFaturada']-pedidos['qtdeSugerida']
    pedidos['QtdSaldo'].fillna(0,inplace=True)
    pedidos['QtdSaldo'] = pedidos['QtdSaldo'].astype(int)
    etapa5 = controle.salvarStatus_Etapa5(rotina, ip, etapa4, 'Explodir os pedidos no nivel sku')#Registrar etapa no controlador



    # 6 Consultando n banco de dados do ERP o saldo de estoque
    estoque = EstoqueSKU()
    pedidos = pd.merge(pedidos,estoque,on='codProduto',how='left')
    etapa6 = controle.salvarStatus_Etapa6(rotina, ip, etapa5, 'Consultando n banco de dados do ERP o saldo de estoque')#Registrar etapa no controlador

    #7 Calculando a nova data de Previsao do pedido
    pedidos['dias_a_adicionar'] = pd.to_timedelta(pedidos['entregas_enviadas']*15, unit='d') # Converte a coluna de inteiros para timedelta
    pedidos['dataPrevAtualizada']= pd.to_datetime(pedidos['dataPrevFat'],errors='coerce', infer_datetime_format=True)
    pedidos['dataPrevAtualizada'] =  pedidos['dataPrevAtualizada'] + pedidos['dias_a_adicionar']
    pedidos['dataPrevAtualizada'].fillna('-',inplace=True)

    etapa7 = controle.salvarStatus_Etapa7(rotina, ip, etapa6, 'Calculando a nova data de Previsao do pedido')#Registrar etapa no controlador


    # 8 -# Clasificando o Dataframe para analise
    pedidos = Classificacao(pedidos, parametroClassificacao)
    etapa8 = controle.salvarStatus_Etapa8(rotina, ip, etapa7, 'Clasificando o Dataframe para analise')#Registrar etapa no controlador



    #9 Contando o numero de ocorrencias acumulado do sku no DataFrame
    pedidos = pedidos[pedidos['vlrSaldo'] > 0]
    pedidos['Sku_acumula'] = pedidos.groupby('codProduto').cumcount() + 1
    etapa9 = controle.salvarStatus_Etapa9(rotina, ip, etapa8, 'Contando o numero de ocorrencias acumulado do sku')#Registrar etapa no controlador


    #10.1 Obtendo o Estoque Liquido para o calculo da necessidade
    pedidos['EstoqueLivre'] = pedidos['estoqueAtual']-pedidos['estReservPedido']
    #10.2 Obtendo a necessidade de estoque
    pedidos['Necessidade'] = pedidos.groupby('codProduto')['QtdSaldo'].cumsum()
    #10.3 0 Obtendo a Qtd que antende para o pedido baseado no estoque
    #pedidos["Qtd Atende"] = pedidos.apply(lambda row: row['QtdSaldo']  if row['Necessidade'] <= row['EstoqueLivre'] else 0, axis=1)
    pedidos['Qtd Atende'] = pedidos['QtdSaldo'].where(pedidos['Necessidade'] <= pedidos['EstoqueLivre'], 0)

    pedidos.loc[pedidos['qtdeSugerida'] > 0, 'Qtd Atende'] = pedidos['qtdeSugerida']

    pedidos['Qtd Atende'] = pedidos['Qtd Atende'].astype(int)
    etapa10 = controle.salvarStatus_Etapa10(rotina, ip, etapa9, 'Calculando a necessidade por sku')#Registrar etapa no controlador


    #11.1 Separando os pedidos a nivel pedido||engenharia||cor
    pedidos["Pedido||Prod.||Cor"] = pedidos['codPedido'].str.cat([pedidos['codItemPai'], pedidos['codCor']],sep='||')
    #11.2  Calculando a necessidade a nivel de grade Pedido||Prod.||Cor
    pedidos['Saldo +Sugerido'] = pedidos['QtdSaldo']+pedidos['qtdeSugerida']
    pedidos['Saldo Grade'] = pedidos.groupby('Pedido||Prod.||Cor')['Saldo +Sugerido'].transform('sum')
    etapa11 = controle.salvarStatus_Etapa11(rotina, ip, etapa10, 'necessidade a nivel de grade Pedido||Prod.||Cor')#Registrar etapa no controlador


    #12 obtendo a Qtd que antende para o pedido baseado no estoque e na grade
    pedidos['X QTDE ATENDE'] = pedidos.groupby('Pedido||Prod.||Cor')['Qtd Atende'].transform('sum')
    #pedidos['Qtd Atende por Cor'] = pedidos.apply(lambda row: row['Saldo +Sugerido'] if row['Saldo Grade'] == row['X QTDE ATENDE'] else 0, axis=1)
    pedidos['Qtd Atende por Cor'] = pedidos['Saldo +Sugerido'].where(pedidos['Saldo Grade'] == pedidos['X QTDE ATENDE'],0)

    pedidos['Qtd Atende por Cor'] = pedidos['Qtd Atende por Cor'].astype(int)
    etapa12 = controle.salvarStatus_Etapa12(rotina, ip, etapa11, 'obtendo a Qtd que antende para o pedido baseado no estoque e na grade')#Registrar etapa no controlador


    #13- Indicador de % que fecha no pedido a nivel de grade Pedido||Prod.||Cor'
    #pedidos['% Fecha'] = (pedidos.groupby('Pedido||Prod.||Cor')['Qtd Atende por Cor'].transform('sum')).round(2) / ( pedidos.groupby('codPedido')['Saldo +Sugerido'].transform('sum')).round(2)
    #pedidos['% Fecha'] = pedidos['% Fecha'].round(2)
    #pedidos['% Fecha'] = pedidos['% Fecha'] *100
    pedidos['Fecha Acumulado'] = pedidos.groupby('codPedido')['Qtd Atende por Cor'].cumsum().round(2)
    pedidos['Saldo +Sugerido_Sum'] = pedidos.groupby('codPedido')['Saldo +Sugerido'].transform('sum')
    pedidos['% Fecha Acumulado'] = (pedidos['Fecha Acumulado'] / pedidos['Saldo +Sugerido_Sum']).round(2) * 100
    pedidos['% Fecha Acumulado'] = pedidos['% Fecha Acumulado'].astype(str)
    pedidos['% Fecha Acumulado'] = pedidos['% Fecha Acumulado'].str.slice(0, 4)
    pedidos['% Fecha Acumulado'] = pedidos['% Fecha Acumulado'].astype(float)
    etapa13 = controle.salvarStatus_Etapa13(rotina, ip, etapa12, ' Indicador de % que fecha no pedido a nivel de grade Pedido||Prod.||Cor')#Registrar etapa no controlador


    # 14 - Encontrando a Marca desejada
    pedidos['codItemPai'] = pedidos['codItemPai'].astype(str)
    pedidos['MARCA'] = pedidos['codItemPai'].apply(lambda x: x[:3])
    pedidos['MARCA'] = numpy.where((pedidos['codItemPai'].str[:3] == '102') | (pedidos['codItemPai'].str[:3] == '202'), 'M.POLLO', 'PACO')
    etapa14 = controle.salvarStatus_Etapa14(rotina, ip, etapa13, ' Encontrando a Marca desejada')#Registrar etapa no controlador

    # função para verificar a presença de "casa" no valor da coluna "produto"
    def categorizar_produto(produto):
        if 'JAQUETA' in produto:
            return 'AGASALHOS'
        elif 'BLUSAO' in produto:
            return 'AGASALHOS'
        elif 'TSHIRT' in produto:
            return 'CAMISETA'
        elif 'POLO' in produto:
            return 'POLO'
        elif 'SUNGA' in produto:
            return 'SUNGA'
        elif 'CUECA' in produto:
            return 'CUECA'
        elif 'CALCA/BER MOLETOM  ' in produto:
            return 'CALCA/BER MOLETOM '
        elif 'CAMISA' in produto:
            return 'CAMISA'
        elif 'SHORT' in produto:
            return 'BOARDSHORT'
        elif 'TRICOT' in produto:
            return 'TRICOT'
        elif 'BABY' in produto:
            return 'CAMISETA'
        elif 'BATA' in produto:
            return 'CAMISA'
        elif 'CALCA' in produto:
            return 'CALCA/BER MOLETOM'
        elif 'CARTEIRA' in produto:
            return 'ACESSORIOS'
        elif 'BONE' in produto:
            return 'ACESSORIOS'
        elif 'TENIS' in produto:
            return 'CALCADO'
        elif 'CHINELO' in produto:
            return 'CALCADO'
        elif 'MEIA' in produto:
            return 'ACESSORIOS'
        elif 'BLAZER' in produto:
            return 'AGASALHOS'
        elif 'CINTO' in produto:
            return 'ACESSORIOS'
        elif 'REGATA' in produto:
            return 'ACESSORIOS'
        elif 'BERMUDA' in produto:
            return 'CALCA/BER MOLETOM'
        elif 'COLETE' in produto:
            return 'AGASALHOS'
        elif 'NECESSA' in produto:
            return 'ACESSORIOS'
        elif 'CARTA' in produto:
            return 'ACESSORIOS'
        elif 'SACOL' in produto:
            return 'ACESSORIOS'
        else:
            return '-'

    # 15 - Encontrando a categoria do produto
    try:
        pedidos['CATEGORIA'] = pedidos['nomeSKU'].apply(categorizar_produto)
        # pedidos['CATEGORIA'] = pedidos.apply(lambda row: categorizar_produto(row['nomeSKU']),axis=1)
    except:
        pedidos['CATEGORIA'] = '-'
    etapa15 = controle.salvarStatus_Etapa15(rotina, ip, etapa14, ' Encontrando a categoria do produto')#Registrar etapa no controlador

    # 16- Trazendo as configuracoes de % deistribuido configurado
    dadosConfPer = ConfiguracaoPercEntregas()
    # 16.1 Encontrando o numero restante de entregas
    pedidos['Entregas Restantes'] = pedidos['entregas_Solicitadas'] - pedidos['entregas_enviadas']
    #pedidos['Entregas Restantes'] = pedidos.apply(lambda row: 1 if row['entregas_Solicitadas'] <= row['entregas_enviadas'] else row['Entregas Restantes'], axis=1)
    pedidos.loc[pedidos['entregas_Solicitadas'] <= pedidos['entregas_enviadas'], 'Entregas Restantes'] = 1

    pedidos['Entregas Restantes'] = pedidos['Entregas Restantes'].astype(str)
    pedidos['Entregas Restantes'] = pedidos['Entregas Restantes'].str.replace('.0','')
    pedidos = pd.merge(pedidos, dadosConfPer, on='Entregas Restantes', how='left')
    etapa16 = controle.salvarStatus_Etapa16(rotina, ip, etapa15, 'Encontrando o numero restante de entregas')#Registrar etapa no controlador

    # 17 - Trazendo as configuracoes de categorias selecionadas e aplicando regras de categoria
    dadosCategoria = ConfiguracaoCategoria()
    pedidos = pd.merge(pedidos,dadosCategoria,on='CATEGORIA',how='left')
    pedidos.loc[pedidos['Status'] != '1', 'Qtd Atende por Cor'] = 0
    pedidos.loc[pedidos['Status'] != '1', 'Qtd Atende'] = 0
    etapa17 = controle.salvarStatus_Etapa17(rotina, ip, etapa16, 'Trazendo as configuracoes de categorias selecionadas')#Registrar etapa no controlador


    #18 - Encontrando no pedido o percentual que atende a distribuicao
    pedidos['% Fecha pedido'] = (pedidos.groupby('codPedido')['Qtd Atende por Cor'].transform('sum')) / (pedidos.groupby('codPedido')['Saldo +Sugerido'].transform('sum'))
    pedidos['% Fecha pedido'] = pedidos['% Fecha pedido']*100
    pedidos['% Fecha pedido'] = pedidos['% Fecha pedido'].astype(float).round(2)
    etapa18 = controle.salvarStatus_Etapa18(rotina, ip, etapa17, 'Encontrando no pedido o percentual que atende a distribuicao')#Registrar etapa no controlador

    #19 - Encontrando os valores que considera na ditribuicao
    pedidos['ValorMin'] = pedidos['ValorMin'].astype(float)
    pedidos['ValorMax'] = pedidos['ValorMax'].astype(float)
    condicoes = [(pedidos['% Fecha pedido'] >= pedidos['ValorMin']) &
                (pedidos['% Fecha pedido'] <= pedidos['ValorMax']),
                (pedidos['% Fecha pedido'] > pedidos['ValorMax']) &
                (pedidos['% Fecha Acumulado'] <= pedidos['ValorMax']),
                (pedidos['% Fecha pedido'] > pedidos['ValorMax']) &
                (pedidos['% Fecha Acumulado'] > pedidos['ValorMax']),
                (pedidos['% Fecha pedido'] < pedidos['ValorMin'])
                # adicionar mais condições aqui, se necessário
                ]
    valores = ['SIM', 'SIM','SIM(Redistribuir)','NAO']# definir os valores correspondentes
    pedidos['Distribuicao'] = numpy.select(condicoes, valores, default=True)
    etapa19 = controle.salvarStatus_Etapa19(rotina, ip, etapa18, 'formula do numpy ')#Registrar etapa no controlador

    # função para avaliar cada grupo


    def avaliar_grupo(df_grupo):
        return len(set(df_grupo)) == 1

    df_resultado = pedidos.loc[:, ['Pedido||Prod.||Cor', 'Distribuicao']]
    df_resultado = df_resultado.groupby('Pedido||Prod.||Cor')['Distribuicao'].apply(avaliar_grupo).reset_index()
    df_resultado.columns = ['Pedido||Prod.||Cor', 'Resultado']
    df_resultado['Resultado'] = df_resultado['Resultado'].astype(str)
    etapa20 = controle.salvarStatus_Etapa20(rotina, ip, etapa19, 'Avaliacao do Grupo')#Registrar etapa no controlador

    pedidos = pd.merge(pedidos, df_resultado, on='Pedido||Prod.||Cor', how='left')

    # 19.1: Atualizando a coluna 'Distribuicao' diretamente
    condicao = (pedidos['Resultado'] == 'False') & (
                (pedidos['Distribuicao'] == 'SIM') & (pedidos['Qtd Atende por Cor'] > 0))
    pedidos.loc[condicao, 'Distribuicao'] = 'SIM(Redistribuir)'
    etapa21 = controle.salvarStatus_Etapa21(rotina, ip, etapa20, 'Encontrando no pedido o percentual que atende a distribuicao')#Registrar etapa no controlador


    #20- Obtendo valor atente por cor
    pedidos['Valor Atende por Cor'] = pedidos['Qtd Atende por Cor'] * pedidos['PrecoLiquido']
    pedidos['Valor Atende por Cor'] = pedidos['Valor Atende por Cor'].astype(float).round(2)
    etapa22 = controle.salvarStatus_Etapa22(rotina, ip, etapa21, 'Obtendo valor atente por cor')#Registrar etapa no controlador



    #21 Identificando a Quantidade Distribuida
    #pedidos['Qnt. Cor(Distrib.)'] = pedidos.apply(lambda row: row['Qtd Atende por Cor'] if row['Distribuicao'] == 'SIM' else 0, axis=1)
    pedidos['Qnt. Cor(Distrib.)'] = pedidos['Qtd Atende por Cor'].where(pedidos['Distribuicao'] == 'SIM', 0)

    pedidos['Qnt. Cor(Distrib.)'] = pedidos['Qnt. Cor(Distrib.)'].astype(int)
    etapa23 = controle.salvarStatus_Etapa23(rotina, ip, etapa22, 'Obtendo valor atente por cor')#Registrar etapa no controlador


    #22 Obtendo valor atente por cor Distribuida
    #pedidos['Valor Atende por Cor(Distrib.)'] = pedidos.apply(lambda row: row['Valor Atende por Cor'] if row['Distribuicao'] == 'SIM' else 0, axis=1)
    pedidos['Valor Atende por Cor(Distrib.)'] = pedidos['Valor Atende por Cor'].where(pedidos['Distribuicao'] == 'SIM', 0)
    pedidos['Valor Atende'] = pedidos['Qtd Atende'] * pedidos['PrecoLiquido']
    pedidos['Valor Atende'] =pedidos['Valor Atende'].astype(float).round(2)
    pedidos.drop(['situacaobloq', 'dias_a_adicionar', 'Resultado'], axis=1, inplace=True)

    etapa24 = controle.salvarStatus_Etapa24(rotina, ip, etapa23, 'Obtendo valor atente por cor Distribuida')#Registrar etapa no controlador
    pedidos['dataPrevAtualizada'] = pedidos['dataPrevAtualizada'].dt.strftime('%d/%m/%Y')
    pedidos["descricaoCondVenda"].fillna('-',inplace=True)
    pedidos["ultimo_fat"].fillna('-', inplace=True)
    pedidos["Status"].fillna('-', inplace=True)

    #Ciclo 2
    situacao = pedidos.groupby('codPedido')['Valor Atende por Cor(Distrib.)'].sum().reset_index()
    situacao = situacao[situacao['Valor Atende por Cor(Distrib.)'] > 0]
    situacao.columns = ['codPedido','totalPçDis']
    pedidos = pd.merge(pedidos,situacao,on='codPedido',how='left')
    pedidos.fillna(0,inplace=True)

    pedidos1 = pedidos[pedidos['totalPçDis'] == 0]
    pedidos1['SituacaoDistrib'] = 'Redistribui'
    pedidos1 = Ciclo2(pedidos1, avaliar_grupo)
    pedidos2 = pedidos[pedidos['totalPçDis'] > 0]
    pedidos2['SituacaoDistrib'] = 'Distribuido1'


    pedidos = pd.concat([pedidos1, pedidos2])

    #23- Salvando os dados gerados em csv
    #retirar as seguintes colunas: StatusSugestao, situacaobloq, dias_a_adicionar, Resultado

    fp.write('monitor.parquet', pedidos)
    etapa25 = controle.salvarStatus_Etapa25(rotina, ip, etapa24, 'Salvando os dados gerados no postgre')#Registrar etapa no controlador
    return pedidos


def API(empresa, iniVenda, finalVenda, tiponota,rotina, ip, datainicio,parametroClassificacao, tipoData):
    tiponota = '1,2,3,4,5,6,7,8,10,24,92,201,1012,77,27,28,172,9998,66,67,233,237'#Arrumar o Tipo de Nota 40
    pedidos = MonitorDePreFaturamento(empresa, iniVenda, finalVenda, tiponota,rotina, ip, datainicio,parametroClassificacao,tipoData)
    pedidos['codPedido'] = pedidos['codPedido'].astype(str)
    pedidos['codCliente'] = pedidos['codCliente'].astype(str)
    pedidos["StatusSugestao"].fillna('-', inplace=True)




    pedidos = pedidos.groupby('codPedido').agg({
    "MARCA": 'first',
    "codTipoNota": 'first',
    "dataEmissao":'first',
    "dataPrevFat": 'first',
    "dataPrevAtualizada": 'first',
    "codCliente": 'first',
    #"razao": 'first',
    "vlrSaldo": 'first',
    #"descricaoCondVenda": 'first',
    "entregas_Solicitadas": 'first',
    "entregas_enviadas": 'first',
    "qtdPecasFaturadas": 'first',
    'Saldo +Sugerido':'sum',
    "ultimo_fat": "first",
    "Qtd Atende": 'sum',
    'QtdSaldo': 'sum',
    'Qtd Atende por Cor': 'sum',
    'Valor Atende por Cor': 'sum',
    #'Valor Atende': 'sum',
    'StatusSugestao': 'first',
    'Valor Atende por Cor(Distrib.)': 'sum',
    'Qnt. Cor(Distrib.)': 'sum',
    'SituacaoDistrib':'first'
    #'observacao': 'first'
    }).reset_index()

    pedidos['%'] = pedidos['Qnt. Cor(Distrib.)']/(pedidos['Saldo +Sugerido'])
    pedidos['%'] = pedidos['%']*100
    pedidos['%'] = pedidos['%'].round(0)
    pedidos.rename(columns={'MARCA': '01-MARCA',"codPedido":"02-Pedido",
                            "codTipoNota":"03-tipoNota","dataPrevFat":"04-Prev.Original","dataPrevAtualizada":"05-Prev.Atualiz","codCliente":"06-codCliente",
                            "vlrSaldo":"08-vlrSaldo","entregas_Solicitadas":"09-Entregas Solic","entregas_enviadas":"10-Entregas Fat",
                            "ultimo_fat":"11-ultimo fat","qtdPecasFaturadas":"12-qtdPecas Fat","Qtd Atende":"13-Qtd Atende","QtdSaldo":"14- Qtd Saldo",
                            "Qnt. Cor(Distrib.)":"21-Qnt Cor(Distrib.)","%":"23-% qtd cor",
                            "StatusSugestao":"18-Sugestao(Pedido)","Qtd Atende por Cor":"15-Qtd Atende p/Cor","Valor Atende por Cor":"16-Valor Atende por Cor",
                            "Valor Atende por Cor(Distrib.)":"22-Valor Atende por Cor(Distrib.)"}, inplace=True)

    pedidos = pedidos.sort_values(by=['23-% qtd cor','08-vlrSaldo'], ascending=False)  # escolher como deseja classificar
    pedidos["10-Entregas Fat"].fillna(0,inplace=True)
    pedidos["09-Entregas Solic"].fillna(0, inplace=True)

    pedidos["11-ultimo fat"].fillna('-', inplace=True)
    pedidos["05-Prev.Atualiz"].fillna('-', inplace=True)
    pedidos.fillna(0, inplace=True)

    pedidos["16-Valor Atende por Cor"] =pedidos["16-Valor Atende por Cor"].round(2)
    pedidos["22-Valor Atende por Cor(Distrib.)"] = pedidos["22-Valor Atende por Cor(Distrib.)"].round(2)

    saldo =pedidos['08-vlrSaldo'].sum()
    TotalQtdCor = pedidos['15-Qtd Atende p/Cor'].sum()
    TotalValorCor = pedidos['16-Valor Atende por Cor'].sum()
    TotalValorCor = TotalValorCor.round(2)

    totalPedidos = pedidos['02-Pedido'].count()
    PedidosDistribui = pedidos[pedidos['23-% qtd cor']>0]
    PedidosDistribui = PedidosDistribui['02-Pedido'].count()

    pedidosRedistribuido = pedidos[pedidos['SituacaoDistrib'] == 'Distribuido2']
    pedidosRedistribuido = pedidosRedistribuido['SituacaoDistrib'].count()

    TotalQtdCordist = pedidos['21-Qnt Cor(Distrib.)'].sum()
    TotalValorCordist = pedidos['22-Valor Atende por Cor(Distrib.)'].sum()
    TotalValorCordist = TotalValorCordist.round(2)

    #Agrupando os clientes
    # Função para concatenar os valores agrupados
    def concat_values(group):
        return '/'.join(str(x) for x in group)
    # Agrupar e aplicar a função de concatenação
    result = pedidos.groupby('06-codCliente')['02-Pedido'].apply(concat_values).reset_index()
    # Renomear as colunas
    result.columns = ['06-codCliente', 'Agrupamento']
    pedidos = pd.merge(pedidos,result,on='06-codCliente',how='left')

    dados = {
        '0-Status':True,
        '1-Total Qtd Atende por Cor': f'{TotalQtdCor} Pçs',
        '2-Total Valor Valor Atende por Cor': f'{TotalValorCor}',
        '3-Total Qtd Cor(Distrib.)': f'{TotalQtdCordist} Pçs',
        '4-Total Valor Atende por Cor(Distrib.)': f'{TotalValorCordist}',
        '5-Valor Saldo Restante':f'{saldo}',
        '5.1-Total Pedidos': f'{totalPedidos}',
        '5.2-Total Pedidos distribui':f'{PedidosDistribui},({pedidosRedistribuido} pedidos redistribuido)',
        '6 -Detalhamento': pedidos.to_dict(orient='records')

    }
    return pd.DataFrame([dados])

def APICongelada(empresa, iniVenda, finalVenda, tiponota,rotina, ip, datainicio,parametroClassificacao, tipoData):
    tiponota = '1,2,3,4,5,6,7,8,10,24,92,201,1012,77,27,28,172,9998,66,67,233,237'#Arrumar o Tipo de Nota 40
    # Carregar o arquivo Parquet
    parquet_file = fp.ParquetFile('monitor.parquet')
    # Converter para DataFrame do Pandas
    pedidos = parquet_file.to_pandas()
    pedidos['codPedido'] = pedidos['codPedido'].astype(str)
    pedidos['codCliente'] = pedidos['codCliente'].astype(str)
    pedidos["StatusSugestao"].fillna('-', inplace=True)
    pedidos = pedidos.groupby('codPedido').agg({
    "MARCA": 'first',
    "codTipoNota": 'first',
    "dataEmissao":'first',
    "dataPrevFat": 'first',
    "dataPrevAtualizada": 'first',
    "codCliente": 'first',
    #"razao": 'first',
    "vlrSaldo": 'first',
    #"descricaoCondVenda": 'first',
    "entregas_Solicitadas": 'first',
    "entregas_enviadas": 'first',
    "qtdPecasFaturadas": 'first',
    'Saldo +Sugerido':'sum',
    "ultimo_fat": "first",
    "Qtd Atende": 'sum',
    'QtdSaldo': 'sum',
    'Qtd Atende por Cor': 'sum',
    'Valor Atende por Cor': 'sum',
    #'Valor Atende': 'sum',
    'StatusSugestao': 'first',
    'Valor Atende por Cor(Distrib.)': 'sum',
    'Qnt. Cor(Distrib.)': 'sum'
    #'observacao': 'first'
    }).reset_index()

    pedidos['%'] = pedidos['Qnt. Cor(Distrib.)']/(pedidos['Saldo +Sugerido'])
    pedidos['%'] = pedidos['%']*100
    pedidos['%'] = pedidos['%'].round(0)
    pedidos.rename(columns={'MARCA': '01-MARCA',"codPedido":"02-Pedido",
                            "codTipoNota":"03-tipoNota","dataPrevFat":"04-Prev.Original","dataPrevAtualizada":"05-Prev.Atualiz","codCliente":"06-codCliente",
                            "vlrSaldo":"08-vlrSaldo","entregas_Solicitadas":"09-Entregas Solic","entregas_enviadas":"10-Entregas Fat",
                            "ultimo_fat":"11-ultimo fat","qtdPecasFaturadas":"12-qtdPecas Fat","Qtd Atende":"13-Qtd Atende","QtdSaldo":"14- Qtd Saldo",
                            "Qnt. Cor(Distrib.)":"21-Qnt Cor(Distrib.)","%":"23-% qtd cor",
                            "StatusSugestao":"18-Sugestao(Pedido)","Qtd Atende por Cor":"15-Qtd Atende p/Cor","Valor Atende por Cor":"16-Valor Atende por Cor",
                            "Valor Atende por Cor(Distrib.)":"22-Valor Atende por Cor(Distrib.)"}, inplace=True)

    pedidos = pedidos.sort_values(by=['23-% qtd cor','08-vlrSaldo'], ascending=False)  # escolher como deseja classificar
    pedidos["10-Entregas Fat"].fillna(0,inplace=True)
    pedidos["09-Entregas Solic"].fillna(0, inplace=True)

    pedidos["11-ultimo fat"].fillna('-', inplace=True)
    pedidos["05-Prev.Atualiz"].fillna('-', inplace=True)
    pedidos.fillna(0, inplace=True)

    pedidos["16-Valor Atende por Cor"] =pedidos["16-Valor Atende por Cor"].round(2)
    pedidos["22-Valor Atende por Cor(Distrib.)"] = pedidos["22-Valor Atende por Cor(Distrib.)"].round(2)

    saldo =pedidos['08-vlrSaldo'].sum()
    TotalQtdCor = pedidos['15-Qtd Atende p/Cor'].sum()
    TotalValorCor = pedidos['16-Valor Atende por Cor'].sum()
    TotalValorCor = TotalValorCor.round(2)

    totalPedidos = pedidos['02-Pedido'].count()
    PedidosDistribui = pedidos[pedidos['23-% qtd cor']>0]
    PedidosDistribui = PedidosDistribui['02-Pedido'].count()


    TotalQtdCordist = pedidos['21-Qnt Cor(Distrib.)'].sum()
    TotalValorCordist = pedidos['22-Valor Atende por Cor(Distrib.)'].sum()
    TotalValorCordist = TotalValorCordist.round(2)

    #Agrupando os clientes
    # Função para concatenar os valores agrupados
    def concat_values(group):
        return '/'.join(str(x) for x in group)
    # Agrupar e aplicar a função de concatenação
    result = pedidos.groupby('06-codCliente')['02-Pedido'].apply(concat_values).reset_index()
    # Renomear as colunas
    result.columns = ['06-codCliente', 'Agrupamento']
    pedidos = pd.merge(pedidos,result,on='06-codCliente',how='left')

    dados = {
        '0-Status':False,
        '001-Mesagem': 'API Congelada pois existe calculo em aberto',
        '1-Total Qtd Atende por Cor': f'{TotalQtdCor} Pçs',
        '2-Total Valor Valor Atende por Cor': f'{TotalValorCor}',
        '3-Total Qtd Cor(Distrib.)': f'{TotalQtdCordist} Pçs',
        '4-Total Valor Atende por Cor(Distrib.)': f'{TotalValorCordist}',
        '5-Valor Saldo Restante':f'{saldo}',
        '5.1-Total Pedidos': f'{totalPedidos}',
        '5.2-Total Pedidos distribui':f'{PedidosDistribui}',
        '6 -Detalhamento': pedidos.to_dict(orient='records')

    }
    return pd.DataFrame([dados])


def ConfiguracaoPercEntregas():
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql(
            """Select * from pcp.monitor_fat_dados """, conn)

    conn.close()
    consultar['Entregas Restantes'] = consultar['Entregas Restantes'].astype(str)

    return consultar


def ConfiguracaoCategoria():
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql(
            """
            Select "Opção" as "CATEGORIA", "Status" from pcp.monitor_check_status 
            """, conn)

    conn.close()

    return consultar


#CROD DA TABELA MAX/MIN POR EMBARQUE:

def ConsultaConfiguracaoDistribuicao():
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql(
            """Select "Entregas Restantes","ValorMin","ValorMax"  from pcp.monitor_fat_dados
order by "Entregas Restantes"::int asc""", conn)

    conn.close()
    consultar['Entregas Restantes'] = consultar['Entregas Restantes'].astype(str)

    return consultar

def Update(arrayEmbarque, arrayMIN, arrayMAX):
    conn = ConexaoPostgreMPL.conexao()


    for i in range(len(arrayEmbarque)):

        embarque = arrayEmbarque[i]
        min =arrayMIN[i]
        max =arrayMAX[i]


        update = """update pcp.monitor_fat_dados 
        set "Entregas Restantes" = %s , "ValorMin" = %s ,"ValorMax" = %s  
        where "Entregas Restantes" = %s """

        cursor = conn.cursor()
        cursor.execute(update,(embarque,min,max,embarque))
        conn.commit()
        cursor.close()



    conn.close()

    return pd.DataFrame([{'Mensagem':'Alerado com sucesso','status':True}])


#Criando o modelo de classificacao
def Classificacao(pedidos, parametro):
    if parametro == 'Faturamento':
        # Define os valores de 'codSitSituacao' com base na condição para Faturamento
        pedidos.loc[(pedidos['codSitSituacao'] == '0') | (pedidos['codSitSituacao'] == '1'), 'codSitSituacao'] = '2-InicioFila'
        pedidos.loc[(pedidos['codSitSituacao'] != '2-InicioFila'), 'codSitSituacao'] = '1-FimFila'
        pedidos = pedidos.sort_values(by=['codSitSituacao', 'vlrSaldo'], ascending=False)
    elif parametro == 'DataPrevisao':
        # Define os valores de 'codSitSituacao' com base na condição para DataPrevisao
        pedidos.loc[(pedidos['codSitSituacao'] == '0') | (pedidos['codSitSituacao'] == '1'), 'codSitSituacao'] = '1-InicioFila'
        pedidos.loc[(pedidos['codSitSituacao'] != '1-InicioFila'), 'codSitSituacao'] = '2-FimFila'
        pedidos = pedidos.sort_values(by=['codSitSituacao', 'dataPrevAtualizada'], ascending=True)
    return pedidos


# testa se existe calculo em aberto

def ExisteCalculoAberto(rotina):
    conn = ConexaoPostgreMPL.conexao2()
    consulta = pd.read_sql("""
        select * from 
        (select status,(now():: time  - substring(inicio,12,5)::time) as ultimoTempo from "Reposicao".configuracoes.controle_requisicao_csw 
        where rotina = %s and status = 'em andamento') df 
        where  df.ultimoTempo < '03:07:00' 
        """, conn, params=(rotina,))

    conn.close()
    print(consulta)
    if not consulta.empty:
        if consulta['status'][0] == 'em andamento':
            return 'em andamento'
        else:
            return 'nao iniciado'
    else:
        return 'nao iniciado'



def AbrirArquivoFast():
    # Carregar o arquivo Parquet
    parquet_file = fp.ParquetFile('/home/grupompl/Automacao_WMS_InternoMPL/pedidos.parquet')

    # Converter para DataFrame do Pandas
    df_loaded = parquet_file.to_pandas()

    df_loaded['dataPrevFat']= pd.to_datetime(df_loaded['dataPrevFat'],errors='coerce', infer_datetime_format=True)
    teste = '2024-01-01'
    df_loaded['filtro'] = df_loaded['dataPrevFat'] >= teste
    df_loaded = df_loaded[df_loaded['filtro']==True].reset_index()
    df_loaded = df_loaded.loc[:, ['codPedido', 'codProduto', 'qtdePedida', 'qtdeFaturada', 'qtdeCancelada','qtdeSugerida',#'StatusSugestao',
                                   'PrecoLiquido']]
    #consultar = consultar.rename(columns={'StatusSugestao': 'Sugestao(Pedido)'})
    df_loaded['qtdeSugerida'] = df_loaded['qtdeSugerida'].replace('None', 0)
    df_loaded['qtdeSugerida'] =df_loaded['qtdeSugerida'].fillna(0,inplace=True)
    df_loaded['qtdeSugerida'] = pd.to_numeric(df_loaded['qtdeSugerida'], errors='coerce').fillna(0)
    df_loaded['qtdePedida'] = pd.to_numeric(df_loaded['qtdePedida'], errors='coerce').fillna(0)
    df_loaded['qtdeFaturada'] = pd.to_numeric(df_loaded['qtdeFaturada'], errors='coerce').fillna(0)
    df_loaded['qtdeCancelada'] = pd.to_numeric(df_loaded['qtdeCancelada'], errors='coerce').fillna(0)

    print(df_loaded)
def Ciclo2(pedidos1,avaliar_grupo):
    ###### O Ciclo2 e´usado para redistribuir as quantidades dos skus  que nao conseguiram atender na distribuicao dos pedidos no primeiro ciclo.

    #etapa 1: recarregando estoque
    estoque = EstoqueSKU() # é feito uma nova releitura do estoque
    pedidos1 = pedidos1[pedidos1['StatusSugestao'] == 'Nao Sugerido']
    pedidos2 = pedidos1[pedidos1['StatusSugestao'] != 'Nao Sugerido']


    pedidos1['codProduto'].fillna(0,inplace=True)
    pedidos1['codProduto']=pedidos1['codProduto'].astype(str)

    SKUnovaReserva = pedidos1.groupby('codProduto').agg({'Qnt. Cor(Distrib.)': 'sum'}).reset_index()



    pedidos1.drop(['EstoqueLivre','estoqueAtual','estReservPedido',
                   'Necessidade','Qtd Atende','Saldo +Sugerido',
                   'Saldo Grade','X QTDE ATENDE','Qtd Atende por Cor','Fecha Acumulado',
                   'Saldo +Sugerido_Sum','% Fecha Acumulado','% Fecha pedido','Distribuicao','Valor Atende por Cor','Qnt. Cor(Distrib.)'
                   ,'Valor Atende por Cor(Distrib.)','Valor Atende','totalPçDis','SituacaoDistrib'], axis=1,inplace=True)



    # 2.1 Somando todas as cores que conseguiu distriubuir no ciclo 1 para depois abater
    SKUnovaReserva.rename(columns={'Qnt. Cor(Distrib.)': 'ciclo1'}, inplace=True)
    estoque['codProduto']=estoque['codProduto'].astype(str)
    estoque2 = pd.merge(estoque,SKUnovaReserva, on='codProduto',how='left' )

    #Etapa3 filtrando somente os pedidos nao distibuidos e fazendo o merge com o estoque
    pedidos1 = pd.merge(pedidos1,estoque2,on='codProduto',how='left')
    pedidos1['EstoqueLivre'] = pedidos1['estoqueAtual']-pedidos1['estReservPedido']-pedidos1['ciclo1']

    #Etapa 4 - Calculando a Nova Necessidade e descobrindo o quanto atente por cor
    pedidos1['Necessidade'] = pedidos1.groupby('codProduto')['QtdSaldo'].cumsum()
    pedidos1['Qtd Atende'] = pedidos1['QtdSaldo'].where(pedidos1['Necessidade'] <= pedidos1['EstoqueLivre'], 0)
    pedidos1.loc[pedidos1['qtdeSugerida'] > 0, 'Qtd Atende'] = pedidos1['qtdeSugerida']
    pedidos1['Qtd Atende'] = pedidos1['Qtd Atende'].astype(int)
    pedidos1['Saldo +Sugerido'] = pedidos1['QtdSaldo'] + pedidos1['qtdeSugerida']
    pedidos1['Saldo Grade'] = pedidos1.groupby('Pedido||Prod.||Cor')['Saldo +Sugerido'].transform('sum')
    pedidos1['X QTDE ATENDE'] = pedidos1.groupby('Pedido||Prod.||Cor')['Qtd Atende'].transform('sum')
    pedidos1['Qtd Atende por Cor'] = pedidos1['Saldo +Sugerido'].where(pedidos1['Saldo Grade'] == pedidos1['X QTDE ATENDE'],0)
    pedidos1['Qtd Atende por Cor'] = pedidos1['Qtd Atende por Cor'].astype(int)


    #Etapa 5: Encontrando o novo % Fecha Acumalado para o ciclo2
    pedidos1['Fecha Acumulado'] = pedidos1.groupby('codPedido')['Qtd Atende por Cor'].cumsum().round(2)
    pedidos1['Saldo +Sugerido_Sum'] = pedidos1.groupby('codPedido')['Saldo +Sugerido'].transform('sum')
    pedidos1['% Fecha Acumulado'] = (pedidos1['Fecha Acumulado'] / pedidos1['Saldo +Sugerido_Sum']).round(2) * 100
    pedidos1['% Fecha Acumulado'] = pedidos1['% Fecha Acumulado'].astype(str)
    pedidos1['% Fecha Acumulado'] = pedidos1['% Fecha Acumulado'].str.slice(0, 4)
    pedidos1['% Fecha Acumulado'] = pedidos1['% Fecha Acumulado'].astype(float)

    pedidos1['% Fecha pedido'] = (pedidos1.groupby('codPedido')['Qtd Atende por Cor'].transform('sum')) / (
        pedidos1.groupby('codPedido')['Saldo +Sugerido'].transform('sum'))
    pedidos1['% Fecha pedido'] = pedidos1['% Fecha pedido'] * 100
    pedidos1['% Fecha pedido'] = pedidos1['% Fecha pedido'].astype(float).round(2)

    # Etapa6: Obtendo novos valores para a distribuicao
    pedidos1['ValorMin'] = pedidos1['ValorMin'].astype(float)
    pedidos1['ValorMax'] = pedidos1['ValorMax'].astype(float)
    condicoes = [(pedidos1['% Fecha pedido'] >= pedidos1['ValorMin']) &
                 (pedidos1['% Fecha pedido'] <= pedidos1['ValorMax']),
                 (pedidos1['% Fecha pedido'] > pedidos1['ValorMax']) &
                 (pedidos1['% Fecha Acumulado'] <= pedidos1['ValorMax']),
                 (pedidos1['% Fecha pedido'] > pedidos1['ValorMax']) &
                 (pedidos1['% Fecha Acumulado'] > pedidos1['ValorMax']),
                 (pedidos1['% Fecha pedido'] < pedidos1['ValorMin'])
                 # adicionar mais condições aqui, se necessário
                 ]
    valores = ['SIM', 'SIM', 'SIM(Redistribuir)', 'NAO']  # definir os valores correspondentes
    pedidos1['Distribuicao'] = numpy.select(condicoes, valores, default=True)

    #Etapa 7: Avaliando se no nivel de pedido||sku||cor possui situacao de quebra
    df_resultado = pedidos1.loc[:, ['Pedido||Prod.||Cor', 'Distribuicao']]
    df_resultado = df_resultado.groupby('Pedido||Prod.||Cor')['Distribuicao'].apply(avaliar_grupo).reset_index()
    df_resultado.columns = ['Pedido||Prod.||Cor', 'Resultado']
    df_resultado['Resultado'] = df_resultado['Resultado'].astype(str)
    pedidos1 = pd.merge(pedidos1, df_resultado, on='Pedido||Prod.||Cor', how='left')
    #7.1 Aplicando nova situacao no redistriuir
    condicao = (pedidos1['Resultado'] == 'False') & (
            (pedidos1['Distribuicao'] == 'SIM') & (pedidos1['Qtd Atende por Cor'] > 0))
    pedidos1.loc[condicao, 'Distribuicao'] = 'SIM(Redistribuir)'


    #8- Encontradno os novos valores para o ciclo2:
    pedidos1['Valor Atende por Cor'] = pedidos1['Qtd Atende por Cor'] * pedidos1['PrecoLiquido']
    pedidos1['Valor Atende por Cor'] = pedidos1['Valor Atende por Cor'].astype(float).round(2)
    pedidos1['Qnt. Cor(Distrib.)'] = pedidos1['Qtd Atende por Cor'].where(pedidos1['Distribuicao'] == 'SIM', 0)
    pedidos1['Qnt. Cor(Distrib.)'] = pedidos1['Qnt. Cor(Distrib.)'].astype(int)
    pedidos1['Valor Atende por Cor(Distrib.)'] = pedidos1['Valor Atende por Cor'].where(pedidos1['Distribuicao'] == 'SIM',0)
    pedidos1['Valor Atende'] = pedidos1['Qtd Atende'] * pedidos1['PrecoLiquido']
    pedidos1['Valor Atende'] = pedidos1['Valor Atende'].astype(float).round(2)

    situacao = pedidos1.groupby('codPedido')['Valor Atende por Cor(Distrib.)'].sum().reset_index()
    situacao = situacao[situacao['Valor Atende por Cor(Distrib.)'] > 0]
    situacao.columns = ['codPedido', 'totalPçDis']
    pedidos1 = pd.merge(pedidos1, situacao, on='codPedido', how='left')

    pedidos1['SituacaoDistrib'] = numpy.where(pedidos1['totalPçDis'] > 0, 'Distribuido2', 'Nao Redistribui')

    pedidos1 = pd.concat([pedidos1, pedidos2])

    return pedidos1


def APICongeladaCiclo2(empresa, iniVenda, finalVenda, tiponota,rotina, ip, datainicio,parametroClassificacao, tipoData):
    tiponota = '1,2,3,4,5,6,7,8,10,24,92,201,1012,77,27,28,172,9998,66,67,233,237'#Arrumar o Tipo de Nota 40

    def avaliar_grupo(df_grupo):
        return len(set(df_grupo)) == 1

    # Carregar o arquivo Parquet
    parquet_file = fp.ParquetFile('monitor.parquet')
    # Converter para DataFrame do Pandas
    pedidos = parquet_file.to_pandas()

    pedidos = Ciclo2(pedidos,avaliar_grupo)

    pedidos['codPedido'] = pedidos['codPedido'].astype(str)
    pedidos['codCliente'] = pedidos['codCliente'].astype(str)
    pedidos["StatusSugestao"].fillna('-', inplace=True)
    pedidos = pedidos.groupby('codPedido').agg({
    "MARCA": 'first',
    "codTipoNota": 'first',
    "dataEmissao":'first',
    "dataPrevFat": 'first',
    "dataPrevAtualizada": 'first',
    "codCliente": 'first',
    #"razao": 'first',
    "vlrSaldo": 'first',
    #"descricaoCondVenda": 'first',
    "entregas_Solicitadas": 'first',
    "entregas_enviadas": 'first',
    "qtdPecasFaturadas": 'first',
    'Saldo +Sugerido':'sum',
    "ultimo_fat": "first",
    "Qtd Atende": 'sum',
    'QtdSaldo': 'sum',
    'Qtd Atende por Cor': 'sum',
    'Valor Atende por Cor': 'sum',
    #'Valor Atende': 'sum',
    'StatusSugestao': 'first',
    'Valor Atende por Cor(Distrib.)': 'sum',
    'Qnt. Cor(Distrib.)': 'sum'
    #'observacao': 'first'
    }).reset_index()

    pedidos['%'] = pedidos['Qnt. Cor(Distrib.)']/(pedidos['Saldo +Sugerido'])
    pedidos['%'] = pedidos['%']*100
    pedidos['%'] = pedidos['%'].round(0)
    pedidos.rename(columns={'MARCA': '01-MARCA',"codPedido":"02-Pedido",
                            "codTipoNota":"03-tipoNota","dataPrevFat":"04-Prev.Original","dataPrevAtualizada":"05-Prev.Atualiz","codCliente":"06-codCliente",
                            "vlrSaldo":"08-vlrSaldo","entregas_Solicitadas":"09-Entregas Solic","entregas_enviadas":"10-Entregas Fat",
                            "ultimo_fat":"11-ultimo fat","qtdPecasFaturadas":"12-qtdPecas Fat","Qtd Atende":"13-Qtd Atende","QtdSaldo":"14- Qtd Saldo",
                            "Qnt. Cor(Distrib.)":"21-Qnt Cor(Distrib.)","%":"23-% qtd cor",
                            "StatusSugestao":"18-Sugestao(Pedido)","Qtd Atende por Cor":"15-Qtd Atende p/Cor","Valor Atende por Cor":"16-Valor Atende por Cor",
                            "Valor Atende por Cor(Distrib.)":"22-Valor Atende por Cor(Distrib.)"}, inplace=True)

    pedidos = pedidos.sort_values(by=['23-% qtd cor','08-vlrSaldo'], ascending=False)  # escolher como deseja classificar
    pedidos["10-Entregas Fat"].fillna(0,inplace=True)
    pedidos["09-Entregas Solic"].fillna(0, inplace=True)

    pedidos["11-ultimo fat"].fillna('-', inplace=True)
    pedidos["05-Prev.Atualiz"].fillna('-', inplace=True)
    pedidos.fillna(0, inplace=True)

    pedidos["16-Valor Atende por Cor"] =pedidos["16-Valor Atende por Cor"].round(2)
    pedidos["22-Valor Atende por Cor(Distrib.)"] = pedidos["22-Valor Atende por Cor(Distrib.)"].round(2)

    saldo =pedidos['08-vlrSaldo'].sum()
    TotalQtdCor = pedidos['15-Qtd Atende p/Cor'].sum()
    TotalValorCor = pedidos['16-Valor Atende por Cor'].sum()
    TotalValorCor = TotalValorCor.round(2)

    totalPedidos = pedidos['02-Pedido'].count()
    PedidosDistribui = pedidos[pedidos['23-% qtd cor']>0]
    PedidosDistribui = PedidosDistribui['02-Pedido'].count()


    TotalQtdCordist = pedidos['21-Qnt Cor(Distrib.)'].sum()
    TotalValorCordist = pedidos['22-Valor Atende por Cor(Distrib.)'].sum()
    TotalValorCordist = TotalValorCordist.round(2)

    #Agrupando os clientes
    # Função para concatenar os valores agrupados
    def concat_values(group):
        return '/'.join(str(x) for x in group)
    # Agrupar e aplicar a função de concatenação
    result = pedidos.groupby('06-codCliente')['02-Pedido'].apply(concat_values).reset_index()
    # Renomear as colunas
    result.columns = ['06-codCliente', 'Agrupamento']
    pedidos = pd.merge(pedidos,result,on='06-codCliente',how='left')

    dados = {
        '0-Status':False,
        '001-Mesagem': 'API Congelada pois existe calculo em aberto',
        '1-Total Qtd Atende por Cor': f'{TotalQtdCor} Pçs',
        '2-Total Valor Valor Atende por Cor': f'{TotalValorCor}',
        '3-Total Qtd Cor(Distrib.)': f'{TotalQtdCordist} Pçs',
        '4-Total Valor Atende por Cor(Distrib.)': f'{TotalValorCordist}',
        '5-Valor Saldo Restante':f'{saldo}',
        '5.1-Total Pedidos': f'{totalPedidos}',
        '5.2-Total Pedidos distribui':f'{PedidosDistribui}',
        '6 -Detalhamento': pedidos.to_dict(orient='records')

    }
    return pd.DataFrame([dados])


def ConverterDataFrameCSV():
    # Carregar o arquivo Parquet
    parquet_file = fp.ParquetFile('monitor.parquet')

    # Converter para DataFrame do Pandas
    pedidos1 = parquet_file.to_pandas()

    pedidos1.to_csv('monitor2.csv')

    return pd.DataFrame([{'Mensagem':'Gerado csv'}])