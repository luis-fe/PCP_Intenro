import pandas as pd
import BuscasAvancadas
import ConexaoCSW
import ConexaoPostgreMPL
import datetime
import numpy
import locale
from models import controle
#Carregando a Capa de pedidos do CSW : BuscasAvancadas.CapaPedido (empresa, iniVenda, finalVenda, tiponota):
def Monitor_CapaPedidos(empresa, iniVenda, finalVenda, tiponota):
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.CapaPedido(empresa, iniVenda, finalVenda, tiponota), conn)

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
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql("""select * from "PCP".pcp."pedidosItemgrade" ig 
where ig."dataEmissao":: date >= %s """,conn,params=(datainicio,)) #codPedido, codProduto, qtdePedida, qtdeFaturada, qtdeCancelada
    consultar['qtdeSugerida'].fillna(0,inplace=True)
    conn.close()

    consultar = consultar.loc[:, ['codPedido', 'codProduto', 'qtdePedida', 'qtdeFaturada', 'qtdeCancelada','qtdeSugerida',#'StatusSugestao',
                                   'PrecoLiquido']]
    #consultar = consultar.rename(columns={'StatusSugestao': 'Sugestao(Pedido)'})

    consultar['qtdeSugerida'] = consultar['qtdeSugerida'].astype(int)

    return consultar

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


