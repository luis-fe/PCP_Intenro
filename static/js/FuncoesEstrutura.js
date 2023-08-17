let IndiceExibicao = 0;
let TotalPagina;
let PaginaAtual = 1;
const codApi = 'http://192.168.0.183:8000/pcp/api/Estrutura';
let plano = [];

const dados2 = {
  "plano": plano
};

const itensPag = 15;
let TextoLabel = "";
let TextoLabelTamanhos = "";
let TextoLabelMP = "";
let TextoNomeMp = "";
let TextoFornecedor = "";
let TextoDescProduto = "";

function CriarTabelaEstrutura(listaEstrutura) {
    const tabela = document.getElementById('TabelaEstrutura');
    tabela.innerHTML = ''; // Limpa o conteúdo da tabela antes de preenchê-la novamente

    // Cria o cabeçalho da tabela
    const cabecalho = document.createElement('thead');
    const cabecalhoRow = document.createElement('tr');
    const colunaTipo = document.createElement('th');
    const colunaColecao = document.createElement('th');
    const colunaProduto = document.createElement('th');
    inputProduto = document.createElement('input');
    inputProduto.id = 'inputProduto';
    inputProduto.setAttribute('placeholder', TextoLabel)
    inputProduto.addEventListener('keydown', event => FiltroProduto(event))
    const colunaDescricaoProduto = document.createElement('th');
    inputDescProduto = document.createElement('input');
    inputDescProduto.id = 'inputDescProduto';
    inputDescProduto.setAttribute('placeholder', TextoDescProduto)
    inputDescProduto.addEventListener('keydown', event => FiltroDescricao(event))
    const colunaSortimento = document.createElement('th');
    const colunaTamanho = document.createElement('th');
    inputTamanho = document.createElement('input');
    inputTamanho.id = 'inputTamanho';
    inputTamanho.setAttribute('placeholder', TextoLabelTamanhos)
    inputTamanho.addEventListener('keydown', event => FiltroTamanho(event))
    const colunaCorProduto = document.createElement('th');
    const colunaSituacaoCor = document.createElement('th');
    const colunaCodMP = document.createElement('th');
    inputCodMP = document.createElement('input');
    inputCodMP.id = 'inputCodMP';
    inputCodMP.setAttribute('placeholder', TextoLabelMP)
    inputCodMP.addEventListener('keydown', event => FiltroMP(event))
    const colunaTamanhoMP = document.createElement('th');
    const colunaNomeComponente = document.createElement('th');
    inputNomeMp = document.createElement('input');
    inputNomeMp.id = 'inputNomeMP';
    inputNomeMp.setAttribute('placeholder', TextoNomeMp)
    inputNomeMp.addEventListener('keydown', event => FiltroNomeMp(event))
    const colunaCorComponente = document.createElement('th');
    const colunaConsumo = document.createElement('th');
    const colunaFornecedor = document.createElement('th');
    inputFornecedor = document.createElement('input');
    inputFornecedor.id = 'inputFornecedor';
    inputFornecedor.setAttribute('placeholder', TextoFornecedor)
    inputFornecedor.addEventListener('keydown', event => FiltroFornecedor(event))
    const colunaStatusEng = document.createElement('th');
   

    colunaTipo.textContent = 'Tipo Mp';
    colunaColecao.textContent = 'Coleção';
    colunaProduto.textContent = 'Produto';
    colunaDescricaoProduto.textContent = 'Desc. Produto';
    colunaSortimento.textContent = 'Cód. Sortimento';
    colunaTamanho.textContent = 'Tamanho';
    colunaCorProduto.textContent = 'Cor Produto';
    colunaSituacaoCor.textContent = 'Situação Cor';
    colunaCodMP.textContent = 'Cód M.P';
    colunaTamanhoMP.textContent = 'Tamanho M.P';
    colunaNomeComponente.textContent = 'Descrição Componente';
    colunaCorComponente.textContent = 'Cor Componente';
    colunaConsumo.textContent = 'Consumo';
    colunaFornecedor.textContent = 'Fornecedor Principal';
    colunaStatusEng.textContent = 'Status Eng.';
    

    colunaTipo.style.width = '120px';
    colunaColecao.style.width = '100px';
    colunaProduto.style.width = '150px';
    colunaDescricaoProduto.style.width = '800px';
    colunaSituacaoCor.style.width = '100px';
    colunaSortimento.style.width = '200px';
    colunaTamanho.style.width = '120px';
    colunaCorProduto.style.width = '150px';
    colunaCodMP.style.width = '160px';
    colunaTamanhoMP.style.width = '170px';
    colunaNomeComponente.style.width = '750px';
    colunaCorComponente.style.width = '200px';
    colunaConsumo.style.width = '200px';
    colunaFornecedor.style.width = '450px';
    colunaStatusEng.style.width = '200px';

    colunaProduto.appendChild(inputProduto);
    colunaTamanho.appendChild(inputTamanho);
    colunaCodMP.appendChild(inputCodMP);
    colunaFornecedor.appendChild(inputFornecedor);
    colunaNomeComponente.appendChild(inputNomeMp);
    colunaDescricaoProduto.appendChild(inputDescProduto);
    cabecalhoRow.appendChild(colunaTipo);
    cabecalhoRow.appendChild(colunaColecao);
    cabecalhoRow.appendChild(colunaProduto);
    cabecalhoRow.appendChild(colunaDescricaoProduto);
    cabecalhoRow.appendChild(colunaSortimento);
    cabecalhoRow.appendChild(colunaTamanho);
    cabecalhoRow.appendChild(colunaCorProduto);
    cabecalhoRow.appendChild(colunaSituacaoCor);
    cabecalhoRow.appendChild(colunaCodMP);
    cabecalhoRow.appendChild(colunaTamanhoMP);
    cabecalhoRow.appendChild(colunaNomeComponente);
    cabecalhoRow.appendChild(colunaCorComponente);
    cabecalhoRow.appendChild(colunaConsumo);
    cabecalhoRow.appendChild(colunaFornecedor);
    cabecalhoRow.appendChild(colunaStatusEng);
    cabecalho.appendChild(cabecalhoRow);
    tabela.appendChild(cabecalho);
    

    const Teste1 = listaEstrutura.slice(IndiceExibicao, IndiceExibicao + 15);

    // Preenche a tabela com os dados da estrutura
    Teste1.forEach(item => {
        const row = document.createElement('tr');
        const colunaTipo = document.createElement('td');
        const colunaColecao = document.createElement('td');
        const colunaProduto = document.createElement('td');
        const colunaDescricaoProduto = document.createElement('td');
        const colunaSortimento = document.createElement('td');
        const colunaTamanho = document.createElement('td');
        const colunaCorProduto = document.createElement('td');
        const colunaSituacaoCor = document.createElement('td');
        const colunaCodMP = document.createElement('td');
        const colunaTamanhoMP = document.createElement('td');
        const colunaNomeComponente = document.createElement('td');
        const colunaCorComponente = document.createElement('td');
        const colunaConsumo = document.createElement('td');
        const colunaFornecedor = document.createElement('td');
        const colunaStatusEng = document.createElement('td');

        colunaTipo.textContent = item['01- tipo'];
        colunaColecao.textContent = item['02- codColecao'];
        colunaProduto.textContent = item['03- codProduto'];
        colunaDescricaoProduto.textContent = item['15- descricao Produto'];
        colunaSortimento.textContent = item['04- codSortimento'];
        colunaTamanho.textContent = item['05- tamanho'];
        colunaCorProduto.textContent = item['06- corProduto'];
        colunaSituacaoCor.textContent = item['14- situacao cor'];
        colunaCodMP.textContent = item['07- codMP'];
        colunaTamanhoMP.textContent = item['08- TamanhoMP'];
        colunaNomeComponente.textContent = item['09- nomeComponente'];
        colunaCorComponente.textContent = item['10- corComponente'];
        colunaConsumo.textContent = item['11- Consumo'];
        colunaFornecedor.textContent = item['12-nomeFornecedor'];
        colunaStatusEng.textContent = item['13-statusEng'];

        row.appendChild(colunaTipo);
        row.appendChild(colunaColecao);
        row.appendChild(colunaProduto);
        row.appendChild(colunaDescricaoProduto);
        row.appendChild(colunaSortimento);
        row.appendChild(colunaTamanho);
        row.appendChild(colunaCorProduto);
        row.appendChild(colunaSituacaoCor);
        row.appendChild(colunaCodMP);
        row.appendChild(colunaTamanhoMP);
        row.appendChild(colunaNomeComponente);
        row.appendChild(colunaCorComponente);
        row.appendChild(colunaConsumo);
        row.appendChild(colunaFornecedor);
        row.appendChild(colunaStatusEng);
        tabela.appendChild(row);
    });
    
    }

      let LabelProdutos = document.getElementById('LabelProdutos');
      let LabelTamanhos = document.getElementById('LabelTamanhos');
      let LabelMP = document.getElementById('LabelMP');
      let LabelNomeMp = document.getElementById('LabelNomeMp');
      let LabelFornecedor = document.getElementById('LabelFornecedor');
      let LabelDescProduto = document.getElementById('LabelDescProduto');

      function FiltroProduto(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const FiltroProduto1 = inputProduto.value;
            console.log(FiltroProduto1);
            LabelProdutos.textContent = FiltroProduto1;
            TextoLabel = LabelProdutos.textContent;
            inputProduto.placeholder = TextoLabel;
            PaginaAtual = 1;
            botaoProximo1.disabled = false;
            const dadosEngenharia = {
            "plano": plano,
            "pagina": 1,
            "itensPag": 15,
            "codEngenharias": TextoLabel,
            "TamanhoProduto": TextoLabelTamanhos,
            "codMP": TextoLabelMP,
            "nomeComponente": TextoNomeMp,
            "nomeFornecedor": TextoFornecedor,
            "desproduto": TextoFornecedor
            }
            (dadosEngenharia)  
        }
      }
      function FiltroTamanho(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const FiltroTamanho1 = inputTamanho.value;
            console.log(FiltroTamanho1);
            LabelTamanhos.textContent = FiltroTamanho1;
            PaginaAtual = 1
            botaoProximo1.disabled = false
            TextoLabelTamanhos = LabelTamanhos.textContent;
            const dadosTamanho = {
            "plano": plano,
            "pagina": 1,
            "itensPag": 15,
            "codEngenharias": TextoLabel,
            "TamanhoProduto": TextoLabelTamanhos,
            "codMP": TextoLabelMP,
            "nomeComponente": TextoNomeMp,
            "nomeFornecedor": TextoFornecedor,
            "desproduto": TextoFornecedor
            }
            CarregarDados(dadosTamanho)  
        }
      };


      function FiltroMP(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const FiltroMP1 = inputCodMP.value;
            console.log(FiltroMP1);
            LabelMP.textContent = FiltroMP1;
            PaginaAtual = 1
            botaoProximo1.disabled = false
            TextoLabelMP = LabelMP.textContent;
            const dadosMP = {
            "plano": plano,
            "pagina": 1,
            "itensPag": 15,
            "codEngenharias": TextoLabel,
            "TamanhoProduto": TextoLabelTamanhos,
            "codMP": TextoLabelMP,
            "nomeComponente": TextoNomeMp,
            "nomeFornecedor": TextoFornecedor,
            "desproduto": TextoFornecedor
            }
            CarregarDados(dadosMP)  
        }
      };

      function FiltroNomeMp(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const FiltroNomeMP1 = inputNomeMp.value;
            console.log(FiltroNomeMP1);
            LabelNomeMp.textContent = FiltroNomeMP1;
            PaginaAtual = 1
            botaoProximo1.disabled = false
            TextoNomeMp = LabelNomeMp.textContent;
            const dadosNomeMP = {
            "plano": plano,
            "pagina": 1,
            "itensPag": 15,
            "codEngenharias": TextoLabel,
            "TamanhoProduto": TextoLabelTamanhos,
            "codMP": TextoLabelMP,
            "nomeComponente": TextoNomeMp,
            "nomeFornecedor": TextoFornecedor,
            "desproduto": TextoFornecedor
            }
            CarregarDados(dadosNomeMP)  
        }
      }

      function FiltroFornecedor(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const FiltroFornecedor1 = inputFornecedor.value;
            console.log(FiltroFornecedor1);
            LabelFornecedor.textContent = FiltroFornecedor1;
            PaginaAtual = 1
            botaoProximo1.disabled = false
            TextoFornecedor = LabelFornecedor.textContent;
            const dadosFornecedor = {
            "plano": plano,
            "pagina": 1,
            "itensPag": 15,
            "codEngenharias": TextoLabel,
            "TamanhoProduto": TextoLabelTamanhos,
            "codMP": TextoLabelMP,
            "nomeComponente": TextoNomeMp,
            "nomeFornecedor": TextoFornecedor,
            "desproduto": TextoFornecedor
            }
            CarregarDados(dadosFornecedor)  
        }
      }

      function FiltroDescricao(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const FiltroDescricao1 = inputDescProduto.value;
            console.log(FiltroDescricao1);
            LabelDescProduto.textContent = FiltroDescricao1;
            PaginaAtual = 1
            botaoProximo1.disabled = false
            TextoDescProduto = LabelDescProduto.textContent;
            const dadosDesc = {
            "plano": plano,
            "pagina": 1,
            "itensPag": 15,
            "codEngenharias": TextoLabel,
            "TamanhoProduto": TextoLabelTamanhos,
            "codMP": TextoLabelMP,
            "nomeComponente": TextoNomeMp,
            "nomeFornecedor": TextoFornecedor,
            "desproduto": TextoDescProduto

            }
            CarregarDados(dadosDesc)  
        }
      }


    

    const labelPagina1 = document.getElementById('LabelContagemPagina1')
    const modalLoading = document.getElementById("ModalLoading");


    function AbrirModalLoading() {
      modalLoading.style.display = "block";
    }
    
    // Função para fechar a modal de carregamento
    function FecharModalLoading() {
      modalLoading.style.display = "none";
      document.getElementById('ImagemLoading').value = '';
    }

    // Função para carregar dados iniciais
    function CarregarDados(dados) {
  

      AbrirModalLoading()

      fetch(codApi, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'a44pcp22'
        },
        body: JSON.stringify(dados),
      })
        .then(response => {
          if (response.ok) {
            return response.json();
          } else {
            FecharModalLoading();
            alert("Não foi possível carregar a Estrutura! Procure o Administrador!")
          }
        })
        .then(data => {
          const detalhamentoCurva = data[0]["0-numero de paginas"];
          const detalhamentoEstrutura = data[0]['1- Detalhamento da Estrutura:'];
          TotalPagina = detalhamentoCurva
          labelPagina1.textContent = `Página ${PaginaAtual} de ${TotalPagina}`;
          LabelProdutos.textContent = ""
          FecharModalLoading();
          CriarTabelaEstrutura(detalhamentoEstrutura);
        })
        .catch(error => {
          console.error(error);
          // Ocultar a imagem de carregamento após a chamada da API terminar (seja sucesso ou erro)
        });
    }


    function AtualizarTabelaEstrutura(listaEstrutura) {
      const tabela = document.getElementById('TabelaEstrutura');
      const linhas = tabela.getElementsByTagName('tr');
      // Remove todas as linhas, exceto a primeira (cabeçalho)
      while (linhas.length > 1) {
          tabela.deleteRow(1);
      }
      // Cria e preenche a tabela com os dados atualizados
      CriarTabelaEstrutura(listaEstrutura);
  }

  function carregarProximosUsuarios() {
    if (PaginaAtual + 1 <= TotalPagina) {
        IndiceExibicao = 0;
        PaginaAtual = PaginaAtual + 1;
        TextoLabel = LabelProdutos.textContent;
        const dados1 = {
            "plano": plano,
            "pagina": PaginaAtual,
            "itensPag": 15,
            "codEngenharias": TextoLabel,
            "TamanhoProduto": TextoLabelTamanhos,
            "codMP": TextoLabelMP,
            "nomeComponente": TextoNomeMp,
            "nomeFornecedor": TextoFornecedor,
            "desproduto": TextoDescProduto
        };
        CarregarDados(dados1);
    }
    // Desabilita o botão "Próxima página" se a próxima página for maior que o total de páginas
    if (PaginaAtual + 1 > TotalPagina) {
        botaoProximo1.disabled = true;
    } else {
        botaoProximo1.disabled = false;
    }
}

