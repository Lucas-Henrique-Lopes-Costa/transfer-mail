#!/usr/bin/env python3
"""
Script de Transferência de Emails usando imapsync
Transfere emails entre contas com logs detalhados do processo
"""

import json
import subprocess
import logging
import sys
from datetime import datetime
from pathlib import Path

# Configuração de logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Nome do arquivo de log com timestamp
log_filename = LOG_DIR / f"transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configurar logging para arquivo e console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def get_imap_server_from_email(email):
    """Tenta detectar o servidor IMAP baseado no domínio do email"""
    domain = email.split("@")[-1].lower()

    # Servidores IMAP comuns
    common_servers = {
        "gmail.com": "imap.gmail.com",
        "outlook.com": "outlook.office365.com",
        "hotmail.com": "outlook.office365.com",
        "live.com": "outlook.office365.com",
        "yahoo.com": "imap.mail.yahoo.com",
        "icloud.com": "imap.mail.me.com",
        "me.com": "imap.mail.me.com",
    }

    if domain in common_servers:
        return common_servers[domain]

    # Para domínios personalizados, tenta mail.dominio ou imap.dominio
    return f"mail.{domain}"


def check_imapsync_installed():
    """Verifica se o imapsync está instalado"""
    try:
        result = subprocess.run(
            ["imapsync", "--version"], capture_output=True, text=True, timeout=5
        )
        logger.info(f"imapsync encontrado: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        logger.error("imapsync não encontrado. Instale com: brew install imapsync")
        return False
    except Exception as e:
        logger.error(f"Erro ao verificar imapsync: {e}")
        return False


def load_email_accounts(json_file="emails.json"):
    """Carrega as contas de email do arquivo JSON"""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            accounts = json.load(f)
        logger.info(f"Carregadas {len(accounts)} conta(s) do arquivo {json_file}")
        return accounts
    except FileNotFoundError:
        logger.error(f"Arquivo {json_file} não encontrado")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao parsear JSON: {e}")
        return None


def transfer_emails(source, destination, index=0, total=1):
    """
    Transfere emails entre duas contas usando imapsync

    Args:
        source: Dicionário com 'email', 'senha' e opcionalmente 'imap_server' e 'imap_port'
        destination: Dicionário com 'email', 'senha' e opcionalmente 'imap_server' e 'imap_port'
        index: Índice da transferência atual
        total: Total de transferências
    """
    logger.info("=" * 80)
    logger.info(f"Iniciando transferência {index + 1}/{total}")
    logger.info(f"Origem: {source['email']}")
    logger.info(f"Destino: {destination['email']}")
    logger.info("=" * 80)

    # Obter servidores IMAP (personalizado ou auto-detectado)
    # Aceita tanto 'imap' quanto 'imap_server'
    host1 = (
        source.get("imap")
        or source.get("imap_server")
        or get_imap_server_from_email(source["email"])
    )
    host2 = (
        destination.get("imap")
        or destination.get("imap_server")
        or get_imap_server_from_email(destination["email"])
    )

    # Obter portas IMAP (padrão: 993 para SSL)
    port1 = source.get("imap_port", 993)
    port2 = destination.get("imap_port", 993)

    # Verificar se deve usar SSL (padrão: sim)
    use_ssl1 = source.get("use_ssl", True)
    use_ssl2 = destination.get("use_ssl", True)

    logger.info(f"Servidor origem: {host1}:{port1} (SSL: {use_ssl1})")
    logger.info(f"Servidor destino: {host2}:{port2} (SSL: {use_ssl2})")

    # Comando imapsync com opções detalhadas
    cmd = [
        "imapsync",
        "--host1",
        host1,
        "--port1",
        str(port1),
        "--user1",
        source["email"],
        "--password1",
        source["senha"],
    ]

    # Adicionar SSL se necessário
    if use_ssl1:
        cmd.append("--ssl1")

    cmd.extend(
        [
            "--host2",
            host2,
            "--port2",
            str(port2),
            "--user2",
            destination["email"],
            "--password2",
            destination["senha"],
        ]
    )

    # Adicionar SSL se necessário
    if use_ssl2:
        cmd.append("--ssl2")

    # Opções adicionais
    cmd.extend(
        [
            "--syncinternaldates",  # Preservar datas internas
            "--syncacls",  # Sincronizar ACLs
            "--subscribe",  # Inscrever nas pastas
            "--nofoldersizes",  # Não calcular tamanhos (mais rápido)
            "--useheader",
            "Message-Id",  # Evitar duplicatas
            "--useheader",
            "Date",
            "--skipsize",  # Pular verificação de tamanho
            "--allowsizemismatch",  # Permitir diferenças de tamanho
            "--no-modulesversion",  # Não verificar versões de módulos
            "--noreleasecheck",  # Não verificar novas versões
        ]
    )

    try:
        logger.info("Executando imapsync...")
        logger.info(f"Comando: imapsync (senha omitida por segurança)")

        # Executar o comando
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Ler output em tempo real
        for line in process.stdout:
            line = line.strip()
            if line:
                logger.info(f"imapsync: {line}")

        # Aguardar conclusão
        return_code = process.wait()

        # Capturar stderr se houver
        stderr_output = process.stderr.read()
        if stderr_output:
            logger.warning(f"Avisos/Erros: {stderr_output}")

        if return_code == 0:
            logger.info("✓ Transferência concluída com sucesso!")
            return True
        else:
            logger.error("=" * 80)
            logger.error("✗ ERRO NA TRANSFERÊNCIA")
            logger.error(f"Email origem: {source['email']}")
            logger.error(f"Email destino: {destination['email']}")
            logger.error(f"Servidor origem: {host1}:{port1}")
            logger.error(f"Servidor destino: {host2}:{port2}")
            logger.error(f"Código de saída: {return_code}")
            logger.error("=" * 80)
            return False

    except subprocess.TimeoutExpired:
        logger.error("=" * 80)
        logger.error("✗ TIMEOUT NA TRANSFERÊNCIA")
        logger.error(f"Email origem: {source['email']}")
        logger.error(f"Email destino: {destination['email']}")
        logger.error("O processo demorou muito tempo para responder")
        logger.error("=" * 80)
        return False
    except Exception as e:
        logger.error("=" * 80)
        logger.error("✗ EXCEÇÃO DURANTE TRANSFERÊNCIA")
        logger.error(f"Email origem: {source['email']}")
        logger.error(f"Email destino: {destination['email']}")
        logger.error(f"Erro: {e}")
        logger.error("=" * 80)
        return False


def main():
    """Função principal"""
    logger.info("=" * 80)
    logger.info("INICIANDO SCRIPT DE TRANSFERÊNCIA DE EMAILS")
    logger.info(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info(f"Arquivo de log: {log_filename}")
    logger.info("=" * 80)

    # Verificar se imapsync está instalado
    if not check_imapsync_installed():
        logger.error("Por favor, instale o imapsync antes de continuar")
        logger.info("macOS: brew install imapsync")
        logger.info(
            "Linux: apt-get install imapsync ou consulte https://imapsync.lamiral.info/"
        )
        sys.exit(1)

    # Carregar contas
    accounts = load_email_accounts()
    if not accounts:
        logger.error("Não foi possível carregar as contas de email")
        sys.exit(1)

    # Estatísticas
    total_accounts = len(accounts)
    success_count = 0
    failed_count = 0

    # Processar cada conta
    failed_accounts = []  # Lista para armazenar contas que falharam

    for idx, account in enumerate(accounts):
        try:
            source = account.get("from")
            destination = account.get("to")

            if not source or not destination:
                logger.warning(f"Conta {idx + 1} com dados incompletos, pulando...")
                failed_count += 1
                failed_accounts.append(
                    {
                        "index": idx + 1,
                        "source": source.get("email", "N/A") if source else "N/A",
                        "destination": (
                            destination.get("email", "N/A") if destination else "N/A"
                        ),
                        "error": "Dados incompletos no JSON",
                    }
                )
                continue

            # Realizar transferência
            success = transfer_emails(source, destination, idx, total_accounts)

            if success:
                success_count += 1
            else:
                failed_count += 1
                failed_accounts.append(
                    {
                        "index": idx + 1,
                        "source": source.get("email", "N/A"),
                        "destination": destination.get("email", "N/A"),
                        "error": "Falha na transferência (veja logs acima)",
                    }
                )

        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"✗ ERRO AO PROCESSAR CONTA {idx + 1}")
            if source:
                logger.error(f"Email origem: {source.get('email', 'N/A')}")
            if destination:
                logger.error(f"Email destino: {destination.get('email', 'N/A')}")
            logger.error(f"Erro: {e}")
            logger.error("=" * 80)
            failed_count += 1
            failed_accounts.append(
                {
                    "index": idx + 1,
                    "source": source.get("email", "N/A") if source else "N/A",
                    "destination": (
                        destination.get("email", "N/A") if destination else "N/A"
                    ),
                    "error": str(e),
                }
            )

    # Resumo final
    logger.info("=" * 80)
    logger.info("RESUMO DA TRANSFERÊNCIA")
    logger.info(f"Total de contas: {total_accounts}")
    logger.info(f"Transferências bem-sucedidas: {success_count}")
    logger.info(f"Transferências com falha: {failed_count}")
    logger.info(f"Log salvo em: {log_filename}")
    logger.info("=" * 80)

    # Mostrar detalhes das contas que falharam
    if failed_accounts:
        logger.error("")
        logger.error("=" * 80)
        logger.error("CONTAS QUE FALHARAM:")
        logger.error("=" * 80)
        for failed in failed_accounts:
            logger.error(f"")
            logger.error(f"Conta #{failed['index']}:")
            logger.error(f"  Origem: {failed['source']}")
            logger.error(f"  Destino: {failed['destination']}")
            logger.error(f"  Motivo: {failed['error']}")
        logger.error("")
        logger.error("=" * 80)

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\nOperação cancelada pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)
