# -*- encoding: UTF-8 -*- 

"""
# Librerías importadas
## Por favor instalar las siguientes por medio de pip
----------------------------------------
Versiones:
pip install SpeechRecognition==2.2.0
pip install pyaudio==0.2.9
pip install openai==0.2.0
----------------------------------------
"""

# Librerias principales
import speech_recognition as sr     # Reconocimiento de voz
import openai                       # API de OpenAI conexion con GPT
from naoqi import ALProxy, ALModule # Clases de Naoqi v2.1.4.13

# Librerías auxiliares
import copy
import sys
import time


"""
Declaracion de constantes
    Parametros de conexion: IP y PORT
    Palabras claves
"""

# Parametros de conexión 
IP = "msi.local."   # IP del robot
PORT = 58739        # Puerto del robot

# Diccionario de listas de palabras claves
PALABRAS = {
    'saludo' : ["hola", "nao","now"],
    'despedida': ["adios","chao","chau",u'adiós'],
}

# Definición de clases
class NAO():
    """
    Clase que representa al robot NAO y sus acciones
    ...
    Atributos 
    ----------
    tts : object
        API Text-to-speech del nao
    asp : object
        API Animated text del NAO
        Permite al robot moverse mientras habla de forma integrada
    posturas : obj
        API para adoptar posturas
    leds : object
        API que permite controlar leds
    alp : object
        API Autonomous life 
        Permite configurar el modo vida autónoma del robot

    Metodos
    -------
    iniciar()
        Inicializa el robot:
            Configura idioma del TTS a español
            Adopta posición StandInit para activar robot
            Adopta posición Crouch
    saludo()
        El robot pasa al modo escucha activa:
            Adopta posición StandInit
            Inicia vida autónoma
            Dice el mensaje de bienvenida
    despedida()
        El robot se despide:
            Dice texto de despedida
            Adopta posición Crouch

    responder(texto, motor_ia=None)
        El robot genera una respuesta a partir del texto y el motor de IA.
        Posteriormente enciende sus leds y dice la respuesta.
    """


    def __init__(self, ip_nao, port_nao):
        """
        Parametros
        ----------
        ip_nao : str
            IP del robot, en formato string
        port_nao : int
            Numero de puerto del robot
        """
        self.tts = ALProxy("ALTextToSpeech", ip_nao, port_nao)
        self.asp = ALProxy("ALAnimatedSpeech", ip_nao, port_nao)
        self.posturas = ALProxy("ALRobotPosture", ip_nao, port_nao)
        self.leds = ALProxy("ALLeds", ip_nao, port_nao)
        self.alp = ALProxy("ALAutonomousLife", ip_nao, port_nao)

    def iniciar(self):
        self.tts.setLanguage("Spanish")
        self.posturas.goToPosture("StandInit",0.5)
        time.sleep(1)
        self.posturas.goToPosture("Crouch",0.5)
        time.sleep(1)

    def saludo(self):
        nao.posturas.goToPosture("StandInit",0.5)
        time.sleep(1)
        self.alp.setState("solitary")
        time.sleep(0.5)
        try:
            nao.leds.on("AllLeds")
        except:
            print('Error de leds')
        self.asp.say(" ^start(animations/Stand/Gestures/Hey_6) Hola, ^wait(animations/Stand/Gestures/Hey_6)"
                     " ^start(animations/Stand/Gestures/Me_1) soy NAO, tu asistente, preguntame lo que quieras"
                     " y te ayudaré ^wait(animations/Stand/Gestures/Me_1) ")
        print("Hola, soy NAO, tu asistente, preguntame lo que quieras y te ayudare")
        time.sleep(1)


    def despedida(self):
        self.asp.say(" ^start(animations/Stand/Gestures/Hey_1) Adiós. Fue un gusto ayudarte. Espero verte pronto."
                     " ^wait(animations/Stand/Gestures/Hey_1)")
        print("Adios. Fue un gusto ayudarte. Espero verte pronto.")
        time.sleep(0.5)
        self.posturas.goToPosture("Crouch",0.5)
        time.sleep(1)


    def responder(self, texto, generador=None):
        self.leds.rasta(1.5)
        if generador==None:
            self.tts.say("Creo que no tengo respuesta para eso")
            print ("El generador no funciona. Texto Original:\n" + texto)
        else:
            if type(texto) == str:
                respuesta = generador(texto).strip()
            else:
                respuesta = generador((texto.encode('utf-8'))).strip()
            
            if type(respuesta) == str:
                print(respuesta)
                self.asp.say(respuesta, {"bodyLanguageMode":"random"})
            else:
                print(respuesta)
                self.asp.say(respuesta.encode(('utf-8')), {"bodyLanguageMode":"random"})
        time.sleep(0.25)

