from paramiko import SSHClient,AutoAddPolicy
from socket import create_connection
from pandas import DataFrame,ExcelWriter
from openpyxl import utils
from tqdm import tqdm
from os import system

system('color a')
loja = input(str('Deseja verificar as maquinas de qual loja ?\n'))
system('cls')
print(f'Realizado Scan na rede da loja {loja}, o processo vai levar alguns minutos\n')


def get_system_info(ip_address, username, password):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(ip_address, username=username, password=password)

    # Executa comandos no dispositivo remoto para obter o tamanho total do disco rígido
    stdin, stdout, stderr = ssh.exec_command("df -h / | awk '{print $2}' | tail -n 1")
    disk_size = stdout.read().decode("utf-8").strip()
    # Executa comandos no dispositivo remoto para obter informações do processador
    stdin, stdout, stderr = ssh.exec_command("cat /proc/cpuinfo | grep 'model name'")
    cpu_info = stdout.read().decode("utf-8").strip()
    # Executa comandos no dispositivo remoto para obter a quantidade de memória total
    stdin, stdout, stderr = ssh.exec_command("cat /proc/meminfo | grep 'MemTotal' | awk '{print $2}'")
    mem_total = stdout.read().decode("utf-8").strip()
    # Obtém informações da versão do sistema operacional
    stdin, stdout, stderr = ssh.exec_command("cat /etc/os-release | grep 'PRETTY_NAME' | awk -F '\"' '{print $2}'")
    os_version = stdout.read().decode("utf-8").strip()
    # Obtém o hostname da máquina
    stdin, stdout, stderr = ssh.exec_command("hostname")
    hostname = stdout.read().decode("utf-8").strip()

    ssh.close()

    return ip_address,hostname,os_version, disk_size, mem_total, cpu_info


ip_range = []
for i in range(1,255):
    ip_range.append(f"192.168.{loja}." + str(i))
username = ""
password = ""

# Cria uma lista vazia para armazenar os resultados
results = []

# Itera sobre os endereços de IP
for ip_address in tqdm(ip_range):
    try:
        sock = create_connection((ip_address, 22), timeout=5)
        sock.close()
        results.append(get_system_info(ip_address, username, password))
    except:
        pass

# Cria um dataframe a partir da lista de resultados
df = DataFrame(results, columns=["IP Address","Hostname","OS", "Total Disk Size", "Total Memory", "CPU Information"])

# Cria uma instância do arquivo excel
writer = ExcelWriter(f"Maquinas_Linux_Loja{loja}.xlsx", engine='openpyxl')

# Escreve os dados no arquivo excel
df.to_excel(writer, index=False)

# Ajusta o tamanho das colunas de acordo com o texto mais longo contido na coluna
worksheet = writer.sheets['Sheet1']
for i, col in enumerate(df.columns):
    column_len = df[col].astype(str).str.len().max()
    column_len = max(column_len, len(col)) + 2
    worksheet.column_dimensions[utils.get_column_letter(i+1)].width = column_len

# Salva o arquivo excel
writer.book.save(f"Maquinas_Linux_Loja{loja}.xlsx")
