import subprocess
import sys

# 1. Bibliotecas que seu código realmente usa
bibliotecas_usadas = ["flask", "numpy", "pandas"]

# 2. Mapeamento de imports para nomes reais dos pacotes no pip (se necessário)
# Exemplo: se usasse "import sklearn", mapearia {"sklearn": "scikit-learn"}
mapeamento = {}
pacotes_necessarios = {mapeamento.get(b, b) for b in bibliotecas_usadas}

# 3. Ler o requirements.txt atual
try:
    with open("requirements.txt", "r") as f:
        linhas = f.readlines()
except FileNotFoundError:
    print("Erro: Arquivo requirements.txt não encontrado.")
    sys.exit(1)

# 4. Identificar o que deve ser deletado
pacotes_para_deletar = []
for linha in linhas:
    linha = linha.strip()
    if not linha or "==" not in linha:
        continue
    
    nome_pacote = linha.split("==")[0].strip()
    
    # Se o pacote (em minúsculo) não estiver na lista de necessários, deleta
    if nome_pacote.lower() not in pacotes_necessarios:
        pacotes_para_deletar.append(nome_pacote)

# 5. Executar a desinstalação automática
if pacotes_para_deletar:
    print(f"Os seguintes pacotes serão removidos: {pacotes_para_deletar}\n")
    
    # Executa o pip uninstall passando a lista de pacotes
    # O argumento '-y' confirma a exclusão automaticamente sem pedir confirmação
    comando = [sys.executable, "-m", "pip", "uninstall", "-y"] + pacotes_para_deletar
    subprocess.run(comando)
    
    print("\nLimpeza concluída com sucesso!")
else:
    print("Nenhum pacote desnecessário encontrado para deletar.")