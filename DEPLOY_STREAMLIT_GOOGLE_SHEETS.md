# Publicar o TCC com link fixo e respostas online

Este app está pronto para publicar no Streamlit Community Cloud e salvar as respostas em uma planilha Google Sheets.

## 1. Criar a planilha

1. Crie uma planilha no Google Sheets.
2. Nomeie uma aba como `respostas`.
3. Copie o ID da planilha pela URL:

```text
https://docs.google.com/spreadsheets/d/ESTE_E_O_ID_DA_PLANILHA/edit
```

## 2. Criar credenciais Google

1. Acesse `https://console.cloud.google.com/`.
2. Crie um projeto.
3. Ative a API `Google Sheets API`.
4. Crie uma `Service Account`.
5. Gere uma chave JSON dessa Service Account.
6. Copie o e-mail da Service Account, algo como:

```text
nome-da-conta@nome-do-projeto.iam.gserviceaccount.com
```

7. Compartilhe a planilha com esse e-mail como `Editor`.

## 3. Publicar no Streamlit Cloud

1. Coloque `app.py` e `requirements.txt` em um repositório no GitHub.
2. Acesse `https://share.streamlit.io/`.
3. Clique em `New app`.
4. Selecione seu repositório.
5. Em `Main file path`, use:

```text
app.py
```

6. Antes de rodar, abra `Advanced settings` ou `Secrets`.
7. Cole os secrets abaixo, preenchendo com os dados do JSON baixado e o ID da planilha.

```toml
[google_sheets]
spreadsheet_id = "COLE_AQUI_O_ID_DA_PLANILHA"
worksheet_name = "respostas"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

## 4. Onde ver os resultados

Depois que alguém finalizar a pesquisa, uma nova linha será adicionada automaticamente na aba `respostas`.

Se os secrets não forem configurados, o app salva localmente em `dados_tcc_final.csv`.
