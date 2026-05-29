import subprocess
from pathlib import Path

# Obtém o caminho do diretório onde este script atual está salvo
diretorio_atual = Path(__file__).parent

# Aponta para o arquivo app.py dentro da pasta app
caminho_app = diretorio_atual / "app" / "app.py"

print(f"Executando: {caminho_app}")

# Executa o script
resultado = subprocess.run(["python", str(caminho_app)])

# Verifica se o script rodou com sucesso
if resultado.returncode == 0:
    print("Script executado com sucesso!")
else:
    print(f"O script falhou com o código de retorno: {resultado.returncode}")