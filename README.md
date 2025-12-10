# 🤖 Mentor Social AI — Inclusão Digital via WhatsApp

> **Inclusão Digital na Prática:** Um assistente de IA que ouve, entende e orienta microempreendedores de baixo letramento, rodando 100% na nuvem AWS.

![Status](https://img.shields.io/badge/Status-Online_na_AWS-green?style=for-the-badge&logo=amazonaws)
![Python](https://img.shields.io/badge/Backend-FastAPI-blue?style=for-the-badge&logo=python)
![Node](https://img.shields.io/badge/Bridge-Node.js-green?style=for-the-badge&logo=nodedotjs)
![AI](https://img.shields.io/badge/AI-Llama_3.3_70B-purple?style=for-the-badge&logo=openai)

## 💡 O Problema
A IA generativa é poderosa, mas excludente. Milhões de microempreendedores no Brasil possuem **baixo letramento digital** ou dificuldades de leitura, o que os impede de usar ferramentas baseadas em texto (prompts complexos). Isso cria um abismo de acesso à tecnologia.

## 🚀 A Solução
O **Mentor Social AI** elimina essa barreira, funcionando como um "Consultor de Negócios de Bolso" acessível via **áudio** na plataforma mais popular do país: o WhatsApp.

**O Fluxo Simplificado:**
1.  🗣️ **Usuário:** Grava um áudio com sua dúvida (ex: *"Como precifico meu bolo?"*).
2.  👂 **Ouve:** O sistema transcreve o áudio com alta precisão (**Whisper V3**).
3.  🧠 **Pensa:** O modelo **Llama 3.3** analisa o contexto e gera uma orientação prática.
4.  💬 **Responde:** O usuário recebe a resposta em texto claro, empático e direto no WhatsApp.

---

## 🛠️ Arquitetura Técnica

O projeto utiliza uma arquitetura híbrida de microsserviços hospedada na **AWS EC2**, garantindo alta disponibilidade e baixo custo.

```mermaid
graph TD
    User([👤 Usuário]) -- Áudio (Ogg) --> Zap[🟢 Zap Bridge\n(Node.js + whatsapp-web.js)]
    
    subgraph AWS Cloud [☁️ AWS EC2 (Ubuntu 24.04)]
        Zap -- POST JSON + Base64 --> Mentor[🔵 Mentor_IA\n(Python FastAPI)]
        Mentor -- Salva/Lê --> DB[(🗄️ SQLite\nHistórico)]
    end
    
    subgraph Groq Cloud [⚡ Groq API (Inference)]
        Mentor -- 1. Envia Áudio --> Whisper(👂 Whisper V3\nSpeech-to-Text)
        Whisper -- 2. Retorna Texto --> Mentor
        Mentor -- 3. Envia Contexto --> Llama(🧠 Llama 3.3\nLLM 70B)
        Llama -- 4. Retorna Resposta --> Mentor
    end
    
    Mentor -- 5. Resposta Texto --> Zap
    Zap -- 6. Envia Msg --> User

    💻 Tecnologias Utilizadas
Infraestrutura & DevOps
AWS EC2 (t3.micro): Servidor Linux Ubuntu 24.04.

PM2: Gerenciador de processos para manter a aplicação online 24/7.

SSH: Acesso remoto seguro.

Backend (Cérebro)
Python 3.10+ & FastAPI: API rápida e assíncrona.

Groq SDK: Para inferência de IA com latência ultrabaixa.

SQLite: Persistência de memória de conversação.

Interface (Bridge)
Node.js: Runtime leve.

Whatsapp-web.js: Biblioteca para automação do WhatsApp.

Puppeteer: Navegador headless para autenticação via QR Code.

📂 Estrutura do Projeto
├── Mentor_IA/          # Microsserviço Python (Cérebro)
│   ├── main.py         # Lógica de IA, Rotas e Transcrição
│   ├── junior_memoria.db # Banco de dados (Histórico)
│   └── requirements.txt # Dependências (fastapi, groq, uvicorn)
│
├── Zap_Bridge/         # Microsserviço Node.js (Interface)
│   ├── index.js        # Conexão Socket com WhatsApp
│   └── package.json    # Dependências (whatsapp-web.js, axios)
│
└── README.md           # Documentação

🔧 Como Rodar Localmente
Pré-requisitos
Python 3.10+

Node.js 18+

Chave de API da Groq Cloud

1. Clone o Repositório
Bash

git clone [https://github.com/wellalvesb/mentor-social-ai.git](https://github.com/wellalvesb/mentor-social-ai.git)
cd mentor-social-ai
2. Backend (Python)
Bash

cd Mentor_IA
# Cria e ativa o ambiente virtual
python -m venv venv
# Windows: venv\Scripts\activate | Linux: source venv/bin/activate

# Instala dependências
pip install -r requirements.txt

# Configura a Chave (Linux/Mac) ou use $env: no Windows
export GROQ_API_KEY="sua_chave_aqui"

# Roda o servidor na porta 5000
python main.py
3. Bridge (Node.js)
Em outro terminal:

Bash

cd Zap_Bridge
npm install
node index.js
Escaneie o QR Code que aparecerá no terminal com seu WhatsApp.

👨‍💻 Desenvolvedor
Desenvolvido por Welton Alves 