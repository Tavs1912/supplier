import requests
import pandas as pd
import re

# TOKEN DE EACESSO
TOKEN_DE_ACESSO = '672AE82F-7D82-41F9-A85E-60B63407B11F'

#Verificar a entrada do CNPJ
CNPJ = None
while not CNPJ:
    cnpj = input("Digite o número do CNPJ (somente números): ")
    if re.match("^[0-9]{14}$", cnpj):
        CNPJ = cnpj
    else:
        print("Entrada inválida! Digite apenas 14 números.")

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

else:
    print(f'Erro ao fazer a requisição HTTP. Código de status: {response.status_code}')