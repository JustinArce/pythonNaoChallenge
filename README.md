# 🤖 Proyecto NAO + GPT-3.5 (Reto Nao Python IA++)

Este repositorio contiene el código utilizado en el reto **NAO Python IA++** del Robotifest 2023. El proyecto integra el robot NAO (v2.1.4.13) con la API de OpenAI (usando `gpt-3.5-turbo-instruct`) para crear un asistente educativo interactivo capaz de mantener conversaciones y responder preguntas complejas de forma amigable.

## 🌟 Características Principales

* **Integración con IA:** Conecta al robot NAO con el poder de los modelos de lenguaje de GPT-3.5.
* **Asistente Educativo:** El *prompt* de la IA está diseñado para que NAO actúe como un asistente educativo, explicando temas de forma clara y concisa para todas las audiencias (niños y adultos mayores).
* **Dos Modos de Entrada:** El proyecto incluye dos planes diferentes para la captura de audio:
    * **Plan A (`IA_PlanA_MicPC.py`):** Utiliza el micrófono de la computadora (PC) que ejecuta el script para el reconocimiento de voz.
    * **Plan B (`IA_PlanB_MicNao.py`):** Utiliza los micrófonos incorporados del robot NAO para grabar el audio y los sensores táctiles (cabeza y manos) para iniciar y detener la interacción.
* **Interacción Natural:** Utiliza palabras clave ("hola", "nao", "adios") para activar y desactivar al robot.
* **Habla Animada:** Emplea la API `ALAnimatedSpeech` de NAOqi para que el robot gesticule y se mueva mientras habla, creando una interacción más natural.
* **Memoria de Conversación:** La IA mantiene un contexto de los últimos intercambios para dar respuestas más coherentes.

## 🛠️ Requisitos

Para ejecutar este proyecto, necesitarás:

* Un robot NAO (versión 2.1.4.13).
* Python 2.7 (para ser compatible con la SDK de NAOqi).
* La [SDK de NAOqi Python](httpss://developer.softbankrobotics.com/nao-6/naoqi-2-framework/python-sdk).
* Las siguientes bibliotecas de Python:

```bash
pip install SpeechRecognition==2.2.0
pip install pyaudio==0.2.9
pip install openai==0.2.0
```

## 🚀 Instrucciones de Configuración

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
    cd TU_REPOSITORIO
    ```

2.  **Instalar Dependencias:**
    Asegúrate de tener la SDK de NAOqi configurada en tu `PYTHONPATH` e instala las bibliotecas de `pip` listadas arriba.

3.  **Crear Archivo de Entorno (`env.py`):**
    Este proyecto requiere una clave de API de OpenAI.
    * Crea un archivo llamado `env.py` en la misma carpeta.
    * Añade tu clave de API dentro de ese archivo, de la siguiente manera:
    ```python
    # env.py
    apikey = "TU_CLAVE_DE_API_DE_OPENAI_VA_AQUI"
    ```
    *(Este archivo será ignorado por Git para proteger tu clave).*

4.  **Configurar el Script:**
    Abre el archivo `.py` que deseas usar (Plan A o Plan B) y actualiza las variables `IP` y `PORT` para que coincidan con la configuración de tu robot NAO.

    ```python
    # Parámetros de conexión 
    IP = "tu_ip_del_robot.local."   # IP del robot
    PORT = 9559                      # Puerto del robot (usualmente 9559)
    ```
    *(Nota: El `PORT` en tu script original (58739) parece ser un puerto personalizado. El puerto estándar de NAOqi es 9559. Ajústalo según sea necesario).*

5.  **Ejecutar el Proyecto:**
    ```bash
    python IA_PlanA_MicPC.py
    ```
    o
    ```bash
    python IA_PlanB_MicNao.py
    ```

## 📜 Contexto del Proyecto

Este código fue desarrollado para el reto "NAO Python IA++", donde obtuvo el segundo lugar. El objetivo era demostrar la integración de capacidades avanzadas de IA en la plataforma NAO para crear aplicaciones útiles e interactivas.

¡Gracias por visitar el repositorio!
