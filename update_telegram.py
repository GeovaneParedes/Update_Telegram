import os
from pathlib import Path
from pyrogram import Client

# Substitua com suas credenciais solicitadas 
API_ID = 'sua_api_id'
API_HASH = 'sua_api_hash'

# Cria uma instância do cliente
app = Client('my_account', api_id=API_ID, api_hash=API_HASH)

# ID do seu canal (use o ID numérico ou o username com '@')
CHANNEL_ID = '@meu_canal' # ou use um id numérico como -1001234567890

def send_files_from_directory(directory: str):
    # Percorre todos os arquivos na pasta especificada
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Envia o arquivo para o canal
                app.send_document(chat_id=CHANNEL_ID, document=file_path)
                print(f"Enviado: {file_path}")
                
                # Exclui o arquivo local após o envio
                os.remove(file_path)
                print(f"Arquivo excluído: {file_path}")

            except Exception as e:
                print(f"Erro ao enviar {file_path}: {e}")

if __name__ == "__main__":
    # Inicia o cliente
    with app:
        # Solicita ao usuário que insira o caminho da pasta
        folder_path = input("Por favor, digite o caminho da pasta: ")
        
        # Verifica se a pasta existe
        if not os.path.isdir(folder_path):
            print("Caminho inválido. Certifique-se de que a pasta existe.")
        else:
            # Envia os arquivos da pasta para o canal
            send_files_from_directory(folder_path)
