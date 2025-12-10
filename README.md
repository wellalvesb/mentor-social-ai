# 🤖 Mentor Social AI — Inclusão Digital via WhatsApp

> Um assistente de IA projetado para democratizar o acesso à consultoria de negócios para microempreendedores com baixo letramento digital.

![Status](https://img.shields.io/badge/Status-Online_na_AWS-green)
![Python](https://img.shields.io/badge/Python-FastAPI-blue)
![AI](https://img.shields.io/badge/AI-Llama_3.3_70B-purple)

## 💡 O Problema
Milhões de brasileiros têm ótimas ideias de negócio, mas encontram barreiras no uso de ferramentas digitais complexas ou baseadas puramente em texto. A IA Generativa é poderosa, mas muitas vezes inacessível.

## 🚀 A Solução
O **Mentor Social AI** funciona diretamente no WhatsApp. O usuário envia um **áudio** com sua dúvida (ex: "Como precifico meu bolo?"), e o sistema:
1.  **Ouve** (Transcreve o áudio usando Whisper V3).
2.  **Pensa** (Processa a resposta com Llama 3.3 focado em linguagem simples e empática).
3.  **Responde** em texto claro e direto no WhatsApp.

## 🛠️ Arquitetura Técnica
O projeto utiliza uma arquitetura híbrida de microsserviços hospedada no AWS EC2, garantindo alta disponibilidade e baixo custo.

```mermaid
graph TD
    %% Definição dos Componentes
    A[Usuário (Microempreendedor)]
    B(WhatsApp)
    C{Zap Bridge - Node.js}
    D[Mentor IA - FastAPI]
    E[junior_memoria.db - SQLite]
    F[Groq API - Whisper V3]
    G[Groq API - Llama 3.3 70B]

    %% Fluxo de Entrada (Áudio)
    A -- Envia Áudio (Dúvida) --> B
    B -- Recebe Mensagem --> C
    C -- Envia para Processamento --> D

    %% Processamento de Transcrição
    D -- 1. Solicita Transcrição --> F
    F -- 2. Retorna Texto Transcrito --> D

    %% Processamento de Resposta
    D -- 3. Consulta Histórico --> E
    E -- Retorna Histórico --> D
    D -- 4. Solicita Resposta --> G
    G -- 5. Retorna Resposta (Texto) --> D

    %% Fluxo de Saída (Resposta)
    D -- Envia Resposta Final --> C
    C -- Envia Mensagem --> B
    B -- Recebe Resposta --> A
```

### ⚙️ Tecnologias Utilizadas

#### Infraestrutura e DevOps
*   **AWS EC2 (t3.micro):** Servidor Linux Ubuntu 24.04.
*   **PM2:** Gerenciador de processos para manter a aplicação online 24 horas por dia, 7 dias por semana.
*   **SSH:** Acesso remoto seguro.

#### Backend (Cérebro)
*   **Linguagem:** Python 3.11
*   **Framework:** FastAPI
*   **LLM:** Groq API (Llama-3.3-70b-versatile)
*   **Speech-to-Text:** Groq API (Whisper Large V3)
*   **Banco de Dados:** SQLite (junior_memoria.db)

#### Interface (Bridge)
*   **Linguagem:** Node.js
*   **Biblioteca:** whatsapp-web.js

## 📂 Estrutura do Projeto
```bash
├── Mentor_IA/          # Backend Python (FastAPI)
│   ├── main.py         # Lógica de IA e Transcrição
│   └── junior_memoria.db # Banco de dados SQLite (Histórico)
├── Zap_Bridge/         # Serviço Node.js
│   └── index.js        # Conexão com WhatsApp
└── README.md
```

## 🔧 Como Rodar Localmente
Clone o repositório

```bash
git clone https://github.com/wellalvesb/mentor-social-ai.git
```

### Backend (Python)

```bash
cd Mentor_IA
pip install -r requirements.txt
# Adicione sua chave GROQ no código ou variável de ambiente
python main.py
```

### Bridge (Node.js)

```bash
cd Zap_Bridge
npm install
node index.js
```

## 👨‍💻 Desenvolvedor
Desenvolvido por Welton Alves. Focado em soluções em IA 