##Clase IA, genera las respuestas mediante conexion al motor de IA gpt 3.5
class IA():
    """
    Clase que representa la inteligencia artificial, conecta con la API, almacena infomacion de parametros y conversacion
    ...
    Atributos 
    ----------
    ENGINE : str
        API Text-to-speech del nao
    CONTEXT : object
        API Animated text del NAO
        Permite al robot moverse mientras habla de forma integrada
    MT : str
        Limite de tokens maximos por respuesta

    Metodos
    -------
    respuesta(texto)
        Genera una respuesta con un motor de IA a partir del input del usuario y la conversacion anterior:
            Agrega el texto a la lista de conversacion
            Genera una respuesta pasando los parametros y la conversacion al API
            Agrega la respuesta a la lista de conversacion y la devuelve  
    """
    def __init__(self):
        self.ENGINE = "gpt-3.5-turbo-instruct"
        self.CONTEXT = ("\nContexto:Eres NAO, un robot asistente educativo. "
                        "Tu funcion es explicar temas complejos de forma clara y asistir en la educación. "
                        "Debes mantener las respuestas cortas, concisas y claras. Ten en cuenta que tu audiencia "
                        "pueden ser niños y adultos mayores, por lo que debes ser muy amable y entretenido para todos."
                        " Si alguien pregunta donde estás, di que en el Robotifest 2023 de la Universidad de Costa Rica."
                        " Responde utilizando lenguaje sencillo y cordial, como en una conversación, de forma amigable.")
        self.MT = 85
        self.conversacion = []
        openai.api_key = env.apikey

    def respuesta(self, pregunta):
        
        self.conversacion.append("\nPregunta: "+pregunta)

        if len(self.conversacion)==1:
            dialogo = self.conversacion[-1]
        elif len(self.conversacion)>2:
            dialogo = (self.conversacion[-3] + self.conversacion[-2] + self.conversacion[-1])
        else:
            dialogo = "\nPregunta: "+pregunta

        response = openai.Completion.create(
            engine=self.ENGINE,  
            prompt = (self.CONTEXT+dialogo+"\nRespuesta: "),
            max_tokens= self.MT  
        )
        output = (response.choices[0].text)
        end = max([output.rfind('.'), output.rfind('?'), output.rfind('!')])
        if len(output) > 0:
            respuesta = output[:end+1]
        else:
            respuesta = ' '

        if type(respuesta) == str:
            self.conversacion.append("\nRespuesta: "+respuesta)
        else:
            self.conversacion.append("\nRespuesta: "+respuesta.encode('utf-8'))

        return respuesta
    

"""
Codigo principal
MAIN

Se inicializan las clases: NAO, IA, sr.Recognizer 
Se configuran modificadores, variables y se enciende el robot

"""


###Inicializar clases
nao = NAO(IP, PORT)
ia = IA()
recognizer = sr.Recognizer("es-CR") # Inicializa el reconocimiento de voz

recognizer.pause_threshold = 1 # Finaliza el SR al detectar silencio de 1s     

#Encender robot
nao.iniciar()

## Variable global
escuchaActiva = False # False si el robot solo espera ordenes de activacion, True si toma el SR para responder

"""
Flujo de ejecucion

En cada ejecucion del while, se escucha por medio del microfono el input del usuario, y se procesa con SR

Se inicia el robot en modo espera, escuchaActiva == False:
    Si se identifica una palabra clave de inicio se activa el robot

Si escuchaActiva == True:
    Modo conversacion:
        Si se identifica una palabra clave de despedida, se termina el programa

        Si no, se pasa el input al nao para que lo procese con el motor de IA, y diga la respuesta     
    
Fin de programa:
    Apaga Leds
    Se despide
    Regresa a posicion inicial 

"""


#Instrucción inicial
print("\nDecir HOLA o NAO para iniciar\n")

### Rutina Principal
while True:

    ## hacer algo con leds
    with sr.Microphone() as source:
        if escuchaActiva==True:
            try:
                nao.leds.setIntensity("AllLeds", 0)
                nao.leds.setIntensity("AllLedsBlue", 0.9)
            except:
                print('ErrorLeds')

        print("Escuchando...\n")

        try:
            ##animacion orejas
            audio = recognizer.listen(source,3)
        except OSError:
            print('\nError: Timeout Microfono\nEs posible que el MIC este desconectado, verificar\n')
            if escuchaActiva==True:
                try:
                    nao.leds.setIntensity("AllLeds", 0)
                    nao.leds.setIntensity("AllLedsRed", 0.9)
                except:
                    print('ErrorLeds')
            continue

        if escuchaActiva==True:
                try:
                    nao.leds.on('AllLeds')
                except:
                    print('ErrorLeds')
    

    try:
        # Utiliza el reconocimiento de voz para obtener el texto
        input_text = recognizer.recognize(audio)
        print("Usuario: " +  (input_text))
    
        # Verifica si el usuario saludo al nao en modo espera
        if  any([palabra in input_text.lower() for palabra in PALABRAS["saludo"]]) and escuchaActiva==False:
            escuchaActiva=True
            nao.saludo()
            print('te escucho')

        ##Si el usuario despide al nao en modo escucha activa, despedir al usuario y apagar        
        elif any([palabra in  (input_text.lower()) for palabra in PALABRAS["despedida"]]) and escuchaActiva==True:
            escuchaActiva=False
            nao.despedida()
            try:
                nao.leds.off('AllLeds')
            except Exception:
                print('Error al apagar leds')

            time.sleep(3)
            nao.posturas.goToPosture('StandInit',0.5)
            time.sleep(2)
            break

        # Si el usuario hizo una pregunta, procesa el texto y responde con IA
        elif escuchaActiva==True:
            print("\nRespuesta:")
            ##Ir a interfase con modelo gpt
            nao.responder(input_text,ia.respuesta)


    #Si hay un error, seguir escuchando
    except LookupError:
        ##Ignorar, seguir escuchando
        print("Voz no detectada\n")

print("PROGRAMA FINALIZADO")