import customtkinter as ctk
import pandas as pd
from pyzabbix import ZabbixAPI
from weasyprint import HTML, CSS
from datetime import datetime, timedelta
import threading
from tkinter import filedialog, messagebox

def fetch_zabbix_data(server, user, password, group_name, days):
    zapi = ZabbixAPI(server)
    zapi.session.verify = False
    zapi.login(user, password)

    time_till = datetime.now()
    time_from = time_till - timedelta(days=days)
    time_from_unix = int(time_from.timestamp())
    time_till_unix = int(time_till.timestamp())
    total_seconds_in_period = days * 24 * 3600

    host_group = zapi.hostgroup.get(filter={'name': [group_name]})
    if not host_group:
        raise ValueError(f"Grupo de hosts '{group_name}' não encontrado.")
    
    hosts = zapi.host.get(
        output=['hostid', 'name'],
        groupids=[host_group[0]['groupid']],
        selectInterfaces=['ip']
    )

    report_data = []
    for host in hosts:
        ping_items = zapi.item.get(
            output=['itemid'], hostids=[host['hostid']], filter={'key_': 'icmpping'}
        )
        if not ping_items:
            continue

        trends = zapi.trend.get(
            output=['value_min'], itemids=[ping_items[0]['itemid']],
            time_from=time_from_unix, time_till=time_till_unix
        )
        
        downtime_hours = sum(1 for trend in trends if int(trend['value_min']) == 0)
        total_downtime_seconds = downtime_hours * 3600
        availability = 100 * (1 - (total_downtime_seconds / total_seconds_in_period))
        
        report_data.append({
            'host': host['name'],
            'ip': host['interfaces'][0]['ip'] if host['interfaces'] else 'N/A',
            'availability': f"{availability:.3f}%",
            'total_downtime': format_downtime(total_downtime_seconds),
            'period_days': days
        })
    
    zapi.user.logout()
    return pd.DataFrame(report_data)

def create_pdf_report(df, output_filename):
    df.fillna('N/A', inplace=True)
    period = df['period_days'].iloc[0] if not df.empty else 'N/A'
    
    html_content = f"""
    <html><head><meta charset="UTF-8"><title>Relatório</title></head><body>
    <header><h1>Relatório de Disponibilidade de Ativos</h1>
    <p class="subtitle">Período Analisado: Últimos {period} dias</p>
    <p class="generation-date">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p></header>
    <table><thead><tr><th>Host</th><th>Endereço IP</th><th>Disponibilidade</th><th>Downtime Total</th></tr></thead><tbody>
    """
    for _, row in df.iterrows():
        style = get_availability_style(row['availability'])
        html_content += f"<tr><td>{row['host']}</td><td>{row['ip']}</td><td {style}>{row['availability']}</td><td>{row['total_downtime']}</td></tr>"
    
    html_content += "</tbody></table><footer><p>Relatório gerado automaticamente.</p></footer></body></html>"
    
    css_style = CSS(string="""
        @page { size: A4; margin: 2cm; @bottom-center { content: "Página " counter(page) " de " counter(pages); font-size: 10pt; color: #888; } }
        body { font-family: 'Helvetica', 'Arial', sans-serif; color: #333; font-size: 10pt; }
        header { text-align: center; border-bottom: 2px solid #0056b3; margin-bottom: 20px; padding-bottom: 10px; }
        h1 { color: #0056b3; margin: 0; }
        .subtitle, .generation-date { color: #555; margin: 2px 0; font-size: 10pt; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        thead tr { background-color: #0056b3; color: white; }
        tbody tr:nth-child(even) { background-color: #f2f2f2; }
        td { text-align: center; }
        td:first-child { text-align: left; width: 50%; }
        footer { text-align: center; margin-top: 30px; font-size: 9pt; color: #888; }
    """)
    
    HTML(string=html_content).write_pdf(output_filename, stylesheets=[css_style])

def format_downtime(seconds):
    if seconds == 0: return "N/A"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    parts = []
    if days > 0: parts.append(f"{int(days)}d")
    if hours > 0: parts.append(f"{int(hours)}h")
    if minutes > 0: parts.append(f"{int(minutes)}m")
    return " ".join(parts) if parts else "< 1m"

