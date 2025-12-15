# Transfer Mail - Transferência de Emails com imapsync

Script Python para transferir emails entre contas usando [imapsync](https://github.com/imapsync/imapsync).

## 📋 Pré-requisitos

### Instalar imapsync

**macOS:**

```bash
brew install imapsync
```

**Linux (Debian/Ubuntu):**

```bash
sudo apt-get install imapsync
```

**Outras plataformas:**
Consulte a [documentação oficial](https://imapsync.lamiral.info/)

### Instalar Python 3

Python 3.7 ou superior é necessário.

## 🚀 Como usar

### 1. Configurar as contas em `emails.json`

Edite o arquivo `emails.json` com suas contas:

```json
[
    {
        "from": {
            "email": "origem@exemplo.com",
            "senha": "senha_origem"
        },
        "to": {
            "email": "destino@exemplo.com",
            "senha": "senha_destino"
        }
    }
]
```

Você pode adicionar múltiplas contas no array.

### 2. Configurar servidores IMAP

Edite o arquivo `transfer_emails.py` e ajuste os servidores IMAP nas linhas:

```python
'--host1', 'imap.gmail.com',  # Servidor IMAP de origem
'--host2', 'imap.gmail.com',  # Servidor IMAP de destino
```

**Exemplos de servidores IMAP:**

- Gmail: `imap.gmail.com`
- Outlook/Hotmail: `outlook.office365.com`
- Yahoo: `imap.mail.yahoo.com`
- iCloud: `imap.mail.me.com`

### 3. Executar o script

```bash
python3 transfer_emails.py
```

ou

```bash
chmod +x transfer_emails.py
./transfer_emails.py
```

## 📊 Logs

Os logs são salvos em dois lugares:

1. **Console:** Saída em tempo real durante a execução
2. **Arquivo:** Pasta `logs/transfer_YYYYMMDD_HHMMSS.log`

Os logs incluem:

- Status da conexão
- Progresso da transferência
- Erros e avisos
- Resumo final (total, sucessos, falhas)

## ⚙️ Configurações do imapsync

O script usa as seguintes opções do imapsync:

- `--ssl1` e `--ssl2`: Conexões SSL seguras
- `--syncinternaldates`: Preserva datas originais dos emails
- `--syncacls`: Sincroniza permissões
- `--subscribe`: Inscreve nas pastas
- `--useheader Message-Id`: Evita duplicatas
- `--skipsize`: Acelera o processo
- `--allowsizemismatch`: Permite diferenças de tamanho

## 🔒 Segurança

⚠️ **IMPORTANTE:**

- Nunca comite o arquivo `emails.json` com senhas reais
- Adicione `emails.json` ao `.gitignore`
- Use senhas de aplicativo quando disponível (Gmail, Outlook, etc.)
- Mantenha os logs seguros, pois podem conter informações sensíveis

## 📝 Exemplo de execução

```
2025-12-15 10:30:00 - INFO - ================================================================================
2025-12-15 10:30:00 - INFO - INICIANDO SCRIPT DE TRANSFERÊNCIA DE EMAILS
2025-12-15 10:30:00 - INFO - Data/Hora: 15/12/2025 10:30:00
2025-12-15 10:30:00 - INFO - Arquivo de log: logs/transfer_20251215_103000.log
2025-12-15 10:30:00 - INFO - ================================================================================
2025-12-15 10:30:00 - INFO - imapsync encontrado: imapsync version 2.200
2025-12-15 10:30:00 - INFO - Carregadas 1 conta(s) do arquivo emails.json
2025-12-15 10:30:00 - INFO - ================================================================================
2025-12-15 10:30:00 - INFO - Iniciando transferência 1/1
2025-12-15 10:30:00 - INFO - Origem: origem@exemplo.com
2025-12-15 10:30:00 - INFO - Destino: destino@exemplo.com
2025-12-15 10:30:00 - INFO - ================================================================================
2025-12-15 10:30:00 - INFO - Executando imapsync...
2025-12-15 10:30:05 - INFO - imapsync: Transferindo mensagens...
2025-12-15 10:35:00 - INFO - ✓ Transferência concluída com sucesso!
2025-12-15 10:35:00 - INFO - ================================================================================
2025-12-15 10:35:00 - INFO - RESUMO DA TRANSFERÊNCIA
2025-12-15 10:35:00 - INFO - Total de contas: 1
2025-12-15 10:35:00 - INFO - Transferências bem-sucedidas: 1
2025-12-15 10:35:00 - INFO - Transferências com falha: 0
2025-12-15 10:35:00 - INFO - Log salvo em: logs/transfer_20251215_103000.log
2025-12-15 10:35:00 - INFO - ================================================================================
```

## 🐛 Troubleshooting

### "imapsync não encontrado"
Instale o imapsync conforme as instruções acima.

### "Erro de autenticação"

- Verifique email e senha
- Use senhas de aplicativo se disponível
- Verifique se IMAP está habilitado na conta

### "Conexão recusada"

- Verifique o servidor IMAP correto
- Verifique firewall/antivírus
- Teste a conexão manualmente

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.
