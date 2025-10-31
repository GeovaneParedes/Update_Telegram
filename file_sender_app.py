#!/usr/bin/env python3
"""
Aplicativo Tkinter para enviar arquivos de uma pasta para um canal do Telegram usando Telethon.
Inclui tratamento de erros, log de atividades e execução em thread separada para manter a GUI responsiva.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dotenv import load_dotenv
import os
from threading import Thread
from telethon import TelegramClient
import asyncio # Necessário para criar o loop de eventos na thread

# Importações FINAIS Corrigidas
from telethon.errors import (
    SessionPasswordNeededError, 
    ChannelPrivateError, 
    PeerIdInvalidError, 
    RPCError 
)


# Carrega as variáveis de ambiente
load_dotenv()

# Configurações explícitas
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
CHANNEL_ID = os.getenv('CHANNEL_ID') 

SESSION_NAME = 'telethon_session' # Nome do arquivo de sessão

class App(tk.Tk):
    """
    Interface Gráfica com Tkinter e lógica de envio Telethon integrada.
    """

    def _run_async_in_thread(self, folder_path):
        """
        Cria e executa um novo event loop para a thread de background.
        Esta é a correção para o erro 'RuntimeError: no current event loop'.
        """
        # 1. Cria um novo loop específico para esta thread
        loop = asyncio.new_event_loop()
        
        # 2. Define o novo loop como o loop atual para esta thread
        asyncio.set_event_loop(loop)
        
        try:
            # 3. Executa a função assíncrona run_sending_logic dentro do loop
            loop.run_until_complete(self.run_sending_logic(folder_path))
        except Exception as e:
            # Captura qualquer erro na thread e o loga na GUI
            self.after(0, lambda: messagebox.showerror("Erro Crítico da Thread", str(e)))
        finally:
            # 4. Finaliza e fecha o loop ao concluir
            loop.close()

    def start_sending_thread(self):
        """Inicia o processo de envio na thread separada."""
        folder_path = self.path_entry.get().strip()
        
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Erro de Validação", "Caminho da pasta inválido ou vazio.")
            return

        # Prepara a GUI
        self.send_button.configure(state="disabled", text="ENVIANDO...")
        self.progress_bar.start(10)
        self._append_to_log("--- Iniciando Envio ---")
        self._append_to_log(f"Enviando para o canal: {self.channel_id}\n")
        
        # A chamada CORRIGIDA para iniciar a thread
        threading_target = lambda: self._run_async_in_thread(folder_path)
        Thread(target=threading_target, daemon=True).start()
    
    def __init__(self):
        super().__init__()
        self.title("Telegram File Sender (Telethon - Tkinter)")
        self.geometry("600x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Teste de Configuração: Padrão Sênior
        if not all([API_ID, API_HASH, CHANNEL_ID]):
             messagebox.showerror("Erro de Configuração", "API_ID, API_HASH ou CHANNEL_ID estão faltando no .env.")
             self.destroy() 
             return
            
        # Inicializa o cliente Telethon
        self.client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
        self.channel_id = CHANNEL_ID 

        self._setup_widgets()
        
    def _setup_widgets(self):
        """Cria e posiciona todos os widgets da interface."""
        
        path_frame = ttk.Frame(self, padding="10")
        path_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        path_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(path_frame, text="Pasta a Enviar:").grid(row=0, column=0, sticky="w")
        
        self.path_entry = ttk.Entry(path_frame, width=50)
        self.path_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        browse_button = ttk.Button(path_frame, text="Procurar...", command=self.browse_folder)
        browse_button.grid(row=1, column=1, sticky="e")
        
        self.send_button = ttk.Button(self, text="▶ INICIAR ENVIO E EXCLUSÃO", 
                                      command=self.start_sending_thread)
        self.send_button.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(self, mode='indeterminate', length=580)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Label(self, text="Log de Atividades:").grid(row=3, column=0, sticky="sw", padx=10)
        
        self.log_textbox = tk.Text(self, state="disabled", height=10, wrap=tk.WORD)
        self.log_textbox.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(self, command=self.log_textbox.yview)
        scrollbar.grid(row=4, column=0, sticky='nse')
        self.log_textbox['yscrollcommand'] = scrollbar.set

    def browse_folder(self):
        """Abre a caixa de diálogo para seleção de pasta."""
        folder_selected = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if folder_selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_selected)

    def log_update(self, file_path: str, status: str):
        """Atualiza o log de atividades na GUI, garantindo segurança entre threads."""
        log_message = f"[{os.path.basename(file_path)}] -> {status}\n"
        self.after(0, self._append_to_log, log_message)

    def _append_to_log(self, message: str):
        """Função que realmente manipula o widget Text na thread principal."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert(tk.END, message)
        self.log_textbox.see(tk.END)
        self.log_textbox.configure(state="disabled")

    # --- Lógica principal de envio (ASYNCRONA) ---
    async def run_sending_logic(self, directory: str):
        """Lógica que interage com o Telethon (ASYNCRONA)."""
        
        failed_files = []
        
        try:
            # 1. Conecta e Autentica
            await self.client.start()
            
            # Autenticação 
            if not await self.client.is_user_authorized():
                self.log_update("ATENÇÃO", "Sessão não autorizada. Rode o script de login.")
                raise SessionPasswordNeededError("Sessão não autorizada. Autentique o arquivo de sessão.")

            self.log_update("Conexão", f"Sessão iniciada como: {(await self.client.get_me()).username}")
            
            # 2. Resolução do Peer (Identificar o canal)
            entity = await self.client.get_entity(self.channel_id)
            self.log_update("DEBUG", f"Peer Resolvido. ID: {entity.id}")
            
            # 3. Percorre a pasta
            for root, _, files in os.walk(directory):
                
                total_files = len(files)
                if total_files > 0:
                    self.log_update("DEBUG", f"Encontrados {total_files} arquivos em: {os.path.basename(root)}")
                
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        # 4. Tenta enviar o documento (Telethon's send_file)
                        await self.client.send_file(entity, file=file_path)
                        
                        # 5. Exclui o arquivo
                        os.remove(file_path)
                        status = "Enviado e excluído com sucesso."
                        
                    except RPCError as e:
                        # RPCError captura FileReferenceError, TimedOut, etc.
                        status = f"Erro RPC (Telegram) CODE {e.code}: {e.message}"
                        failed_files.append(file_path)
                    except (FileNotFoundError, PermissionError) as e:
                        status = f"Erro Local: {type(e).__name__} (Leitura/Exclusão)."
                        failed_files.append(file_path)
                    except Exception as e:
                        status = f"Erro Geral: {type(e).__name__} - {e}"
                        failed_files.append(file_path)
                    
                    finally:
                        self.log_update(os.path.basename(file_path), status)

        # 6. Captura de Erros Críticos
        except SessionPasswordNeededError as e:
            self.after(0, lambda: messagebox.showerror("Erro de Autenticação", f"Autenticação de 2FA necessária! {e}"))
        except (PeerIdInvalidError, ChannelPrivateError) as e:
            self.after(0, lambda: messagebox.showerror("Erro de ID/Permissão", f"Falha ao encontrar o canal {self.channel_id}. {e}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro Inesperado Crítico", f"Ocorreu um erro crítico: {type(e).__name__} - {e}"))
            
        finally:
            # Encerra a conexão e agenda o reset da GUI
            await self.client.disconnect()
            self.after(0, self._reset_gui)
            
    def _reset_gui(self):
        """Restaura o estado inicial da GUI para permitir um novo envio."""
        self.progress_bar.stop()
        
        # 1. Restaura o botão e o estado
        self.send_button.configure(state="normal", text="▶ INICIAR ENVIO E EXCLUSÃO")
        
        # 2. Adiciona a mensagem final para indicar que está pronto
        self._append_to_log("\n--- APLICAÇÃO PRONTA PARA NOVO ENVIO ---")
        
        # 3. Força o Tkinter a redesenhar e processar eventos (CRUCIAL!)
        self.update_idletasks()


if __name__ == '__main__':
    # Telethon requer que o API_ID seja int
    try:
        int(API_ID)
    except (TypeError, ValueError):
        print("Erro: API_ID deve ser um número inteiro no arquivo .env.")
        exit(1)

    app = App()
    app.mainloop()