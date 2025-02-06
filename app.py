import streamlit as st
import requests
import json
import time
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente definidas no arquivo .env
load_dotenv()

st.secrets["BASE_API_URL"]
st.secrets["FLOW_ID"]
st.secrets["API_KEY"]

# Configuração inicial do Streamlit
st.set_page_config(
    page_title="Assistente Bernhoft",
    page_icon="🤖",
    layout="centered",
)

# CSS customizado para melhorar a interface
st.markdown(
    """
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f8f9fa;
        }
        .chat-container {
            max-width: 700px;
            margin: auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        }
        .chat-box {
            border: none;
            width: 100%;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            padding: 12px;
            border-radius: 10px;
            margin: 10px 0;
            text-align: right;
            width: fit-content;
            max-width: 80%;
            align-self: flex-end;
        }
        .bot-message {
            background-color: #000000;
            padding: 12px;
            border-radius: 10px;
            margin: 10px 0;
            text-align: left;
            width: fit-content;
            max-width: 80%;
            align-self: flex-start;
        }
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin: 5px;
        }
        .user-container, .bot-container {
            display: flex;
            align-items: center;
        }
        .user-container {
            justify-content: flex-end;
        }
        .bot-container {
            justify-content: flex-start;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Cabeçalho
st.markdown("<h2 style='text-align: center;'>Assistente Bernhoft 🤖</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Converse com nosso assistente de IA.</p>", unsafe_allow_html=True)

# Inicializando o chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Função para chamar a API do Langflow com tratamento de erros
def call_langflow_api(message):
    api_url = f"{BASE_API_URL}/api/v1/run/{FLOW_ID}"
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }
    headers = {"x-api-key": API_KEY} if API_KEY else {}

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()  # Levanta erro para códigos 4xx ou 5xx
        response_data = response.json()

        # Log da resposta completa para debug
        st.write(f"📩 Resposta da API: `{json.dumps(response_data, indent=2)}`")

        # Extraindo corretamente a resposta dentro de 'outputs'
        try:
            text_response = response_data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
            return text_response
        except KeyError:
            return "⚠️ Erro ao interpretar a resposta. Estrutura inesperada na API."

    except requests.exceptions.RequestException as e:
        st.error(f"🚨 Erro ao conectar com a API: {e}")
        return f"Erro ao conectar com a API: {e}"

# Exibindo o histórico de mensagens com formatação
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="user-container">
                <div class="user-message">{msg['content']}</div>
                <img src="https://cdn-icons-png.flaticon.com/512/4825/4825038.png" class="avatar">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="bot-container">
                <img src="https://cdn-icons-png.flaticon.com/512/4712/4712038.png" class="avatar">
                <div class="bot-message">{msg['content']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# ---- Lógica de recebimento de mensagem modificada (baseada no código de referência) ----

# Inicializa o estágio caso não exista
if "stage" not in st.session_state:
    st.session_state.stage = "user"

if st.session_state.stage == "user":
    # Recebe a mensagem do usuário via st.chat_input (sem o uso de form)
    user_input = st.chat_input("Digite sua mensagem...")
    if user_input and user_input.strip():
        # Adiciona a mensagem do usuário ao histórico imediatamente
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.stage = "assistant"  # Muda o estágio para processar a resposta
        st.rerun()

elif st.session_state.stage == "assistant":
    # Usa a última mensagem do usuário para chamar a API
    last_user_message = st.session_state.messages[-1]["content"]
    with st.spinner("Assistente está digitando..."):
        time.sleep(1)  # Pequeno delay para melhorar a fluidez
        bot_response = call_langflow_api(last_user_message)
    # Adiciona a resposta do assistente ao histórico
    st.session_state.messages.append({"role": "bot", "content": bot_response})
    st.session_state.stage = "user"  # Retorna ao estágio de input do usuário
    st.rerun()
