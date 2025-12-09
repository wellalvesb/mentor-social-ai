const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { args: ['--no-sandbox'] }
});

client.on('qr', qr => qrcode.generate(qr, { small: true }));
client.on('ready', () => console.log('✅ Zap Conectado!'));

client.on('message', async msg => {
    // Ignora status e grupos
    if (msg.from.includes('status') || msg.from.includes('@g.us')) return;

    console.log(`📩 Mensagem de: ${msg.from}`);

    // --- PREPARA O PACOTE DE DADOS ---
    let payload = {
        user_id: msg.from,
        message: msg.body || "",       // Garante que nunca vai vazio
        audio_base64: null             // Padrão é null
    };

    // --- SE TIVER MÍDIA (ÁUDIO) ---
    if (msg.hasMedia) {
        try {
            const media = await msg.downloadMedia();
            if (media.mimetype.includes('audio')) {
                console.log('🎤 Áudio detectado!');
                payload.audio_base64 = media.data;
                payload.message = ""; // Limpa texto se for áudio
            }
        } catch (err) {
            console.error('Erro baixar midia:', err);
        }
    }

    // --- ENVIA PRO PYTHON ---
    try {
        const res = await axios.post('http://127.0.0.1:5000/chat', payload);
        const { response_text, audio_response } = res.data;

        // Responde com áudio se tiver, senão texto
        if (audio_response) {
            const mediaResponse = new MessageMedia('audio/mp3', audio_response);
            await client.sendMessage(msg.from, mediaResponse, { sendAudioAsVoice: true });
            console.log('🗣️ Áudio respondido!');
        } else {
            await client.sendMessage(msg.from, response_text);
            console.log('📝 Texto respondido!');
        }

    } catch (error) {
        // Log de erro inteligente
        if (error.response) {
            console.log('❌ O Python recusou os dados (Erro 422/500):');
            console.log(JSON.stringify(error.response.data, null, 2));
        } else {
            console.log('❌ Python desligado ou erro de rede.');
        }
    }
});

client.initialize();