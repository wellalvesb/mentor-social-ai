import os
import sqlite3
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from typing import Optional
import base64

# --- CONFIGURAÇÃO GROQ (CÉREBRO E OUVIDOS) ---
# Sua chave Groq (Válida para Textos e Áudios)
# Substitua a linha da chave por isso antes de salvar:
# --- CONFIGURAÇÃO ---
# Chave Groq (Llama 3.3 + Whisper V3)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "SUA_CHAVE_AQUI")
client = Groq(api_key=GROQ_API_KEY)

# --- PERSONALIDADE (JÚNIOR - O MENTOR DIDÁTICO E OBJETIVO) ---
# --- PERSONALIDADE (JÚNIOR - O MENTOR CONTA-GOTAS) ---
SYSTEM_PROMPT = """
IDENTIDADE:
Você é o 'Júnior', um Mentor de Negócios parceiro e prático.
Seu público tem pressa e baixo letramento digital.

REGRAS DE OURO (ANTI-TEXTÃO):
1. **REGRA DO CONTA-GOTAS:** JAMAIS entregue um projeto ou lista gigante de uma vez. Se o assunto for complexo, explique o básico e dê APENAS O PRIMEIRO PASSO.
2. **SIMPLIFICAÇÃO EXTREMA:** Não use termos como "Stakeholders", "Compliance" ou "Infraestrutura" sem explicar. Use metáforas (ex: "Governança é como organizar as prateleiras do estoque").
3. **TAMANHO MÁXIMO:** Sua resposta não pode passar de 3 ou 4 parágrafos curtos. O usuário está no celular.

ESTRUTURA DE RESPOSTA OBRIGATÓRIA:
1. **Confirmação:** "Entendi, Welton!"
2. **Resumo Simples:** Explique o conceito em 1 frase simples.
3. **Ação Imediata (Passo 1):** Diga a primeira coisa que ele tem que fazer.
4. **Gancho:** Pergunte: "Fez sentido? Podemos ir para o próximo passo?"

EXEMPLO DE COMO NÃO FAZER (ERRADO):
"Aqui está seu plano de Governança: 1. Análise, 2. Política, 3. Implementação..." (ISSO É CHATO E LONGO).

EXEMPLO DE COMO FAZER (CORRETO):
"Boa, Welton! Governança de dados parece nome difícil, mas é só 'organizar a casa' para não perder informações importantes. 🧹
O Passo 1 é saber o que você tem hoje.
Pega um papel e anota: Quais dados você guarda dos seus clientes? (Nome, Zap, Endereço?)
Me conta aqui que a gente monta o resto juntos! 👇"
"""


app = FastAPI()

# --- BANCO DE DADOS (SQLite) ---
def iniciar_banco():
    conn = sqlite3.connect('junior_memoria.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT, role TEXT, content TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def salvar_mensagem(user_id, role, content):
    conn = sqlite3.connect('junior_memoria.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO conversas (user_id, role, content) VALUES (?, ?, ?)', (user_id, role, content))
    conn.commit()
    conn.close()

def recuperar_historico(user_id, limite=10):
    conn = sqlite3.connect('junior_memoria.db')
    cursor = conn.cursor()
    cursor.execute('SELECT role, content FROM conversas WHERE user_id = ? ORDER BY id DESC LIMIT ?', (user_id, limite))
    mensagens = cursor.fetchall()
    conn.close()
    
    # Formata para a Groq (user/system/assistant)
    historico = []
    for m in mensagens[::-1]:
        # Converte nomes de roles se necessário
        role = m[0]
        if role == "model": role = "assistant" 
        historico.append({"role": role, "content": m[1]})
    return historico

# Inicia o banco
iniciar_banco()

class ZapMessage(BaseModel):
    user_id: str
    message: Optional[str] = None
    text: Optional[str] = None
    audio_base64: Optional[str] = None

# --- ROTA PRINCIPAL ---
@app.post("/chat")
async def chat_endpoint(dados: ZapMessage):
    user_id = dados.user_id
    texto_usuario = dados.message or dados.text or ""
    
    print(f"\n📩 Mensagem recebida de {user_id}")

    # 1. TRANSCRIÇÃO DE ÁUDIO (Groq Whisper)
    if dados.audio_base64:
        print("🎤 Áudio detectado! Transcrevendo...")
        try:
            # Limpa o base64
            b64_clean = dados.audio_base64
            if "," in b64_clean:
                b64_clean = b64_clean.split(",")[1]
            
            # Salva temporário
            arquivo_temp = f"temp_{user_id}.ogg"
            with open(arquivo_temp, "wb") as f:
                f.write(base64.b64decode(b64_clean))
            
            # Transcreve
            with open(arquivo_temp, "rb") as arquivo_audio:
                transcricao = client.audio.transcriptions.create(
                    file=("audio.ogg", arquivo_audio),
                    model="whisper-large-v3",
                    language="pt"
                )
            texto_usuario = transcricao.text
            print(f"📝 Transcrição: {texto_usuario}")
            
            if os.path.exists(arquivo_temp):
                os.remove(arquivo_temp)
            
        except Exception as e:
            print(f"❌ Erro transcrição: {e}")
            return {"response_text": "Não consegui ouvir o áudio. Pode escrever?", "audio_response": None}

    if not texto_usuario:
        return {"response_text": "...", "audio_response": None}

    # 2. INTELIGÊNCIA (Groq Llama 3.3)
    try:
        # Salva msg do usuário
        salvar_mensagem(user_id, "user", texto_usuario)
        
        # Recupera histórico
        historico = recuperar_historico(user_id)
        
        # Monta as mensagens (Sistema + Histórico + Nova Mensagem)
        mensagens_envio = [{"role": "system", "content": SYSTEM_PROMPT}] + historico
        # Se a última mensagem do histórico não for a atual (caso já tenha salvo), não adiciona duplicado
        # Mas no nosso fluxo, salvamos antes e recuperamos. O recuperar pega a atual. 
        # Ajuste seguro: adicionar a mensagem atual explicitamente se ela não veio no histórico
        if not historico or historico[-1]['content'] != texto_usuario:
             mensagens_envio.append({"role": "user", "content": texto_usuario})

    # Chama a Groq
        chat_completion = client.chat.completions.create(
            messages=mensagens_envio,
            # Modelo Versatile (Rápido e Inteligente)
            model="llama-3.3-70b-versatile",
            
            # 0.5 = Criativo o suficiente para ser simpático, 
            # mas rígido o suficiente para NÃO inventar nomes.
            temperature=0.5, 
            
            # 450 = Margem de segurança. 
            # Ele vai usar só uns 100 ou 150 na prática (por causa do prompt "Seja breve"),
            # mas se precisar explicar algo complexo, ele tem espaço e não corta.
            max_tokens=450
        )
        
        resposta_texto = chat_completion.choices[0].message.content
        
        # Salva resposta
        salvar_mensagem(user_id, "assistant", resposta_texto)
        print(f"🤖 Resposta Groq: {resposta_texto}")

        return {"response_text": resposta_texto, "audio_response": None}

    except Exception as e:
        print(f"❌ Erro Groq: {str(e)}")
        # Se der erro de modelo de novo, fallback para o instant (mais rápido)
        return {"response_text": "Tive um lapso de memória, pode repetir?", "audio_response": None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)