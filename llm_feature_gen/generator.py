from textwrap import dedent
from .client import OllamaClient

DEFAULT_TEXT_MODEL = "llama3.2"
VISION_MODEL = "llava:7b-v1.5-q4_0"

DEFAULT_PROMPT = """
Eres un ingeniero QA senior.
A partir de la documentación proporcionada (y de la interfaz, si existe), genera exactamente {n} escenarios en formato Gherkin (.feature) en español, que cubran tanto el camino feliz como casos límite relevantes.

Requisitos:
La salida debe contener ÚNICAMENTE el contenido del archivo .feature, sin explicaciones ni comentarios adicionales.

La estructura debe ser:

vbnet
Copiar
Editar
Feature: [Nombre de la funcionalidad]
  [Descripción breve en español]

  Scenario: [Nombre del escenario]
    Given ...
    When ...
    And ...
    Then ...
Aunque los pasos estén redactados en español, los keywords iniciales deben estar en inglés (Feature, Scenario, Given, When, And, Then).

No incluyas ningún texto adicional fuera del contenido de la feature.

El contenido debe ser válido para ser guardado directamente como archivo .feature.
""".strip()


class FeatureGenerator:
    def __init__(
        self,
        text_model: str = DEFAULT_TEXT_MODEL,
        vision_model: str = VISION_MODEL,
    ):
        self.client = OllamaClient()
        self.text_model = text_model
        self.vision_model = vision_model

    # ---- visión ------------------------------------------------------------
    def describe_ui(self, image_path: str) -> str:
        encoded = self.client.encode_image(image_path)
        return self.client.generate(
            self.vision_model,
            """
               Actúa como un ingeniero QA experto en interfaces.

                Debes observar exclusivamente la imagen proporcionada y **describir con el máximo nivel de detalle todos los elementos visibles en la interfaz**, sin analizar el prompt ni escribir texto explicativo adicional.
                Instrucciones:
                - **No expliques tu análisis. No des conclusiones. No resumas.**
                - **No describas este texto. Ignora el contenido de este prompt.**
                - Tu única tarea es **listar y describir** lo que aparece en la imagen de forma precisa y directa.
                - Describe:
                  - Textos visibles (etiquetas, títulos, campos, mensajes)
                  - Botones (texto, color, ubicación)
                  - Campos de entrada, menús, enlaces, íconos, estados visuales, colores, estructuras, banners
                  - Todo lo visible, aunque parezca irrelevante
                - Usa frases cortas, claras y descriptivas, como en un informe técnico visual.
                
                No incluyas frases como “en resumen”, “probablemente”, “la interfaz es”, “se presenta”.
                
                **Objetivo**: generar una descripción literal de la imagen para que otro QA pueda generar casos de uso sin necesidad de verla.
                
                **Salida esperada**: solo la descripción detallada de la interfaz.
            """, images=[encoded],
        )

    def _build_prompt(
        self,
        requirements: str,
        ui_desc: str | None,
        n: int,
        custom_prompt: str | None,
    ) -> str:
        template = custom_prompt or DEFAULT_PROMPT
        return (
            dedent(template.format(n=n))
            + f"\n\n### Documentación\n{requirements}\n\n### UI\n{ui_desc or 'N/A'}"
        )

    def generate(
        self,
        requirements: str,
        ui_desc: str | None = None,
        n: int = 5,
        custom_prompt: str | None = None,
    ) -> str:
        prompt = self._build_prompt(requirements, ui_desc, n, custom_prompt)
        return self.client.generate(self.text_model, prompt)