function carregarUsuariosAnteriores() {
  if (PaginaAtual > 1) {
      IndiceExibicao = 0;
      PaginaAtual = PaginaAtual - 1;
      TextoLabel = LabelProdutos.textContent;
      const dados1 = {
          "plano": plano,
          "pagina": PaginaAtual,
          "itensPag": 15,
          "codEngenharias": TextoLabel,
          "TamanhoProduto": TextoLabelTamanhos,
          "codMP": TextoLabelMP,
          "nomeComponente": TextoNomeMp,
          "nomeFornecedor": TextoFornecedor,
          "desproduto": TextoDescProduto
      };
      CarregarDados(dados1);
  }
  // Desabilita o botão "Próxima página" se a página atual for 1
  if (PaginaAtual < 1) {
      botaoAnterior1.disabled = true;
      botaoProximo1.disabled = false;
  } else {
    botaoAnterior1.disabled = false;
    botaoProximo1.disabled = false;
  }
}


function CarregarUltimaPagina() {
  TotalPagina = parseInt(TotalPagina)
  if (PaginaAtual <= TotalPagina) {
      IndiceExibicao = 0;
      PaginaAtual = TotalPagina;
      TextoLabel = LabelProdutos.textContent;
      const dados1 = {
          "plano": plano,
          "pagina": TotalPagina,
          "itensPag": 15,
          "codEngenharias": TextoLabel,
          "TamanhoProduto": TextoLabelTamanhos,
          "codMP": TextoLabelMP,
          "nomeComponente": TextoNomeMp,
          "nomeFornecedor": TextoFornecedor,
          "desproduto": TextoDescProduto
      };
      CarregarDados(dados1);
  }
  // Desabilita o botão "Próxima página" se a próxima página for maior que o total de páginas
  if (PaginaAtual > TotalPagina) {
      botaoProximo1.disabled = true;
      UltimaPagina1.disabled = true;
  } else {
      botaoProximo1.disabled = false;
      UltimaPagina1.disabled = false;
  }
}

