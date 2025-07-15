import os
import subprocess
import json


class GitController:
    """
    Sistema completo para controle de versões com Git e autenticação SSH via GitHub.
    Gera chave SSH, verifica ambiente, salva diretório selecionado e executa comandos Git com segurança.
    """

    CONFIG_PATH = "config.json"

    def __init__(self):
        """
        Inicializa o sistema, carregando o último caminho do projeto (se salvo).
        """
        self.projeto_path = None
        self.carregar_config()
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

    def carregar_config(self):
        """Carrega diretório salvo anteriormente em config.json"""
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, 'r') as f:
                    dados = json.load(f)
                    if os.path.isdir(dados.get("projeto_path", "")):
                        self.projeto_path = dados["projeto_path"]
                        print(f"📂 Diretório restaurado: {self.projeto_path}")
            except Exception as e:
                print("⚠️ Falha ao carregar configuração:", e)

    def salvar_config(self):
        """Salva diretório atual em config.json"""
        try:
            with open(self.CONFIG_PATH, 'w') as f:
                json.dump({"projeto_path": self.projeto_path}, f)
        except Exception as e:
            print("⚠️ Erro ao salvar configuração:", e)

    def executar_comando(self, comando):
        """Executa um comando Git no terminal dentro do diretório selecionado."""
        if not self.projeto_path:
            print("⚠️ Selecione o diretório do projeto primeiro (opção 0).")
            return
        try:
            resultado = subprocess.run(
                comando, capture_output=True, text=True, check=True, cwd=self.projeto_path
            )
            print(resultado.stdout)
        except subprocess.CalledProcessError as e:
            print("❌ Erro ao executar comando:")
            print(e.stderr)

    def verificar_git_repo(self):
        """Verifica se o diretório é um repositório Git válido."""
        return os.path.isdir(os.path.join(self.projeto_path, ".git"))

    def selecionar_diretorio(self):
        """Permite ao usuário selecionar o diretório local do projeto Git."""
        path = input("📁 Caminho do projeto (ex: C:/meu_projeto): ").strip()
        if os.path.isdir(path) and os.path.isdir(os.path.join(path, ".git")):
            self.projeto_path = path
            self.salvar_config()
            print(f"✅ Diretório definido: {self.projeto_path}")
        else:
            print("❌ Caminho inválido ou não é um repositório Git.")

    def detectar_mudancas(self):
        """Exibe as mudanças não versionadas no repositório."""
        self.executar_comando(["git", "status"])

    def commit_push(self):
        """Adiciona, comita e envia alterações para o repositório remoto."""
        msg = input("📝 Mensagem do commit: ").strip()
        self.executar_comando(["git", "add", "."])
        self.executar_comando(["git", "commit", "-m", msg])
        self.verificar_url_ssh()
        self.executar_comando(["git", "push"])

    def git_pull(self):
        """Atualiza o repositório local com as mudanças remotas."""
        self.verificar_url_ssh()
        self.executar_comando(["git", "pull"])

    def criar_tag(self):
        """Cria e envia uma nova tag de versão para o GitHub."""
        tag = input("🏷 Nome da nova versão (ex: v1.0.0): ").strip()
        self.executar_comando(["git", "tag", tag])
        self.executar_comando(["git", "push", "origin", tag])

    def status(self):
        """Exibe o status atual do repositório."""
        self.executar_comando(["git", "status"])

    def configurar_ssh(self):
        """
        Gera nova chave SSH se necessário e instrui o usuário a cadastrar no GitHub.
        Também atualiza a URL remota do projeto para usar o protocolo SSH.
        """
        ssh_path = os.path.expanduser("~/.ssh/id_ed25519")
        pub_key_path = ssh_path + ".pub"

        if not os.path.exists(ssh_path):
            print("🔐 Gerando nova chave SSH...")
            email = input("Digite seu e-mail GitHub: ").strip()
            subprocess.run(["ssh-keygen", "-t", "ed25519", "-C", email, "-f", ssh_path, "-N", ""])
            print("✅ Chave SSH gerada.")
        else:
            print("🔐 Chave SSH já existe.")

        with open(pub_key_path, 'r') as pub_file:
            chave = pub_file.read()

        print("\n📎 Copie e cole esta chave pública no seu GitHub:")
        print(chave)
        print("Acesse: https://github.com/settings/keys\n")
        input("Pressione ENTER após adicionar a chave...")

        if self.projeto_path:
            repo_ssh = input("🔗 Cole aqui a URL SSH do repositório (ex: git@github.com:user/repo.git): ")
            self.executar_comando(["git", "remote", "set-url", "origin", repo_ssh])
            print("✅ Repositório configurado para SSH.")
        else:
            print("⚠️ Selecione o diretório primeiro.")

    def verificar_url_ssh(self):
        """Garante que o repositório esteja configurado com SSH."""
        try:
            resultado = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True, text=True, check=True,
                cwd=self.projeto_path
            )
            if "https://" in resultado.stdout:
                print("⚠️ Seu repositório está configurado com HTTPS.")
                print("🔁 Recomenda-se trocar para SSH com a opção 7 (Configurar SSH).")
        except Exception as e:
            print("Erro ao verificar URL remota:", e)

    def sair(self):
        """Encerra o programa."""
        print("👋 Saindo...")
        exit()

    def mostrar_menu(self):
        """Exibe o menu principal e trata as seleções."""
        while True:
            print("\n===== GIT CONTROLLER (COMPLETO) =====")
            print("0 - Selecionar diretório do projeto")
            print("1 - Detectar mudanças")
            print("2 - Commit e Push")
            print("3 - Pull (atualizar local)")
            print("4 - Criar nova tag de versão")
            print("5 - Ver status")
            print("6 - Sair")
            print("7 - Configurar autenticação SSH")
            print("======================================")
            escolha = input("Escolha uma opção: ").strip()

            acao = self.menu_opcoes.get(escolha)
            if acao:
                acao()
            else:
                print("❌ Opção inválida!")


if __name__ == "__main__":
    app = GitController()
    app.mostrar_menu()
