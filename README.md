# Hardening Suite

Automação de hardening para Linux (Ubuntu/Debian), com foco em SSH, firewall, fail2ban, sistema e auditoria.

## Requisitos

* Linux (Ubuntu/Debian)
* Python 3.10+
* Privilégios elevados (`sudo`)
* Rede para `apt`, quando aplicável

## Instalação

```bash
cd hardening-suite
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Alternativa sem instalação em modo editável:

```bash
pip install typer rich pydantic
```

## Execução

```bash
sudo .venv/bin/python harden.py <comando>
```

### Verificação de distribuição

Comandos de hardening (`harden-ssh`, `harden-network`, etc.) **só rodam** se `ID` em `/etc/os-release` for `ubuntu` ou `debian`. O comando `scan` não bloqueia.

Para forçar em outra distro (não recomendado):

```bash
sudo .venv/bin/python harden.py --skip-distro-check harden-system
```

### Opções úteis

| Contexto | Opção | Efeito |
|----------|--------|--------|
| Rede | `--limit-ssh` | `ufw limit` nas portas TCP do SSH |
| Rede | `--ensure-ipv6` / `--no-ensure-ipv6` | Ajusta `IPV6=yes` ou `no` em `/etc/default/ufw` antes das regras |
| SSH | `--public-key-file PATH` | Lê a chave pública do arquivo (não interativo) |
| SSH | `--ensure-ssh` | Instala `openssh-server` (apt) e tenta iniciar o serviço se não estiver pronto (WSL/labs) |

Exemplos:

```bash
sudo .venv/bin/python harden.py harden-network --limit-ssh
sudo .venv/bin/python harden.py harden-network --no-ensure-ipv6
sudo .venv/bin/python harden.py harden-ssh --public-key-file /root/my_key.pub
sudo .venv/bin/python harden.py harden-ssh --ensure-ssh
```

### Códigos de saída (CLI)

| Código | Significado |
|--------|-------------|
| 0 | Sucesso |
| 1 | Falha geral / comando |
| 2 | Validação |
| 3 | Rollback / operação revertida |
| 4 | Backup / restauração |
| 5 | Distribuição não suportada |

## Comandos

* `scan` — informações do sistema
* `harden-ssh` — chave pública, `sshd_config` (só seção **global**, antes do primeiro `Match`), teste e rollback
* `harden-network` — UFW (portas do `sshd_config`, IPv4/IPv6 conforme UFW) + fail2ban (`port` alinhado ao SSH)
* `harden-system` — atualizações e ferramentas básicas
* `harden-advanced` — serviços, modprobe, permissões, sudo via `sudoers.d` + `visudo`
* `harden-audit` — auditd, rkhunter, AIDE

Ordem sugerida: `harden-ssh` → `harden-network` → `harden-system` → `harden-advanced` → `harden-audit`.

## Testes

```bash
pip install -e .
python -m unittest discover -s tests -p "test_*.py" -v
```

Inclui validação de chaves SSH, parser global do `sshd`, fail2ban, modprobe, `run_guarded` (códigos de saída), smoke do Typer e, em **Linux**, um smoke de integração leve (`tests/integration/`, leitura de `/etc/os-release`, `get_os_info`, `uname`).

### CI (GitHub Actions)

O workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) corre em **ubuntu-latest** com Python 3.10, 3.11 e 3.12, instala o projeto com `pip install -e .` e executa o mesmo `unittest discover`. Assim a suíte corre **num SO Linux real** no push/PR (ramos `main` ou `master`).

### Aviso explícito — cobertura e confiança

> **Cobertura de testes** — não substitui pentest nem auditoria em produção. O CI executa testes automatizados em Linux, mas **não** são testes de integração ponta-a-ponta contra um servidor onde a ferramenta já tenha aplicado hardening com root (sem `sshd`/UFW/sudo alterados pela suite no pipeline).
>
> **“Seguro para usar” depende do uso** — em VM/snapshot, homologação e Ubuntu/Debian com backup e consola, é **razoavelmente confiável** para um projeto deste tipo. Em **produção crítica** sem janela de manutenção e sem plano B, **nunca** é “garantido”.

Detalhe adicional:

* Mesmo com CI em Linux, os testes continuam a ser sobretudo **unitários e smoke**; **processo** (staging, backups, consola, reversão) continua necessário para confiança operacional.
* Integração pesada (ex.: VM descartável que executa `harden-*` de ponta a ponta) pode ser acrescentada à parte, se a sua organização exigir esse nível.

## Uso recomendado (além do aviso acima)

* Preferir **VM com snapshot**, **homologação** e só depois produção.
* Garantir **backup**, **acesso à consola** (ou IPMI / cloud) e **janela de manutenção** quando aplicável.
* **Produção crítica:** não tratar o resultado como garantido; validar sempre num ambiente parecido antes.

## Limitações conhecidas

* `Include` em `sshd_config` não é expandido: portas e edição global não “enxergam” ficheiros incluídos.
* Derivados (ex.: Linux Mint) com `ID` diferente de `ubuntu`/`debian` precisam de `--skip-distro-check` ou extensão da lista em `app/core/constants.py`.
* WSL pode limitar serviços e firewall.

## Estrutura

```
app/
├── cli/            CLI e tratamento de erros
├── core/
├── collectors/
├── policies/
├── remediators/
├── utils/
├── validators/
tests/              Testes unittest
state/backups/      Backups gerados em execução
```
