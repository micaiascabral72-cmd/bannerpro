import streamlit as st
from io import BytesIO
from PIL import Image

from utils import validate_and_resize_image
from ai_service import generate_enhanced_prompt, generate_banner_image, configure_apis

# 1. Configuração Inicial da Página
st.set_page_config(
    page_title="BannerGen AI | Pro Edition",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicialização do Estado para histórico da sessão
if "history" not in st.session_state:
    st.session_state.history = []

# 3. Validação de Setup da API Google
try:
    gemini_client = configure_apis()
except ValueError as e:
    st.error("🚨 Erro Crítico de Configuração de Segurança")
    st.error(str(e))
    st.info("Para ambiente local: Crie `.streamlit/secrets.toml` com a variável `GEMINI_API_KEY`.")
    st.info("Para deploy: Configure a chave em 'Advanced Settings -> Secrets' no painel do Streamlit Cloud.")
    st.stop() 

# 4. Interface Principal
st.title("🎨 BannerGen AI (Gemini 3.6 + Imagen 3)")
st.markdown("Transforme ideias simples e uma imagem de referência em **banners profissionais (16:9)**. "
            "Nossa IA utiliza o Gemini 3.6 Flash como Diretor de Arte e o Imagen 3 para renderização de altíssima qualidade.")

col_form, col_result = st.columns([1, 1.2], gap="large")

with col_form:
    st.subheader("1. Configuração da Arte")
    
    with st.form("banner_form"):
        user_prompt = st.text_area(
            "Descreva o propósito e estilo do seu banner:", 
            placeholder="Ex: Banner para lançamento de um tênis esportivo. Fundo com neon urbano, piso molhado refletindo luzes, estilo cyberpunk.",
            height=130
        )
        
        uploaded_file = st.file_uploader(
            "Upload da imagem de referência (Produto, Logo, Pessoa):", 
            type=["jpg", "jpeg", "png"],
            help="Tamanho máximo: 5MB. Arquivos muito grandes serão redimensionados automaticamente."
        )
        
        submit_button = st.form_submit_button("🚀 Gerar Banner Profissional", use_container_width=True)
        
    if submit_button:
        if not user_prompt.strip():
            st.error("❌ Por favor, descreva o que deseja no banner.")
        elif not uploaded_file:
            st.error("❌ Por favor, envie uma imagem de referência.")
        else:
            with st.status("Iniciando Pipeline de IA...", expanded=True) as status:
                try:
                    st.write("⚙️ Validando e otimizando imagem...")
                    processed_image = validate_and_resize_image(uploaded_file)
                    
                    st.write("🧠 Acionando Gemini 3.6 Flash (Design Multimodal)...")
                    enhanced_prompt = generate_enhanced_prompt(gemini_client, user_prompt, processed_image)
                    
                    st.write("🖌️ Renderizando arte com Imagen 3 (Isso pode levar de 5 a 15 segundos)...")
                    final_image = generate_banner_image(gemini_client, enhanced_prompt)
                    
                    st.session_state.history.insert(0, {
                        "user_text": user_prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "image": final_image
                    })
                    
                    status.update(label="✨ Banner Concluído com Sucesso!", state="complete", expanded=False)
                    
                except ValueError as ve:
                    status.update(label="Erro de Validação", state="error")
                    st.error(f"Erro nos dados: {str(ve)}")
                except RuntimeError as re:
                    status.update(label="Erro de Geração", state="error")
                    st.error(f"Erro na API do Google: {str(re)}")
                except Exception as e:
                    status.update(label="Erro Inesperado", state="error")
                    st.error(f"Ocorreu um erro sistêmico: {str(e)}")

with col_result:
    st.subheader("2. Resultado Final")
    
    if st.session_state.history:
        latest_banner = st.session_state.history[0]
        
        st.image(latest_banner["image"], caption="Arte renderizada pelo Imagen 3", use_container_width=True)
        
        buf = BytesIO()
        latest_banner["image"].save(buf, format="PNG")
        
        st.download_button(
            label="💾 Baixar Banner em Alta Resolução (PNG)",
            data=buf.getvalue(),
            file_name="banner_pro_imagen3.png",
            mime="image/png",
            use_container_width=True,
            type="primary"
        )
        
        with st.expander("Ver 'Magia' dos Bastidores (Prompt criado pelo Gemini 3.6)"):
            st.markdown("**Este foi o direcionamento técnico enviado para o Imagen 3 renderizar:**")
            st.code(latest_banner["enhanced_prompt"], language="text")
    else:
        st.info("Preencha o formulário ao lado. O resultado aparecerá aqui.")

# 5. Seção de Histórico da Sessão
if len(st.session_state.history) > 1:
    st.markdown("---")
    st.subheader("🕰️ Banners Gerados Anteriormente")
    
    cols = st.columns(3)
    for i, item in enumerate(st.session_state.history[1:4]):
        with cols[i]:
            st.image(item["image"], use_container_width=True)
            st.caption(f"Prompt: {item['user_text'][:40]}...")
