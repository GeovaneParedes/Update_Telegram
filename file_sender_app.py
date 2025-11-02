#!/usr/bin/env python3
"""
Aplicativo Tkinter para enviar arquivos de uma pasta para um canal do Telegram usando Telethon.
Inclui tratamento de erros, log de atividades e execução em thread separada para manter a GUI responsiva.
"""
# file_sender_app.py (Versão Final com Progresso e Callback)
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dotenv import load_dotenv
import os
from threading import Thread
from telethon import TelegramClient
import asyncio
from telethon.errors import (
    SessionPasswordNeededError, 
    ChannelPrivateError, 
    PeerIdInvalidError, 
    RPCError, 
    TimeoutError
)

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações explícitas
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
CHANNEL_ID = os.getenv('CHANNEL_ID') 

SESSION_NAME = 'telethon_session' 

class App(tk.Tk):
    """
    Interface Gráfica com Tkinter e lógica de envio Telethon integrada.
    """

    def _run_async_in_thread(self, folder_path):
        """
        Cria e executa um novo event loop para a thread de background.
        """
        import asyncio
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.run_sending_logic(folder_path))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro Crítico da Thread",
                                                        str(e)))
        finally:
            loop.close()

    def start_sending_thread(self):
        """Inicia o processo de envio na thread separada."""
        folder_path = self.path_entry.get().strip()
        
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Erro de Validação", 
                                 "Caminho da pasta inválido ou vazio.")
            return

        # Zera o contador de progresso
        self.files_sent = 0
        self.total_files = 0
        self.progress_bar.config(value=0, mode='indeterminate') # Volta para indeterminado durante a busca
        self.progress_label.config(text="Aguardando conexão...")
        
        # Prepara a GUI
        self.send_button.config(state="disabled", text="ENVIANDO...")
        self.progress_bar.start(10)
        self._append_to_log("--- Iniciando Envio ---")
        self._append_to_log(f"Enviando para o canal: {self.channel_id}\n")
        
        # A chamada CORRIGIDA para iniciar a thread
        threading_target = lambda: self._run_async_in_thread(folder_path)
        Thread(target=threading_target, daemon=True).start()
    
    def __init__(self):
        super().__init__()
        self.title("Telegram File Sender (Telethon - Tkinter)")
        self.geometry("600x450") # Aumentado para caber o label de progresso
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        # Variáveis de Progresso
        self.files_sent = 0
        self.total_files = 0
        
        if not all([API_ID, API_HASH, CHANNEL_ID]):
             messagebox.showerror("Erro de Configuração", 
                      "API_ID, API_HASH ou CHANNEL_ID estão faltando no .env.")
             self.destroy() 
             return
            
        self.client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
        self.channel_id = CHANNEL_ID 

        self._setup_widgets()
        
    def _setup_widgets(self):
        """Cria e posiciona todos os widgets da interface."""
        
        path_frame = ttk.Frame(self, padding="10")
        path_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        path_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(path_frame, text="Pasta a Enviar:").grid(row=0, column=0, 
                                                           sticky="w")
        
        self.path_entry = ttk.Entry(path_frame, width=50)
        self.path_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        browse_button = ttk.Button(path_frame, text="Procurar...", 
                                   command=self.browse_folder)
        browse_button.grid(row=1, column=1, sticky="e")
        
        self.send_button = ttk.Button(self, text="▶ INICIAR ENVIO E EXCLUSÃO", 
                                      command=self.start_sending_thread)
        self.send_button.grid(row=2, column=0, sticky="ew", padx=10, pady=5) # Ajustado para row 2
        
        # Novo Label para mostrar a porcentagem
        self.progress_label = ttk.Label(self, text="Status: Aguardando...", 
                                        anchor='w')
        self.progress_label.grid(row=3, column=0, sticky="ew", padx=10, 
                                 pady=(5, 2))
        
        # Barra de progresso determinada
        self.progress_bar = ttk.Progressbar(self, mode='determinate', 
                                            length=580)
        self.progress_bar.grid(row=4, column=0, sticky="ew", padx=10, 
                               pady=(0, 10)) # Ajustado para row 4
        
        # Logs
        ttk.Label(self, text="Log de Atividades:").grid(row=5, column=0, 
                                                        sticky="sw", padx=10)
        
        self.log_textbox = tk.Text(self, state="disabled", height=10, 
                                   wrap=tk.WORD)
        self.log_textbox.grid(row=6, column=0, sticky="nsew", padx=10, 
                              pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(self, command=self.log_textbox.yview)
        scrollbar.grid(row=6, column=0, sticky='nse')
        self.log_textbox['yscrollcommand'] = scrollbar.set

    def browse_folder(self):
        """Abre a caixa de diálogo para seleção de pasta."""
        folder_selected = filedialog.askdirectory(
            initialdir=os.path.expanduser("~"))
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

    def send_file_callback(self, current, total):
        """
        Callback do Telethon: Atualiza o progresso do ARQUIVO atual.
        current: bytes transferidos, total: bytes totais do arquivo.
        """
        if total > 0:
            file_percent = int(current * 100 / total)
            
            # Cálculo do progresso GERAL: (Arquivos enviados + progresso do arquivo atual)
            if self.total_files > 0:
                total_progress = ((self.files_sent) / self.total_files) * 100
                total_progress += (file_percent / self.total_files)
                
                # Atualização da GUI
                self.after(0, self.progress_bar.config, {'value': total_progress})
                self.after(0, self.progress_label.config, 
                           {'text': f"Transferindo Arquivo: {file_percent}%" 
                            f"| Progresso Total: {int(total_progress)}%" 
                            f"({self.files_sent}/{self.total_files})"})
            
    # --- Lógica principal de envio (ASYNCRONA) ---
    async def run_sending_logic(self, directory: str):
        """Lógica que interage com o Telethon (ASYNCRONA)."""
        
        failed_files = []
        
        try:
            # 1. Conecta e Autentica
            await self.client.start()
            
            if not await self.client.is_user_authorized():
                self.log_update(
                    "ATENÇÃO", "Sessão não autorizada. Rode o script de login.")
                raise SessionPasswordNeededError(
                    "Sessão não autorizada. Autentique o arquivo de sessão.")

            self.log_update(
                "Conexão",
                f"Sessão iniciada como: {(await self.client.get_me()).username}")
            
            # 2. Resolução do Peer (Identificar o canal)
            entity = await self.client.get_entity(self.channel_id)
            self.log_update("DEBUG", f"Peer Resolvido. ID: {entity.id}")
            
            # 3. Pré-cálculo do total de arquivos
            all_files = []
            for root, _, files in os.walk(directory):
                all_files.extend([os.path.join(root, f) for f in files])
                
            self.total_files = len(all_files)
            self.log_update(
                "DEBUG", 
                f"Total de arquivos encontrados para envio: {self.total_files}")
            
            if self.total_files == 0:
                self.log_update(
                    "AVISO", "A pasta está vazia. Processo finalizado.")
                return

            # Configura a barra de progresso para o modo determinado
            self.after(0, self.progress_bar.config, {'mode': 'determinate', 
                                                     'maximum': 100})
            
            # 4. Percorre e envia
            for file_path in all_files:
                
                try:
                    # Tenta enviar o documento com o callback de progresso
                    await self.client.send_file(
                        entity, 
                        file=file_path, 
                        progress_callback=self.send_file_callback # Adiciona o callback
                    )
                    
                    # 5. Exclui o arquivo
                    os.remove(file_path)
                    status = "Enviado e excluído com sucesso."
                    self.files_sent += 1
                    
                    # Atualiza progresso GERAL após a conclusão do arquivo
                    self.after(0, self.progress_bar.config, 
                               {'value': (self.files_sent / self.total_files) * 100})
                    
                except RPCError as e:
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
            self.after(0, lambda: messagebox.showerror(
                "Erro de Autenticação", 
                f"Autenticação de 2FA necessária! {e}"))
        except (PeerIdInvalidError, ChannelPrivateError) as e:
            self.after(0, lambda: messagebox.showerror(
                "Erro de ID/Permissão", 
                f"Falha ao encontrar o canal {self.channel_id}. {e}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Erro Inesperado Crítico", 
                f"Ocorreu um erro crítico: {type(e).__name__} - {e}"))
            
        finally:
            await self.client.disconnect()
            self.after(0, self._reset_gui)
            
    def _reset_gui(self):
        """Restaura o estado inicial da GUI para permitir um novo envio."""
        self.progress_bar.stop()
        
        # Restaura o botão e o estado
        self.send_button.config(
            state="normal", text="▶ INICIAR ENVIO E EXCLUSÃO")
        
        # Adiciona a mensagem final e zera o label
        self._append_to_log("\n--- APLICAÇÃO PRONTA PARA NOVO ENVIO ---")
        self.progress_label.config(
            text=
            f"Status: Concluído ({self.files_sent}"
            f"enviados de {self.total_files})")
        
        # Força o Tkinter a redesenhar
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