def get_availability_style(availability_str):
    try:
        value = float(str(availability_str).strip().replace('%', ''))
        if value < 98.0: return 'style="background-color: #FFCDD2; color: #C62828;"'
        elif value < 99.9: return 'style="background-color: #FFF9C4; color: #F9A825;"'
        else: return 'style="background-color: #C8E6C9; color: #2E7D32;"'
    except (ValueError, TypeError): return ''

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gerador de Relatórios Zabbix")
        self.geometry("500x550")
        
        #Tema - pode ser alterado para "Dark", "Light" ou "System"
        ctk.set_appearance_mode("System")
        
        self.grid_columnconfigure(1, weight=1)

        self.zabbix_server_label = ctk.CTkLabel(self, text="Servidor Zabbix URL:")
        self.zabbix_server_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        self.zabbix_server_entry = ctk.CTkEntry(self, placeholder_text="https://zabbix.seu-dominio.com")
        self.zabbix_server_entry.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="ew")

        self.zabbix_user_label = ctk.CTkLabel(self, text="Usuário API:")
        self.zabbix_user_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.zabbix_user_entry = ctk.CTkEntry(self)
        self.zabbix_user_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        self.zabbix_password_label = ctk.CTkLabel(self, text="Senha API:")
        self.zabbix_password_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.zabbix_password_entry = ctk.CTkEntry(self, show="*")
        self.zabbix_password_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        self.group_name_label = ctk.CTkLabel(self, text="Nome do Grupo de Hosts:")
        self.group_name_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.group_name_entry = ctk.CTkEntry(self)
        self.group_name_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        self.period_days_label = ctk.CTkLabel(self, text="Período (dias):")
        self.period_days_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.period_days_entry = ctk.CTkEntry(self)
        self.period_days_entry.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        self.period_days_entry.insert(0, "30") # Valor padrão

        self.generate_button = ctk.CTkButton(self, text="Gerar Relatório PDF", command=self.start_report_generation)
        self.generate_button.grid(row=5, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.log_textbox = ctk.CTkTextbox(self, state="disabled", height=150)
        self.log_textbox.grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

    def log_message(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")
        
    def start_report_generation(self):
        self.generate_button.configure(state="disabled", text="Gerando...")
        self.log_message("Iniciando geração do relatório...")
        
        thread = threading.Thread(target=self.run_report_task)
        thread.start()

    def run_report_task(self):
        """Tarefa que roda em segundo plano."""
        try:
            server = self.zabbix_server_entry.get()
            user = self.zabbix_user_entry.get()
            password = self.zabbix_password_entry.get()
            group = self.group_name_entry.get()
            days = int(self.period_days_entry.get())

            if not all([server, user, password, group, days]):
                raise ValueError("Todos os campos são obrigatórios.")

            # 1. Buscar dados do Zabbix
            self.log_message(f"Conectando ao Zabbix e buscando dados do grupo '{group}'...")
            df = fetch_zabbix_data(server, user, password, group, days)
            self.log_message(f"Dados de {len(df)} hosts encontrados.")

            if df.empty:
                raise ValueError("Nenhum dado encontrado para os critérios informados.")

            # 2. Pedir ao usuário onde salvar o PDF
            output_filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Salvar Relatório Como..."
            )
            if not output_filename:
                self.log_message("Geração cancelada pelo usuário.")
                self.generate_button.configure(state="normal", text="Gerar Relatório PDF")
                return

            # 3. Criar o PDF
            self.log_message(f"Criando o arquivo PDF em '{output_filename}'...")
            create_pdf_report(df, output_filename)
            self.log_message("Relatório PDF gerado com sucesso!")
            messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{output_filename}")

        except Exception as e:
            self.log_message(f"ERRO: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")
        finally:
            self.generate_button.configure(state="normal", text="Gerar Relatório PDF")


if __name__ == "__main__":
    app = App()
    app.mainloop()