function CarregarPrimeiraPagina() {
  if (PaginaAtual > 1) {
    IndiceExibicao = 0;
    PaginaAtual = 1;
    TextoLabel = LabelProdutos.textContent;
    const dados1 = {
        "plano": plano,
        "pagina": PaginaAtual,
        "itensPag": 15,
        "codEngenharias": TextoLabel,
        "TamanhoProduto": TextoLabelTamanhos,
        "codMP": TextoLabelMP,
        "nomeComponente": TextoNomeMp,
        "nomeFornecedor": TextoFornecedor,
        "desproduto": TextoDescProduto
    };
    CarregarDados(dados1);
}

// Desabilita o botão "Próxima página" se a página atual for 1
if (PaginaAtual < 1) {
    botaoAnterior1.disabled = true;
    PrimeiraPagina.disabled = true;
} else {
  botaoAnterior1.disabled = false;
  PrimeiraPagina.disabled = false;
}
}


    const botaoProximo1 = document.getElementById('ButtonProximaPagina1');
    botaoProximo1.addEventListener('click', carregarProximosUsuarios);

    const botaoAnterior1 = document.getElementById('ButtonPaginaAnterior1');
    botaoAnterior1.addEventListener('click', carregarUsuariosAnteriores);

    const UltimaPagina1 = document.getElementById('ButtonUltimaPagina1');
    UltimaPagina1.addEventListener('click', CarregarUltimaPagina);

    const PrimeiraPagina = document.getElementById('ButtonPrimeiraPagina1');
    PrimeiraPagina.addEventListener('click', CarregarPrimeiraPagina);



    //------------------------------------------------- FUNÇÃO EXCEL ----------------------------------------------------------------//

    const ApiEstrutura = 'http://192.168.0.183:8000/pcp/api/Estrutura';
    

    
    
    function exportarParaExcel() {
      TextoLabel = LabelProdutos.textContent
      TextoLabelTamanhos = LabelTamanhos.textContent
      TextoLabelMP = TextoLabelMP.textContent
      TextoNomeMp = TextoNomeMp.textContent


      const dadosParaExportar = {
        "plano": inputPlano.value,
        "Excel": true,
        "codEngenharias": TextoLabel,
        "TamanhoProduto": TextoLabelTamanhos,
        "codMP": TextoLabelMP,
        "nomeComponente": TextoNomeMp,
        "nomeFornecedor": TextoFornecedor,
        "desproduto": TextoDescProduto
      };

      fetch(ApiEstrutura, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'a44pcp22'
        },
        body: JSON.stringify(dadosParaExportar),
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Erro ao obter os dados da API');
        }
      })
      .then(data => {
        const detalhamentoEstrutura = data[0]['1- Detalhamento da Estrutura:'];
        
        
        // Verificar se os dados foram obtidos corretamente
        if (!detalhamentoEstrutura || detalhamentoEstrutura.length === 0) {
          throw new Error('Não há dados para exportar.');
        }
        
        const nomeArquivo = 'Estrutura de Produtos.xlsx';
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.json_to_sheet(detalhamentoEstrutura);
        
        // Adicionar a planilha ao workbook
        XLSX.utils.book_append_sheet(wb, ws, 'Dados Estrutura');
    
        // Salvar o arquivo
        XLSX.writeFile(wb, nomeArquivo);
      })
      .catch(error => {
        console.error(error);
      });
    }

    const botaoExportarExcel = document.getElementById('ButtonExportarExcel1');
    botaoExportarExcel.addEventListener('click', () => exportarParaExcel());
    
    //------------------------------------------------SELECIONANDO PLANO--------------------------------------------------------------//



    function ConsultaPlanosExistentes() {
      fetch(`http://192.168.0.183:8000/pcp/api/Plano`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'a44pcp22'
        },
      })
        .then(response => {
          if (response.ok) {
            return response.json();
          } else {
            console.log(response);
            throw new Error('Erro ao obter a lista de usuários');
          }
        })
        .then(data => {
          criarTabelaPlanos(data)
          console.log(data);
        })
        .catch(error => {
          console.error('Erro capturado:', error);
        });
    }
  
  
  function criarTabelaPlanos(listaPlanos) {
      const tabelaPlanos = document.getElementById('TabelaPlanos2');
      tabelaPlanos.innerHTML = '';
  
      const cabecalho = document.createElement('thead');
      const cabecalhoRow = document.createElement('tr');
      const colunaCheckboxPlanos = document.createElement('th');
      const ColunaCodigoPlano= document.createElement('th');
      const ColunaDescricaoPlanos = document.createElement('th');
  
      colunaCheckboxPlanos.textContent = '';
      ColunaCodigoPlano.textContent = 'Código';
      ColunaDescricaoPlanos.textContent = 'Descrição';
  
      cabecalhoRow.appendChild(colunaCheckboxPlanos);
      cabecalhoRow.appendChild(ColunaCodigoPlano);
      cabecalhoRow.appendChild(ColunaDescricaoPlanos);
      cabecalho.appendChild(cabecalhoRow);
      tabelaPlanos.appendChild(cabecalho);
  
      listaPlanos.forEach(item => {
          const row = document.createElement('tr');
          const colunaCheckboxPlanos = document.createElement('td');
          const ColunaCodigoPlano = document.createElement('td');
          const ColunaDescricaoPlanos = document.createElement('td');
  
          const checkboxPlanos = document.createElement('input');
          checkboxPlanos.type = 'checkbox';
          checkboxPlanos.value = item["01- Codigo Plano"];
          checkboxPlanos.name = 'checkboxPlanos';
          colunaCheckboxPlanos.appendChild(checkboxPlanos);
          ColunaCodigoPlano.textContent = item["01- Codigo Plano"];
          ColunaDescricaoPlanos.textContent = item["02- Descricao do Plano"];
  
          row.appendChild(colunaCheckboxPlanos);
          row.appendChild(ColunaCodigoPlano);
          row.appendChild(ColunaDescricaoPlanos);
  
          tabelaPlanos.appendChild(row);
      });
  }
  
  

  const modalPlanos = document.getElementById('modalSelecionarPlano');
  const fecharModalPlanos1 = document.getElementById('fecharModalSelecaoPlanos');
  
  function abrirModalPlano(){
    ConsultaPlanosExistentes();
    modalPlanos.style.display = 'block';
  };

  
  fecharModalPlanos1.addEventListener('click', function() {
    modalPlanos.style.display = 'none';
  });
  
  
  const botaoSelecionarPlano = document.getElementById('botaoSelecionarPlano2')
  
  botaoSelecionarPlano.addEventListener('click', function() {
  const LinhasTabelaPlano = document.getElementById('TabelaPlanos2').getElementsByTagName('tr');

  
      for (let i = 1; i < LinhasTabelaPlano.length; i++) {
          const linha2 = LinhasTabelaPlano[i];
          const checkboxPlanoSelecionado = linha2.querySelector('input[type="checkbox"]');
  
          if (checkboxPlanoSelecionado.checked) {
              const colunasPlanoSelecionado = linha2.getElementsByTagName('td');
              const Plano = colunasPlanoSelecionado[1].textContent.trim();
  
              plano = Plano
          }
      }
  
      if (plano.length === 0) {
          alert('Nenhuma Coleção selecionada');
          modalColecoes.style.display = 'none';
          modalColecoes.style.display = 'block';
      } else {
          let passandoDados = {
              "plano": plano
          };
          console.log(plano)
          inputPlano.value = plano;
          CarregarDados(passandoDados)
  
          
      }
  
      modalPlanos.style.display = 'none';
  });



  const BotaoPesquisaPlano = document.getElementById("ButtonPesquisaPlanoEstrutura");
  
  
  BotaoPesquisaPlano.addEventListener('click', function () {
      console.log("botão clicado")
      modalPlanos.style.display = "flex";
      ConsultaPlanosExistentes();
  });


  const inputPlano = document.getElementById("InputCodPlanoEstrutura");

  inputPlano.addEventListener("keydown", event => {
    const dadosIniciais = {
        "plano": inputPlano.value,
        "itensPag": 15
    };
    if (event.key === "Enter") {
        event.preventDefault(); // Impede o comportamento padrão de submit de formulário
        console.log("teste")
        CarregarDados(dadosIniciais);
    }

});



