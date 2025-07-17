import os
import subprocess
import json


class GitConfig:
    """
    Responsável por carregar e salvar configurações do caminho do projeto
    em um arquivo JSON.
    """
    CONFIG_PATH = "config.json"

    @staticmethod
    def carregar():
        """Carrega o caminho do projeto salvo em config.json."""
        if os.path.exists(GitConfig.CONFIG_PATH):
            try:
                with open(GitConfig.CONFIG_PATH, 'r') as f:
                    dados = json.load(f)
                    if os.path.isdir(dados.get("projeto_path", "")):
                        return dados["projeto_path"]
            except Exception as e:
                print("⚠️ Falha ao carregar configuração:", e)
        return None

    @staticmethod
    def salvar(path):
        """Salva o caminho do projeto atual em config.json."""
        try:
            with open(GitConfig.CONFIG_PATH, 'w') as f:
                json.dump({"projeto_path": path}, f)
        except Exception as e:
            print("⚠️ Erro ao salvar configuração:", e)


class GitSSH:
    """
    Responsável pela geração de chaves SSH e exibição da chave pública
    para autenticação com o GitHub.
    """
    @staticmethod
    def gerar_chave(email):
        """
        Gera uma nova chave SSH do tipo ed25519, se não existir.
        Retorna o caminho da chave pública gerada.
        """
        ssh_path = os.path.expanduser("~/.ssh/id_ed25519")
        if not os.path.exists(ssh_path):
            subprocess.run(["ssh-keygen", "-t", "ed25519", "-C", email, "-f", ssh_path, "-N", ""])
            print("✅ Chave SSH gerada.")
        else:
            print("🔐 Chave SSH já existe.")
        return ssh_path + ".pub"

    @staticmethod
    def exibir_chave(pub_key_path):
        """Exibe a chave pública gerada e orienta o usuário a adicioná-la no GitHub."""
        with open(pub_key_path, 'r') as pub_file:
            chave = pub_file.read()
        print("\n📎 Copie e cole esta chave pública no seu GitHub:")
        print(chave)
        print("Acesse: https://github.com/settings/keys\n")
        input("Pressione ENTER após adicionar a chave...")


class GitController:
    """
    Controlador principal do sistema. Gerencia a interação com o usuário,
    execução de comandos Git e operações de configuração e autenticação.
    """
    def __init__(self):
        """Inicializa o controlador e carrega as configurações salvas."""
        self.projeto_path = GitConfig.carregar()
        if self.projeto_path:
            print(f"📂 Diretório restaurado: {self.projeto_path}")
        self.menu_opcoes = {
            "0": self.selecionar_diretorio,
            "1": self.detectar_mudancas,
            "2": self.commit_push,
            "3": self.git_pull,
            "4": self.criar_tag,
            "5": self.status,
            "6": self.sair,
            "7": self.configurar_ssh
        }

    def executar_comando(self, comando):
        """Executa um comando no terminal dentro do diretório selecionado."""
        if not self.projeto_path:
            print("⚠️ Selecione o diretório do projeto primeiro (opção 0).")
            return
        try:
            resultado = subprocess.run(comando, capture_output=True, text=True, check=True, cwd=self.projeto_path)
            print(resultado.stdout)
        except subprocess.CalledProcessError as e:
            print("❌ Erro ao executar comando:")
            print(e.stderr)

    def selecionar_diretorio(self):
        """Permite selecionar o diretório do projeto Git local."""
        path = input("📁 Caminho do projeto (ex: C:/meu_projeto): ").strip()
        if os.path.isdir(path) and os.path.isdir(os.path.join(path, ".git")):
            self.projeto_path = path
            GitConfig.salvar(path)
            print(f"✅ Diretório definido: {self.projeto_path}")
        else:
            print("❌ Caminho inválido ou não é um repositório Git.")

    def detectar_mudancas(self):
        """Mostra alterações não commitadas no projeto."""
        self.executar_comando(["git", "status"])

    def commit_push(self):
        """
        Adiciona arquivos, realiza commit com mensagem e envia alterações
        para o repositório remoto.
        """
        msg = input("📝 Mensagem do commit: ").strip()
        self.executar_comando(["git", "add", "."])
        self.executar_comando(["git", "commit", "-m", msg])
        self.verificar_url_ssh()
        self.executar_comando(["git", "push"])

    def git_pull(self):
        """Atualiza o projeto local com alterações do repositório remoto."""
        self.verificar_url_ssh()
        self.executar_comando(["git", "pull"])

    def criar_tag(self):
        """Cria e envia uma nova tag de versão para o repositório remoto."""
        tag = input("🏷 Nome da nova versão (ex: v1.0.0): ").strip()
        self.executar_comando(["git", "tag", tag])
        self.executar_comando(["git", "push", "origin", tag])

    def status(self):
        """Exibe o status atual do repositório Git."""
        self.executar_comando(["git", "status"])

    def configurar_ssh(self):
        """
        Cria uma nova chave SSH (caso não exista), orienta o usuário a
        cadastrá-la no GitHub e define a URL remota do repositório.
        """
        email = input("Digite seu e-mail GitHub: ").strip()
        pub_key_path = GitSSH.gerar_chave(email)
        GitSSH.exibir_chave(pub_key_path)

        if self.projeto_path:
            repo_ssh = input("🔗 Cole aqui a URL SSH do repositório (ex: git@github.com:user/repo.git): ")
            self.executar_comando(["git", "remote", "set-url", "origin", repo_ssh])
            print("✅ Repositório configurado para SSH.")
        else:
            print("⚠️ Selecione o diretório primeiro.")

    def verificar_url_ssh(self):
        """Verifica se o repositório está usando SSH em vez de HTTPS."""
        try:
            resultado = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True, check=True, cwd=self.projeto_path)
            if "https://" in resultado.stdout:
                print("⚠️ Seu repositório está configurado com HTTPS.")
                print("🔁 Recomenda-se trocar para SSH com a opção 7 (Configurar SSH).")
        except Exception as e:
            print("Erro ao verificar URL remota:", e)

    def sair(self):
        """Encerra a execução do programa."""
        print("👋 Saindo...")
        exit()

    def mostrar_menu(self):
        """Exibe o menu principal e aguarda ações do usuário."""
        while True:
            print("\n===== GIT CONTROLLER (POO) =====")
            print("0 - Selecionar diretório do projeto")
            print("1 - Detectar mudanças")
            print("2 - Commit e Push")
            print("3 - Pull (atualizar local)")
            print("4 - Criar nova tag de versão")
            print("5 - Ver status")
            print("6 - Sair")
            print("7 - Configurar autenticação SSH")
            print("==================================")
            escolha = input("Escolha uma opção: ").strip()
            acao = self.menu_opcoes.get(escolha)
            if acao:
                acao()
            else:
                print("❌ Opção inválida!")


if __name__ == "__main__":
    GitController().mostrar_menu()
