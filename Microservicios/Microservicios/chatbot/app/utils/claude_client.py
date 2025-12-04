import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def generar_respuesta_claude(mensaje_usuario, contexto=""):
    try:
        respuesta = client.messages.create(
            model="claude-3-haiku-20240307",  # Puedes usar claude-3-opus o claude-3-sonnet
            max_tokens=500,
            temperature=0.7,
            system=(
                "Eres un asesor virtual de Global Speed. "
                "Tu tarea es ayudar a los usuarios a elegir el mejor plan de internet "
                "según sus necesidades, basándote únicamente en la información proporcionada."
            ),
            messages=[
                {"role": "user", "content": f"{mensaje_usuario}\n\n{contexto}"}
            ]
        )
        return respuesta.content[0].text.strip()
    except Exception as e:
        print("❌ Error al consultar Claude:", e)
        return "Ocurrió un error al generar una respuesta inteligente. Intenta nuevamente."
