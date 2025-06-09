update_telegram.py

Script para envio automatizado de arquivos de uma pasta local para um canal do Telegram usando Pyrogram.
📦 Descrição

Este script percorre todos os arquivos de uma pasta local especificada pelo usuário, envia cada arquivo como documento para um canal do Telegram e, após o envio, remove o arquivo localmente. É útil para uploads em lote, backup ou automação de distribuição de arquivos via Telegram.
🚀 Instalação

    Clone este repositório ou salve o script update_telegram.py.

    Instale as dependências:

bash
pip install pyrogram tgcrypto

⚙️ Configuração

    Obtenha suas credenciais da API do Telegram:

        Crie uma conta em my.telegram.org.

        Crie um novo aplicativo para obter API_ID e API_HASH.

    Edite o script:

        Substitua 'sua_api_id' e 'sua_api_hash' pelos valores obtidos.

        Defina o CHANNEL_ID com o username do canal (ex: '@meu_canal') ou o ID numérico (ex: -1001234567890).

📝 Uso

Execute o script:

bash
python update_telegram.py

Digite o caminho da pasta quando solicitado. Todos os arquivos encontrados serão enviados para o canal e excluídos localmente após o envio.
📂 Exemplo de Execução

bash
$ python update_telegram.py
Por favor, digite o caminho da pasta: /caminho/para/a/pasta
Enviado: /caminho/para/a/pasta/arquivo1.pdf
Arquivo excluído: /caminho/para/a/pasta/arquivo1.pdf
Enviado: /caminho/para/a/pasta/arquivo2.docx
Arquivo excluído: /caminho/para/a/pasta/arquivo2.docx

🛠️ Como funciona

    Percorre todos os arquivos da pasta informada.

    Envia cada arquivo como documento para o canal do Telegram definido.

    Remove o arquivo localmente após envio com sucesso.

    Exibe mensagens de status e erros no terminal.

⚠️ Atenção

    Todos os arquivos enviados serão excluídos da pasta local.

    Certifique-se de que o usuário/bot utilizado tem permissão para enviar mensagens no canal.

    Use com cautela em pastas com arquivos importantes.

📄 Exemplo de Código

python
import os
from pyrogram import Client

API_ID = 'sua_api_id'
API_HASH = 'sua_api_hash'
app = Client('my_account', api_id=API_ID, api_hash=API_HASH)
CHANNEL_ID = '@meu_canal' # ou -1001234567890

def send_files_from_directory(directory: str):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                app.send_document(chat_id=CHANNEL_ID, document=file_path)
                print(f"Enviado: {file_path}")
                os.remove(file_path)
                print(f"Arquivo excluído: {file_path}")
            except Exception as e:
                print(f"Erro ao enviar {file_path}: {e}")

if __name__ == "__main__":
    with app:
        folder_path = input("Por favor, digite o caminho da pasta: ")
        if not os.path.isdir(folder_path):
            print("Caminho inválido. Certifique-se de que a pasta existe.")
        else:
            send_files_from_directory(folder_path)

📬 Licença

Este projeto está disponível sob a licença MIT.
🤝 Contribuição

Sugestões e melhorias são bem-vindas! Abra uma issue ou 
envie um pull request.
