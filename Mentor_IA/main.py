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
# --- PERSONALIDADE ---
SYSTEM_PROMPT = """
Você é o 'Júnior', um mentor de negócios amigo e popular.
Fale com empreendedores brasileiros simples.
REGRAS:
1. Responda APENAS em texto.
2. Seja breve, direto e use emojis moderadamente.
3. NUNCA use formatação markdown (negrito ** ou itálico *), use apenas texto puro.
4. Use o histórico da conversa para manter o contexto.
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
            # ESTE É O MODELO NOVO E ESTÁVEL (O antigo foi desligado)
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300
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