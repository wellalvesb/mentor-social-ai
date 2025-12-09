import os
import re
import sqlite3
import base64
import uvicorn
import edge_tts
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq

# --- CONFIGURAÇÃO ---
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

SYSTEM_PROMPT = """
Você é o 'Júnior', um mentor de negócios amigo e popular.
Ajude empreendedores de baixo letramento.

REGRAS:
1. JAMAIS USE ASTERISCOS (*) ou formatação.
2. Seja breve, direto e encorajador.
3. Use o histórico da conversa para dar conselhos personalizados.
"""

app = FastAPI()

# --- BANCO DE DADOS (SQLite) ---
def iniciar_banco():
    conn = sqlite3.connect('junior_memoria.db')
    cursor = conn.cursor()
    # Cria a tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def salvar_mensagem(user_id, role, content):
    conn = sqlite3.connect('junior_memoria.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO conversas (user_id, role, content) VALUES (?, ?, ?)', 
                  (user_id, role, content))
    conn.commit()
    conn.close()

def recuperar_historico(user_id, limite=20):
    conn = sqlite3.connect('junior_memoria.db')
    cursor = conn.cursor()
    # Pega as últimas X mensagens
    cursor.execute('''
        SELECT role, content FROM conversas 
        WHERE user_id = ? 
        ORDER BY id DESC LIMIT ?
    ''', (user_id, limite))
    mensagens = cursor.fetchall()
    conn.close()
    
    # O banco devolve do mais novo pro mais velho, precisamos inverter
    historico_formatado = [{"role": m[0], "content": m[1]} for m in mensagens]
    return historico_formatado[::-1] # Inverte a lista

# Inicia o banco assim que o código carrega
iniciar_banco()

class ZapMessage(BaseModel):
    user_id: str
    message: Optional[str] = None 
    text: Optional[str] = None    
    audio_base64: Optional[str] = None

# --- LIMPEZA E VOZ ---
def limpar_texto_para_audio(texto):
    if not texto: return ""
    texto = re.sub(r'\*.*?\*', '', texto)
    texto = texto.replace('*', '').replace('#', '').replace('_', '')
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

async def gerar_voz(texto):
    try:
        texto_limpo = limpar_texto_para_audio(texto)
        if not texto_limpo: texto_limpo = "Entendi."
        
        comunicar = edge_tts.Communicate(texto_limpo, "pt-BR-AntonioNeural")
        filename = f"resp_{os.getpid()}.mp3"
        await comunicar.save(filename)
        return filename
    except Exception as e:
        print(f"⚠️ Erro TTS: {e}")
        return None

# --- ROTA PRINCIPAL ---
@app.post("/chat")
async def chat_endpoint(dados: ZapMessage):
    user_id = dados.user_id
    # Pega texto de qualquer campo que vier
    texto_usuario = dados.message or dados.text or ""
    
    print(f"\n📩 Mensagem de {user_id}")

    # 1. PROCESSAR ÁUDIO (Se houver)
    if dados.audio_base64:
        try:
            b64 = dados.audio_base64.split(",")[1] if "," in dados.audio_base64 else dados.audio_base64
            arquivo_temp = "temp_audio.ogg"
            with open(arquivo_temp, "wb") as f:
                f.write(base64.b64decode(b64))
            with open(arquivo_temp, "rb") as arquivo_audio:
                transcricao = client.audio.transcriptions.create(
                    file=(arquivo_temp, arquivo_audio),
                    model="whisper-large-v3",
                    language="pt"
                )
            texto_usuario = transcricao.text
            print(f"📝 Ouvido: {texto_usuario}")
        except Exception:
            return {"response_text": "Não consegui ouvir...", "audio_response": None}

    if not texto_usuario:
        return {"response_text": "...", "audio_response": None}

    # 2. INTELIGÊNCIA COM MEMÓRIA ETERNA
    try:
        # A) Salva o que o usuário disse no banco
        salvar_mensagem(user_id, "user", texto_usuario)

        # B) Busca o histórico recente (últimas 20 trocas) para dar contexto
        historico = recuperar_historico(user_id, limite=20)
        
        # C) Monta o prompt
        mensagens_para_enviar = [{"role": "system", "content": SYSTEM_PROMPT}] + historico

        # D) Chama a IA
        completion = client.chat.completions.create(
            messages=mensagens_para_enviar,
            model="llama-3.3-70b-versatile",
            temperature=0.7 
        )
        resposta_texto = completion.choices[0].message.content
        
        # E) Salva a resposta da IA no banco
        salvar_mensagem(user_id, "assistant", resposta_texto)
        
        print(f"🤖 Resposta: {resposta_texto}")

    except Exception as e:
        erro = f"Erro IA: {str(e)}"
        print(erro)
        return {"response_text": erro, "audio_response": None}

    # 3. GERAR VOZ
    audio_b64 = None
    try:
        if resposta_texto:
            arquivo_mp3 = await gerar_voz(resposta_texto)
            if arquivo_mp3:
                with open(arquivo_mp3, "rb") as f:
                    audio_b64 = base64.b64encode(f.read()).decode('utf-8')
                os.remove(arquivo_mp3)
    except Exception:
        pass

    return {
        "response_text": resposta_texto,
        "audio_response": audio_b64
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)