def MonitorDePreFaturamento(empresa, iniVenda, finalVenda, tiponota,rotina, ip, datainicio,parametroClassificacao):
    #Convertendo tipo de nota em string "1,2, 3, .."

    #tiponota2 = ""
    #for i in tiponota:
        #tiponota2 = tiponota2 + "," + i

    #tiponota2 = tiponota2[1:]

    # 1 - Carregar Os pedidos (etapa 1)
    pedidos = Monitor_CapaPedidos(empresa, iniVenda, finalVenda, tiponota)
    statusSugestao = CapaSugestao()
    pedidos = pd.merge(pedidos,statusSugestao,on='codPedido',how='left')
    pedidos["StatusSugestao"].fillna('0', inplace=True)
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
    sku = Monitor_nivelSku(iniVenda)
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
    pedidos["Qtd Atende"] = pedidos.apply(lambda row: row['QtdSaldo']  if row['Necessidade'] <= row['EstoqueLivre'] else 0, axis=1)
    pedidos["Qtd Atende"] = pedidos.apply(lambda row: row['qtdeSugerida'] if row['qtdeSugerida']>0 else row['Qtd Atende'], axis=1)
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
    pedidos['Qtd Atende por Cor'] = pedidos.apply(lambda row: row['Saldo +Sugerido'] if row['Saldo Grade'] == row['X QTDE ATENDE'] else 0, axis=1)
    pedidos['Qtd Atende por Cor'] = pedidos['Qtd Atende por Cor'].astype(int)
    etapa12 = controle.salvarStatus_Etapa12(rotina, ip, etapa11, 'obtendo a Qtd que antende para o pedido baseado no estoque e na grade')#Registrar etapa no controlador


    #13- Indicador de % que fecha no pedido a nivel de grade Pedido||Prod.||Cor'
    #pedidos['% Fecha'] = (pedidos.groupby('Pedido||Prod.||Cor')['Qtd Atende por Cor'].transform('sum')).round(2) / ( pedidos.groupby('codPedido')['Saldo +Sugerido'].transform('sum')).round(2)
    #pedidos['% Fecha'] = pedidos['% Fecha'].round(2)
    #pedidos['% Fecha'] = pedidos['% Fecha'] *100
    pedidos['Fecha Acumulado'] = pedidos.groupby('codPedido')['Qtd Atende por Cor'].cumsum().round(2)
    pedidos['Saldo +Sugerido_Sum'] = pedidos.groupby('codPedido')['Saldo +Sugerido'].transform('sum')
    pedidos['% Fecha Acumulado'] = (pedidos['Fecha Acumulado'] / pedidos['Saldo +Sugerido_Sum']).round(2) * 100
    etapa13 = controle.salvarStatus_Etapa13(rotina, ip, etapa12, ' Indicador de % que fecha no pedido a nivel de grade Pedido||Prod.||Cor')#Registrar etapa no controlador


    # 14 - Encontrando a Marca desejada
    pedidos['codItemPai'] = pedidos['codItemPai'].astype(str)
    pedidos['MARCA'] = pedidos['codItemPai'].apply(lambda x: x[:3])
    pedidos['MARCA'] = numpy.where((pedidos['codItemPai'].str[:3] == '102') | (pedidos['codItemPai'].str[:3] == '202'), 'M.POLLO', 'PACO')
    etapa14 = controle.salvarStatus_Etapa14(rotina, ip, etapa13, ' Encontrando a Marca desejada')#Registrar etapa no controlador

    #15
    # função para verificar a presença de "casa" no valor da coluna "produto"
    categorias = {
        'JAQUETA': 'AGASALHOS',
        'BLUSAO': 'AGASALHOS',
        'TSHIRT': 'CAMISETA',
        'POLO': 'POLO',
        'SUNGA': 'SUNGA',
        'CUECA': 'CUECA',
        'CALCA/BER MOLETOM': 'CALCA/BER MOLETOM',
        'CAMISA': 'CAMISA',
        'SHORT': 'BOARDSHORT',
        'TRICOT': 'TRICOT',
        'BABY': 'CAMISETA',
        'BATA': 'CAMISA',
        'CALCA': 'CALCA/BER MOLETOM',
        'CARTEIRA': 'ACESSORIOS',
        'BONE': 'ACESSORIOS',
        'TENIS': 'CALCADO',
        'CHINELO': 'CALCADO',
        'MEIA': 'ACESSORIOS',
        'BLAZER': 'AGASALHOS',
        'CINTO': 'ACESSORIOS',
        'REGATA': 'ACESSORIOS',
        'BERMUDA': 'CALCA/BER MOLETOM',
        'COLETE': 'AGASALHOS',
        'NECESSA': 'ACESSORIOS',
        'CARTA': 'ACESSORIOS',
        'SACOL': 'ACESSORIOS'
    }

    pedidos['CATEGORIA'] = numpy.where(pedidos['nomeSKU'].str.contains('|'.join(categorias.keys())),
                                    pedidos['nomeSKU'].str.extract('({})'.format('|'.join(categorias.keys())),
                                                                   expand=False).map(categorias), '-')
    etapa15 = controle.salvarStatus_Etapa15(rotina, ip, etapa14, ' Encontrando a categoria do produto')#Registrar etapa no controlador

    # 16- Trazendo as configuracoes de % deistribuido configurado
    dadosConfPer = ConfiguracaoPercEntregas()
    # 16.1 Encontrando o numero restante de entregas
    pedidos['Entregas Restantes'] = pedidos['entregas_Solicitadas'] - pedidos['entregas_enviadas']
    pedidos['Entregas Restantes'] = pedidos.apply(lambda row: 1 if row['entregas_Solicitadas'] <= row['entregas_enviadas'] else row['Entregas Restantes'], axis=1)
    pedidos['Entregas Restantes'] = pedidos['Entregas Restantes'].astype(str)
    pedidos['Entregas Restantes'] = pedidos['Entregas Restantes'].str.replace('.0','')
    pedidos = pd.merge(pedidos, dadosConfPer, on='Entregas Restantes', how='left')
    etapa16 = controle.salvarStatus_Etapa16(rotina, ip, etapa15, 'Encontrando o numero restante de entregas')#Registrar etapa no controlador

    # 17 - Trazendo as configuracoes de categorias selecionadas e aplicando regras de categoria
    dadosCategoria = ConfiguracaoCategoria()
    dadosCategoria = dadosCategoria.rename(columns={'Opção': 'CATEGORIA'})
    pedidos = pd.merge(pedidos,dadosCategoria,on='CATEGORIA',how='left')
    pedidos['Qtd Atende por Cor'] = pedidos.apply(lambda row: row['Qtd Atende por Cor'] if row['Status'] == '1' else 0,axis=1)
    pedidos['Qtd Atende'] = pedidos.apply(lambda row: row['Qtd Atende'] if row['Status'] == '1' else 0,axis=1)
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
    # função para avaliar cada grupo
    def avaliar_grupo(df_grupo):
        if (df_grupo['Distribuicao'] == 'SIM(Redistribuir)').all():
            return 'True'
        if (df_grupo['Distribuicao'] == 'SIM').all():
            return 'True'
        else:
            return 'False'
    df_resultado = pedidos.groupby('Pedido||Prod.||Cor').apply(avaliar_grupo).reset_index()
    df_resultado.rename(columns={0: 'Resultado'}, inplace=True)

    pedidos = pd.merge(pedidos, df_resultado, on='Pedido||Prod.||Cor', how='left')
    pedidos['Distribuicao'] = numpy.where((pedidos['Resultado'] == 'False') &
                                       ((pedidos['Distribuicao'] == 'SIM') & (pedidos['Qtd Atende por Cor'] > 0)),
                                       'SIM(Redistribuir)', pedidos['Distribuicao'])
    etapa19 = controle.salvarStatus_Etapa19(rotina, ip, etapa18, 'Encontrando no pedido o percentual que atende a distribuicao')#Registrar etapa no controlador


    #20- Obtendo valor atente por cor
    pedidos['Valor Atende por Cor'] = pedidos['Qtd Atende por Cor'] * pedidos['PrecoLiquido']
    pedidos['Valor Atende por Cor'] = pedidos['Valor Atende por Cor'].astype(float).round(2)
    etapa20 = controle.salvarStatus_Etapa20(rotina, ip, etapa19, 'Obtendo valor atente por cor')#Registrar etapa no controlador



    #21 Identificando a Quantidade Distribuida
    pedidos['Qnt. Cor(Distrib.)'] = pedidos.apply(lambda row: row['Qtd Atende por Cor'] if row['Distribuicao'] == 'SIM' else 0, axis=1)
    pedidos['Qnt. Cor(Distrib.)'] = pedidos['Qnt. Cor(Distrib.)'].astype(int)
    etapa21 = controle.salvarStatus_Etapa21(rotina, ip, etapa20, 'Obtendo valor atente por cor')#Registrar etapa no controlador


    #22 Obtendo valor atente por cor Distribuida
    pedidos['Valor Atende por Cor(Distrib.)'] = pedidos.apply(lambda row: row['Valor Atende por Cor'] if row['Distribuicao'] == 'SIM' else 0, axis=1)
    pedidos['Valor Atende'] = pedidos['Qtd Atende'] * pedidos['PrecoLiquido']
    pedidos['Valor Atende'] =pedidos['Valor Atende'].astype(float).round(2)
    etapa22 = controle.salvarStatus_Etapa22(rotina, ip, etapa21, 'Obtendo valor atente por cor Distribuida')#Registrar etapa no controlador


    #23- Salvando os dados gerados em csv
    pedidos.to_csv('meutesteMonitor.csv')
    etapa23 = controle.salvarStatus_Etapa23(rotina, ip, etapa22, 'Salvando os dados gerados em csv')#Registrar etapa no controlador



