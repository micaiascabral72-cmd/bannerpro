import streamlit as st

# ==========================================
# REGRA DE OURO: Configurar a página ANTES de importar qualquer coisa pesada
# Isso impede o "Crash da Tela Preta" (Timeout de Renderização)
# ==========================================
st.set_page_config(
    page_title="BannerGen AI | Pro Edition",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Agora sim, fazemos os imports pesados e locais
from io import BytesIO
from PIL import Image
from banner_utils import validate_and_resize_image
from ai_service import generate_enhanced_prompt, generate_banner_image, configure_apis

# Inicialização do Estado (Session State) para manter o histórico
if "history" not in st.session_state:
    st.session_state.history = []

# Validação de Setup da API Google
try:
    gemini_client = configure_apis()
except ValueError as e:
    st.error("🚨 Erro de Configuração")
    st.error(str(e))
    st.stop() 

# Interface Principal
st.title("🎨 BannerGen AI (Gemini 3.6 + Imagen 3)")
st.markdown("Transforme ideias simples e uma imagem de referência em **banners profissionais (16:9)**.")

col_form, col_result = st.columns([1, 1.2], gap="large")

with col_form:
    st.subheader("1. Configuração da Arte")
    
    with st.form("banner_form"):
        user_prompt = st.text_area(
            "Descreva o propósito e estilo do seu banner:", 
            placeholder="Ex: Banner para lançamento de um tênis esportivo. Fundo com neon urbano...",
            height=130
        )
        
        uploaded_file = st.file_uploader(
            "Upload da imagem de referência:", 
            type=["jpg", "jpeg", "png"]
        )
        
        submit_button = st.form_submit_button("🚀 Gerar Banner Profissional", use_container_width=True)
        
    if submit_button:
        if not user_prompt.strip():
            st.error("❌ Descreva o que deseja no banner.")
        elif not uploaded_file:
            st.error("❌ Envie uma imagem de referência.")
        else:
            with st.status("Iniciando Pipeline de IA...", expanded=True) as status:
                try:
                    st.write("⚙️ Validando imagem...")
                    processed_image = validate_and_resize_image(uploaded_file)
                    
                    st.write("🧠 Acionando Gemini 3.6 Flash...")
                    enhanced_prompt = generate_enhanced_prompt(gemini_client, user_prompt, processed_image)
                    
                    st.write("🖌️ Renderizando arte com Imagen 3...")
                    final_image = generate_banner_image(gemini_client, enhanced_prompt)
                    
                    st.session_state.history.insert(0, {
                        "user_text": user_prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "image": final_image
                    })
                    
                    status.update(label="✨ Sucesso!", state="complete", expanded=False)
                    
                except Exception as e:
                    status.update(label="Erro", state="error")
                    st.error(f"Falha: {str(e)}")

with col_result:
    st.subheader("2. Resultado Final")
    
    if st.session_state.history:
        latest_banner = st.session_state.history[0]
        
        st.image(latest_banner["image"], caption="Arte renderizada pelo Imagen 3", use_container_width=True)
        
        buf = BytesIO()
        latest_banner["image"].save(buf, format="PNG")
        
        st.download_button(
            label="💾 Baixar Banner (PNG)",
            data=buf.getvalue(),
            file_name="banner_pro.png",
            mime="image/png",
            use_container_width=True,
            type="primary"
        )
        
        with st.expander("Ver Prompt Gerado"):
            st.code(latest_banner["enhanced_prompt"], language="text")
    else:
        st.info("Preencha o formulário ao lado.")
