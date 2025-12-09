# 🎙️ Mentor Social AI - Chatbot de Voz no WhatsApp

> **Inclusão Digital na Prática:** Um assistente de IA que ouve, entende e fala com empreendedores de baixo letramento, rodando 100% na nuvem AWS.

![Badge Status](https://img.shields.io/badge/Status-Concluído-success)
![AWS](https://img.shields.io/badge/Cloud-AWS_EC2-orange)
![Python](https://img.shields.io/badge/Backend-Python_FastAPI-blue)
![Node](https://img.shields.io/badge/Bridge-Node.js-green)
![AI](https://img.shields.io/badge/Model-Llama_3_(Groq)-purple)

---

## 💡 O Problema
A IA Generativa é revolucionária, mas excludente. Milhões de microempreendedores possuem **baixo letramento digital**, ficando impedidos de usar ferramentas baseadas em texto complexo.

## 🛠️ A Solução
O **Mentor Social AI** quebra essa barreira. Ele atua como um "Consultor de Negócios de Bolso" acessível via áudio.
1. O usuário envia um áudio com sua dúvida.
2. O sistema transcreve e processa com Llama 3 (instruído para didática simplificada).
3. A resposta retorna em **áudio natural**, com tom acolhedor.

---

## 🏗️ Arquitetura Técnica
O projeto utiliza uma arquitetura híbrida de microsserviços em **AWS EC2 (Linux Ubuntu)**.

- **Infraestrutura:** AWS EC2 (`t3.micro`), PM2 (Gerenciador de Processos 24/7).
- **Cérebro (Python):** FastAPI, Edge-TTS (Síntese de voz neural), Groq Cloud (Llama 3).
- **Ouvidos (Node.js):** WhatsApp-Web.js, Puppeteer (Headless Chrome), Axios.
- **Segurança:** Configuração de Swap Memory e Controle de Orçamento AWS.

---

## 🚀 Como testar
Este projeto foi desenhado para rodar como um **Agente Autônomo**.
O código fonte demonstra a integração entre Python e Node.js para processamento de áudio em tempo real.

---
**Desenvolvido por Welton** 🚀