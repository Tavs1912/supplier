import requests
import pandas as pd
import re

# TOKEN DE EACESSO
TOKEN_DE_ACESSO = '9CBE472F-A3A4-4FAD-A509-6798668EC7CD'

# Função para consultar o saldo remanescente
def consultar_saldo():
    url_saldo = f'https://www.sintegraws.com.br/api/v1/consulta-saldo.php?token={TOKEN_DE_ACESSO}'
    response_saldo = requests.get(url_saldo)
    
    if response_saldo.status_code == 200:
        data_saldo = response_saldo.json()
        saldo_remanescente = data_saldo['saldo']
        return saldo_remanescente
    else:
        print(f'Erro ao consultar o saldo. Código de status: {response_saldo.status_code}')
        return None


#Função de editar o CNPJ
def format_cnpj(cnpj):
    return re.sub(r'\D', '', cnpj)

#Verificar a entrada do CNPJ
CNPJ = None
while not CNPJ:
    cnpj = input("Digite o número do CNPJ (formato XX.XXX.XXX/XXXX-XX): ")
    CNPJ = format_cnpj(cnpj)
    if len(CNPJ) != 14:
        print("Entrada inválida! Digite exatamente 14 dígitos.")

# Fazer a requisição HTTP para a API
url = f'https://www.sintegraws.com.br/api/v1/execute-api.php?token={TOKEN_DE_ACESSO}&cnpj={CNPJ}&plugin=ST'
response = requests.get(url)

# Verificar se a requisição foi bem sucedida
if response.status_code == 200:
    
    # Extrair as informações do JSON retornado pela API
    data           = response.json()

    # verificar se ele tem cadastro no SINTEGRA
    if data['code'] == "1" or data['situacao_ie'] == 'baixada':
        
        url  = f'https://www.sintegraws.com.br/api/v1/execute-api.php?token={TOKEN_DE_ACESSO}&cnpj={CNPJ}&plugin=RF'
        data = requests.get(url).json()
        
        empresa        = data['nome']
        endereco       = data['logradouro'] + ', ' + data['numero']
        bairro         = data['bairro']
        cnpj           = data['cnpj']
        cep            = data['cep']
        cidade         = data['municipio']
        codigo_cnae    = data['atividade_principal'][0]['code']
        descricao_cnae = data['atividade_principal'][0]['text']

        #criar uma dataframe a partir das informações exatraida.
        df = pd.DataFrame({
                'Empresa': [empresa],
                'Endereço': [endereco],
                'Bairro': [bairro],
                'CNPJ': [cnpj],
                'CEP': [cep],
                'Cidade': [cidade],
                'Inscricao_estadual' : "ISENTO",
                'Codigo_CNAE': [codigo_cnae],
                'Descricao_CNAE': [descricao_cnae],
            })
        
        df['Empresa']   = df['Empresa'].str.upper()
        df['Endereço']  = df['Endereço'].str.upper()
        df['Bairro']    = df['Bairro'].str.upper()
        df['Cidade']    = df['Cidade'].str.upper()
        df['CNPJ']      = df['CNPJ'].apply(lambda x: re.sub(r'\D', '', x))

        df = df.stack().reset_index()
        df.columns = ['Variável', 'Indicador', 'Valor']
        df.to_excel('resultado.xlsx', index=False)

        saldo_remanescente = consultar_saldo(TOKEN_DE_ACESSO)
        if saldo_remanescente is not None:
            print(f'Saldo remanescente:{saldo_remanescente} Unidades'
    
    #Caso tenha o cadastro ele seguirá por esse caminho
    else:
        empresa        = data['nome_empresarial']
        endereco       = data['logradouro'] + ', ' + data['numero']
        bairro         = data['bairro']
        cnpj           = data['cnpj']
        cep            = data['cep']
        cidade         = data['municipio']
        ie             = data['inscricao_estadual']
        codigo_cnae    = data['cnae_principal']['code']
        descricao_cnae = data['cnae_principal']['text']

        # Criar um dataframe com as informações extraídas
        df = pd.DataFrame({
            'Empresa': [empresa],
            'Endereço': [endereco],
            'Bairro': [bairro],
            'CNPJ': [cnpj],
            'CEP': [cep],
            'Cidade': [cidade],
            'I.E': [ie],
            'Codigo_CNAE': [codigo_cnae],
            'Descricao_CNAE': [descricao_cnae],
        })
        
        df['Empresa']   = df['Empresa'].str.upper()
        df['Endereço']  = df['Endereço'].str.upper()
        df['Bairro']    = df['Bairro'].str.upper()
        df['Cidade']    = df['Cidade'].str.upper()

        df = df.stack().reset_index()
        df.columns = ['Variável', 'Indicador', 'Valor']
        df.to_excel('resultado.xlsx', index=False)

        saldo_remanescente = consultar_saldo(TOKEN_DE_ACESSO)
        if saldo_remanescente is not None:
            print(f'Saldo remanescente:{saldo_remanescente} Unidades'
else:
    print(f'Erro ao fazer a requisição HTTP. Código de status: {response.status_code}')
