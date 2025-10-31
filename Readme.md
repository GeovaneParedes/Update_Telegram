update_telegram.py

Script para envio automatizado de arquivos de uma pasta local para um canal do Telegram usando Pyrogram.
📦 Descrição

Este script percorre todos os arquivos de uma pasta local especificada pelo usuário, envia cada arquivo como documento para um canal do Telegram e, após o envio, remove o arquivo localmente. É útil para uploads em lote, backup ou automação de distribuição de arquivos via Telegram.

⚠️ Atenção

    Todos os arquivos enviados serão excluídos da pasta local.

    Certifique-se de que o usuário/bot utilizado tem permissão para enviar mensagens no canal.

    Use com cautela em pastas com arquivos importantes.


📬 Licença

Este projeto está disponível sob a licença MIT.
🤝 Contribuição

Sugestões e melhorias são bem-vindas! Abra uma issue ou 
envie um pull request.

# 🚀 Telegram Batch Sender (with GUI)

## 🎯 Overview

This project provides a robust, GUI-enabled solution for automatically sending local files from a specified directory to a Telegram channel using the [Pyrogram](https://docs.pyrogram.org/) library. After successful transmission, the files are deleted locally.

It is designed following **Clean Code** and **SOLID** principles, separating the business logic (Telegram Client) from the User Interface (Tkinter GUI).

## ✨ Key Features

* **GUI Interface:** Simple and functional interface built with Tkinter for easy folder selection and process monitoring.
* **Secure Configuration:** Uses a `.env` file to manage sensitive API credentials (API_ID, API_HASH).
* **Modular Design:** Separate modules for Telegram API interaction (`telegram_client.py`) and GUI management (`file_sender_app.py`).
* **Efficient Processing:** Uses Python threading to prevent the GUI from freezing during large file uploads.
* **Error Handling:** Robust error management for network issues, Pyrogram RPC errors, and file I/O operations.

## 🛠️ Installation

### Prerequisites

* Python 3.11 or newer (following technical guidelines).

### Steps

1.  **Clone the Repository** (If applicable):
    ```bash
    git clone [your-repository-url]
    cd telegram-batch-sender
    ```

2.  **Install Dependencies:**
    Install the required packages using the senior-standard `requirements.txt` file.
    ```bash
    # Ensure you are using a virtual environment (best practice)
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

To use the sender, you must configure your Telegram API credentials and the target channel ID in a dedicated environment file.

1.  **Obtain API Credentials:**
    * Create a Telegram account and visit [my.telegram.org](https://my.telegram.org/).
    * Create a new application to obtain your `API_ID` and `API_HASH`.

2.  **Create the `.env` File:**
    Create a file named `.env` in the root directory and add the following content, replacing the placeholders with your actual values:
    ```dotenv
    # .env
    API_ID="YOUR_API_ID_HERE"
    API_HASH="YOUR_API_HASH_HERE"
    CHANNEL_ID="@your_channel_username" # Or the numeric ID, e.g., -1001234567890
    ```
    > **Security Note:** Never commit the `.env` file to your version control system (e.g., Git).

## 📝 Usage

### Running the Application

Execute the main application file (`file_sender_app.py`):

```bash
python file_sender_app.py