def API(empresa, iniVenda, finalVenda, tiponota):
    pedidos = pd.read_csv('meutesteMonitor.csv')
    pedidos['codPedido'] = pedidos['codPedido'].astype(str)
    pedidos['codCliente'] = pedidos['codCliente'].astype(str)
    pedidos["StatusSugestao"].fillna('-', inplace=True)



    pedidos = pedidos.groupby('codPedido').agg({
    "MARCA": 'first',
    "codTipoNota": 'first',
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

    pedidos = pedidos.sort_values(by='08-vlrSaldo', ascending=False)  # escolher como deseja classificar
    pedidos["10-Entregas Fat"].fillna(0,inplace=True)
    pedidos["09-Entregas Solic"].fillna(0, inplace=True)
    pedidos["11-ultimo fat"].fillna('-', inplace=True)
    pedidos["05-Prev.Atualiz"].fillna('-', inplace=True)

    pedidos["16-Valor Atende por Cor"] =pedidos["16-Valor Atende por Cor"].round(2)
    pedidos["22-Valor Atende por Cor(Distrib.)"] = pedidos["22-Valor Atende por Cor(Distrib.)"].round(2)

    TotalQtdCor = pedidos['15-Qtd Atende p/Cor'].sum()
    TotalValorCor = pedidos['16-Valor Atende por Cor'].sum()
    TotalValorCor = TotalValorCor.round(2)

    TotalQtdCordist = pedidos['21-Qnt Cor(Distrib.)'].sum()
    TotalValorCordist = pedidos['22-Valor Atende por Cor(Distrib.)'].sum()
    TotalValorCordist = TotalValorCordist.round(2)

    dados = {
        '1-Total Qtd Atende por Cor': f'{TotalQtdCor} Pçs',
        '2-Total Valor Valor Atende por Cor': f'{TotalValorCor}',
        '3-Total Qtd Cor(Distrib.)': f'{TotalQtdCordist} Pçs',
        '4-Total Valor Atende por Cor(Distrib.)': f'{TotalValorCordist}',
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
            """Select * from pcp.monitor_check_status """, conn)

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

    if parametro =='Faturamento':
        pedidos['codSitSituacao'] = pedidos.apply(lambda row: '2-InicioFila' if row['codSitSituacao'] == '0' or row['codSitSituacao'] == '1' else '1-FimFila',axis=1)
        pedidos = pedidos.sort_values(by=['codSitSituacao','vlrSaldo'], ascending=False)  # escolher como deseja classificar
        return pedidos
    elif parametro == 'DataPrevisao':
        pedidos['codSitSituacao'] = pedidos.apply(lambda row: '1-InicioFila' if row['codSitSituacao'] == '0' or row['codSitSituacao'] == '1' else '2-FimFila',axis=1)
        pedidos = pedidos.sort_values(by=['codSitSituacao','dataPrevAtualizada'], ascending=True)  # escolher como deseja classificar
        return pedidos


