from google import genai
from google.genai import types
from PIL import Image
import io
import streamlit as st

def configure_apis() -> genai.Client:
    gemini_key = st.secrets.get("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("A chave GEMINI_API_KEY não está configurada nos secrets do Streamlit.")
    return genai.Client(api_key=gemini_key)

def generate_enhanced_prompt(client: genai.Client, user_text: str, image: Image.Image) -> str:
    try:
        system_instruction = (
            "You are an Elite AI Prompt Designer specializing in Graphic Design and Commercial Banners. "
            "Analyze the provided image and the user's intent to create a highly detailed, "
            "professional text-to-image prompt in English. "
            "Your output must specify: visual style, lighting setup, color palette, camera angles, "
            "framing, composition rules (e.g., rule of thirds), and background aesthetics. "
            "DO NOT include any conversational text. OUTPUT ONLY THE FINAL PROMPT ready for image generation."
        )
        user_message = f"User Intent for the banner: {user_text}"

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[image, user_message],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        if response.text:
            return response.text.strip()
        else:
            raise ValueError("O Gemini não retornou nenhum conteúdo válido.")
    except Exception as e:
        st.warning(f"⚠️ Aviso: Falha na análise multimodal. Detalhe: {str(e)}. Usando fallback textual.")
        return (f"A highly professional commercial banner, 8k resolution, photorealistic masterpiece. "
                f"Core theme: {user_text}. Stunning cinematic lighting, perfect composition, vibrant colors.")

def generate_banner_image(client: genai.Client, prompt: str) -> Image.Image:
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=f"{prompt}\n\nGenerate this as a 16:9 widescreen banner image."
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_bytes = part.inline_data.data
                final_image = Image.open(io.BytesIO(image_bytes))
                return final_image
        raise ValueError("O modelo não retornou nenhuma imagem.")
    except Exception as e:
        raise RuntimeError(f"Falha na API de geração de imagem (Gemini Image): {str(e)}")
