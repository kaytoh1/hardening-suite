HEAD
# hardening-suite
Segurança linux
# Hardening Suite

## Descrição

Hardening Suite é uma ferramenta de automação para hardening de sistemas Linux (Ubuntu/Debian), projetada para aplicar boas práticas de segurança de forma segura, modular e automatizada.

A ferramenta executa configurações críticas de segurança incluindo SSH, firewall, proteção contra brute force, hardening do sistema, auditoria e verificação de integridade.

O foco do projeto é evitar erros comuns de configuração, reduzir superfície de ataque e garantir que o acesso remoto não seja perdido durante o processo.

---

## Objetivo

Automatizar o hardening de um sistema Linux com:

* Execução segura
* Validação antes de aplicar mudanças
* Proteção contra lockout de SSH
* Estrutura modular e extensível

---

## Requisitos

* Linux (Ubuntu/Debian recomendado)
* Python 3.10 ou superior
* Acesso root (sudo)
* Conexão com internet

---

## Instalação

### 1. Clonar ou acessar o projeto

```bash
cd /mnt/c/Users/kaytoh/Desktop/hardening/hardening-suite
```

### 2. Criar ambiente virtual

```bash
python3 -m venv .venv
```

### 3. Ativar ambiente virtual

```bash
source .venv/bin/activate
```

### 4. Instalar dependências

```bash
pip install typer rich pydantic
```

---

## Estrutura do Projeto

```
app/
├── cli/            Interface de linha de comando
├── core/           Constantes, modelos e exceções
├── collectors/     Coleta de informações do sistema
├── policies/       Regras de segurança
├── remediators/    Execução das ações de hardening
├── utils/          Funções auxiliares

state/
├── backups/        Backups automáticos
├── reports/        Relatórios (futuro)
├── runs/           Histórico de execução
```

---

## Como Executar

Todos os comandos devem ser executados com privilégios elevados.

### Executar comando geral

```bash
sudo .venv/bin/python harden.py <comando>
```

---

## Comandos Disponíveis

### 1. Hardening de SSH

```bash
sudo .venv/bin/python harden.py harden-ssh
```

O que faz:

* Configura autenticação por chave SSH
* Desativa login por senha
* Desativa login root
* Ajusta permissões de `.ssh`
* Valida configuração antes de aplicar
* Reinicia SSH com verificação de acesso

---

### 2. Hardening de rede

```bash
sudo .venv/bin/python harden.py harden-network
```

O que faz:

* Instala e configura UFW
* Bloqueia conexões de entrada por padrão
* Libera acesso SSH
* Instala e configura Fail2ban

---

### 3. Hardening de sistema

```bash
sudo .venv/bin/python harden.py harden-system
```

O que faz:

* Atualiza pacotes do sistema
* Ativa atualizações automáticas
* Instala ferramentas de segurança
* Remove dependências desnecessárias

---

### 4. Hardening avançado

```bash
sudo .venv/bin/python harden.py harden-advanced
```

O que faz:

* Desativa serviços inseguros
* Bloqueia módulos perigosos do kernel
* Corrige permissões críticas
* Ativa logging de sudo

---

### 5. Auditoria e integridade

```bash
sudo .venv/bin/python harden.py harden-audit
```

O que faz:

* Instala e ativa auditd
* Instala e executa rkhunter
* Instala AIDE
* Inicializa base de integridade (com fallback seguro)

---

## Ordem Recomendada de Execução

Para evitar problemas:

1. harden-ssh
2. harden-network
3. harden-system
4. harden-advanced
5. harden-audit

---

## Como o Sistema Funciona

Fluxo de execução:

1. CLI recebe comando
2. Módulo correspondente é chamado
3. Sistema executa comandos Linux via subprocess
4. Configurações são aplicadas
5. Validação é feita (quando necessário)
6. Backups são gerados automaticamente

---

## Segurança

A ferramenta implementa:

* Proteção contra perda de acesso SSH
* Firewall com política restritiva
* Bloqueio de brute force
* Atualizações automáticas
* Hardening de permissões
* Auditoria de sistema
* Detecção de rootkits
* Verificação de integridade de arquivos

---

## Observações Importantes

* O projeto é otimizado para Ubuntu/Debian
* Algumas ferramentas podem demorar (ex: AIDE)
* WSL pode apresentar limitações
* Sempre valide acesso SSH antes de aplicar mudanças

---

## Tratamento de Erros

* Timeout controlado para comandos longos
* Erros não críticos não interrompem execução
* Validação antes de aplicar mudanças críticas
* Execução resiliente para ambiente real

---

## Limitações Atuais

* Suporte limitado a outras distribuições
* Não possui execução remota (multi-host)
* Não possui interface gráfica
* Não possui sistema de rollback completo

---

## Possíveis Evoluções

* Execução em múltiplos servidores
* Suporte multi-distro
* Interface web
* Relatórios de segurança
* Perfis de hardening

---

## Conclusão

Hardening Suite automatiza tarefas críticas de segurança em Linux, reduzindo erros humanos e aplicando boas práticas de forma estruturada.

O projeto demonstra conceitos de:

* automação de infraestrutura
* segurança de sistemas
* organização modular
* execução segura de comando


0da48f5 (Projeto Hardening)
