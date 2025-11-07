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
import speech_recognition as sr         # Reconocimiento de voz
import openai                           # API de OpenAI conexion con GPT
from naoqi import ALProxy, ALModule     # Clases de Naoqi v2.1.4.13

# Librerías auxiliares
import copy
import sys
import time
import tempfile

"""
Declaracion de constantes
    Parametros de conexion: IP y PORT
    Palabras claves
"""
# Parametros de conexión 
IP = "127.0.0.1"   # IP del robot
PORT = 58739       # Puerto del robot

#Palabras clave
PALABRAS_INICIO = "hola;okay;nao;"
PALABRAS_FIN = "adios;chao;apagar;"

# Definición de clases

"""
Clase NAO
    Encargada de representar al robot
    Ejecuta movimientos, acciones fisicas y enlaza con la memoria del robot
"""
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
    adp : object
        API AudioDevice
        Permite acceder a los dispositivos de audio, en este caso los micrófonos
    memory : object
        API 'ALMemory'
        Memoria del robot
    headTouched : bool
        Almacena el estado de los sensores de cabeza, si han sido tocados o no
    handTouched : bool
        Almacena el estado de los sensores de las manos, si han sido tocados o no
    audioFile : path str
        Localizacion del archivo de audio en la memoria temporal
    

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
    updateHandTouch()
        Verifica en la memoria si el usuario tocó alguno de los sensores de las manos del robot
    updateHeadTouch()
        Verifica en la memoria si el usuario tocó alguno de los sensores de la cabeza del robot
    startRecord()
        Iniciar grabación con el micrófono del nao
    stopRecord()
        Finalizar grabación
    speechStopped()
        Verifica en la memoria si el estado del speech recognition indica que el usuario dijo una frase y terminó de hablar
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
        self.adp = ALProxy("ALAudioDevice", ip_nao, port_nao)
        self.memory = ALProxy("ALMemory", ip_nao, port_nao)
        self.headTouched = False
        self.handTouched = False
        self.audioFile = tempfile.mkdtemp() + "\\rec.wav"

    def iniciar(self):
        self.tts.setLanguage("Spanish")
        self.posturas.goToPosture("StandInit",0.5)
        time.sleep(1)
        self.posturas.goToPosture("Crouch",0.5)
        time.sleep(1)
        ##implementar sonido beep

    def saludo(self):
        try:
            nao.leds.on("AllLeds")
        except:
            print('Error de leds')
        nao.posturas.goToPosture("StandInit",0.5)
        time.sleep(1)
        self.alp.setState("solitary")
        time.sleep(0.5)
        self.asp.say(" ^start(animations/Stand/Gestures/Hey_6) Hola, ^wait(animations/Stand/Gestures/Hey_6)"
                     " ^start(animations/Stand/Gestures/Me_1) soy NAO, tu asistente, preguntame lo que quieras"
                     " y te ayudaré ^wait(animations/Stand/Gestures/Me_1) ")
        print("Hola, soy NAO, tu asistente, preguntame lo que quieras y te ayudare")
        time.sleep(1)

    def despedida(self):
        self.asp.say(" ^start(animations/Stand/Gestures/Hey_1) Adiós. Si quieres llamarme di: Hola Nao y te ayudaré."
                     " ^wait(animations/Stand/Gestures/Hey_1)")
        print("Adios. Si quieres llamarme di HOLA NAO y te ayudare.")
        time.sleep(0.5)
        self.posturas.goToPosture("Crouch",0.5)
        time.sleep(1)

    def responder(self, texto, generador=None):
        self.leds.rasta(1.5)
        if generador==None or texto=="":
            self.tts.say("Creo que no tengo respuesta para eso")
            print ("El generador no funciona. Texto Original:\n" + texto + '.')
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
        time.sleep(1)

    def updateHandTouch(self):
        self.handTouched = (self.memory.getData("HandRightBackTouched") 
                            or self.memory.getData("HandRightLeftTouched") 
                            or self.memory.getData("HandRightRightTouched")
                            or self.memory.getData("HandLeftBackTouched") 
                            or self.memory.getData("HandLeftLeftTouched")
                            or self.memory.getData("HandLeftRightTouched"))
        return self.handTouched
        
    def updateHeadTouch(self):
        self.headTouched = (self.memory.getData("FrontTactilTouched") 
                            or self.memory.getData("MiddleTactilTouched") 
                            or self.memory.getData("RearTactilTouched"))
        return self.headTouched
    
    def startRecord(self, file):
        self.adp.startMicrophonesRecording(self.audioFile)

    def stopRecord(self):
        self.adp.stopMicrophonesRecording()

    def speechStopped(self):
        try:
            return (self.memory.getData("ALSpeechRecognition/Status") == "EndOfProcess" 
                    or self.memory.getData("ALSpeechRecognition/Status") == "Stop")
        except Exception:
            return False

"""
Clase IA
    Encargada de representar y conectar con la IA, el api de OPENAI
    Guarda los parámetros de conexión y contexto para enlazar a la IA
    Genera respuestas a partir del texto del usuario y la historia reciente de la conversacion
"""
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
    conversacion : list
        Lista de dialogos entre la IA y el robot
    

    Metodos
    -------
    respuesta(pregunta)
        Genera una respuesta con un motor de IA a partir del input de pregunta del usuario y la conversacion anterior reciente:
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
                        " Si alguien pregunta donde estás, di que en el Robotifest 2023 de la Universidad de Costa Rica, "
                        " en el Museo de San Ramón."
                        " Responde utilizando lenguaje sencillo y cordial, como en una conversación, de forma amigable."
                        " A continuación la conversación: ")
        self.MT = 85
        self.conversacion = []
        ##Declaracion del api key
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
Clase SpeechTestClass que hereda de ALModule.
    Representa al reconocimiento de voz, con sus módulos y funciones
"""
class SpeechTestClass(ALModule):
    """
Definicion de constantes de clase
Estas variables controlan aspectos como las palabras clave, la expresión visual y auditiva y el umbral de confianza para la detección de palabras.
"""
    VISUAL_EXPRESSION = True
    AUDIO_EXPRESSION = True
    ENABLE_WORD_SPOTTING = True
    CONFIDENCE_THRESHOLD = 25
    
    lastWords = None
    """
Se inicializa el módulo de reconocimiento de voz (self.asr) y configura el idioma en espanol.
Se enlaza con un objeto para acceder a la memoria del robot (self.memory).
...
    Atributos 
    ----------
    asr : str
        IP del robot, en formato string
    memory : obj
        nao.memory, memoria del nao
    word_list : str 
        Nombre de la instancia de clase
    

    Metodos
    -------
    Consultar documentacion de ALSpeechRecognition  
"""
    def __init__(self, IP, PORT, name, memory, word_list):
        """
        Parametros
        ----------
        IP : str
            IP del robot, en formato string
        PORT : int
            Numero de puerto del robot
        name : str 
            Nombre de la instancia de clase
        memory : NAO.memory
            Memoria del robot nao, instancia de ALProxy('ALMemory')
        word_list : lista
            Lista de palabras que se utilizarán para el Speech recognition
            
        """

        ALModule.__init__(self, name)
        try:
            self.asr = ALProxy("ALSpeechRecognition", IP, PORT)
            self.asr.setLanguage("Spanish")
        except Exception as e:
            self.asr = None
            self.logger.error(e)
        self.memory = memory
        self.word_list = word_list
    
    def onLoad(self):
        from threading import Lock
        self.bIsRunning = False
        self.mutex = Lock()
        self.hasPushed = False
        self.hasSubscribed = False
        self.BIND_PYTHON(self.getName(), "onWordRecognized")
        
        self.isWordSaid = False

    def onUnload(self):
        from threading import Lock
        self.mutex.acquire()
        try:
            if (self.bIsRunning):
                if (self.hasSubscribed):
                    self.memory.unsubscribeToEvent("WordRecognized", self.getName())
                if (self.hasPushed and self.asr):
                    self.asr.pause(True)
                    self.asr.popContexts()
        except RuntimeError as e:
            self.mutex.release()
            raise e
        self.bIsRunning = False
        self.mutex.release()

    def onInput_onStart(self):
        from threading import Lock
        self.mutex.acquire()
        
        self.asr.pause(True)
        if self.bIsRunning:
            self.mutex.release()
            return
        self.bIsRunning = True
        try:
            if self.asr:
                self.asr.setVisualExpression(self.VISUAL_EXPRESSION)
                self.asr.setAudioExpression(self.AUDIO_EXPRESSION)
                self.asr.pushContexts()
            self.hasPushed = True
            if self.asr:
                self.asr.setVocabulary(self.word_list.split(';'), self.ENABLE_WORD_SPOTTING)
            self.memory.subscribeToEvent("WordRecognized", self.getName(), "onWordRecognized")
            self.hasSubscribed = True
        except RuntimeError as e:
            self.mutex.release()
            self.onUnload()
            raise e
        self.mutex.release()
        self.asr.pause(False)

    def onInput_onStop(self):
        if self.bIsRunning:
            self.onUnload()

    def onWordRecognized(self, key, value, message):
        if len(value) > 1 and value[1] >= self.CONFIDENCE_THRESHOLD / 100.:
            self.wordRecognized(value[0])
            self.lastWords = copy.copy(value)
        else:
            self.onNothing()

    def onNothing(self):
        print("No se reconoce palabra clave")
        
    def wordRecognized(self, wordRecognized):
        self.isWordSaid = True
        print(wordRecognized)
        
    def getWords(self):
        return self.lastWords
        
    def isSearchedWordSaid(self):
        return self.isWordSaid
    

"""
Codigo principal
MAIN

Se inicializan las clases: NAO, IA, sr.Recognizer y SpeechTestClass
Se configuran modificadores, variables y se enciende el robot

"""

###Inicializar clases
nao = NAO(IP, PORT)
ia = IA()
recognizer = sr.Recognizer("es-CR") # Inicializa el reconocimiento de voz

##Clases SR

SpeechTestClass = SpeechTestClass(IP, PORT, 'SpeechTestClass', nao.memory, PALABRAS_INICIO) ## SR inicial
SpeechRecClass = SpeechTestClass(IP, PORT, 'SpeechRecClass', nao.memory, PALABRAS_FIN)      ## SR grabacion

#Configurar modificador de SR para mejorar tiempos
recognizer.pause_threshold = 1.5 # Finaliza el SR al detectar silencio de 1s     

## Variable global
escuchaActiva = False # False si el robot solo espera ordenes de activacion, True si toma el SR para responder

#Encender robot
nao.iniciar()


"""
Flujo de ejecucion

Se inicia el robot en modo espera:
    Se inicia el SR inicial
    Si se identifica una palabra clave de inicio o se toca cabeza o una de las manos, se activa el robot

Si escuchaActiva == True:
    Modo conversacion
    Se inicia el SR de grabacion
    Inicio de grabacion
    Si se toca una mano o se dice una palabra clave de despedida el robot se apaga
    Al detectar que se dijo una frase desconocida o se toca la cabeza detiene la grabacion
    Procesa la grabacion por medio de libreria SR
    Pasa el texto a la IA
    Vuelve al inicio del bucle

Fin de programa:
    Apaga Leds
    Se despide
    Regresa a posicion inicial 



"""

#Instrucción inicial
print("decir HOLA/NAO para iniciar, o tocar")

##Ciclo de ejecucion
while True:
    
    ##Si el nao está en modo espera se ejecuta 
    if escuchaActiva == False:
        
        #Se ejecuta el SR del nao para el modo espera
        SpeechTestClass.onLoad()
        SpeechTestClass.onInput_onStart()

        ##Escuchar si el usuario dice Hola Nao, o toca brazo o cabeza     
        while not SpeechTestClass.isSearchedWordSaid() or nao.updateHeadTouch() or nao.updateHandTouch():
            time.sleep(0.25)
        
        # Se actualiza la variable de escucha activa
        escuchaActiva = True
        # Se inicia el modo interactivo de nao
        nao.saludo()
        ##Cambiar por una animación en Leds de orejas
        nao.leds.on("EarLeds")
        pass

    
    elif escuchaActiva == True:
        # Se inicia el SR de nao, para el modo activo
        SpeechRecClass.onLoad()
        SpeechRecClass.onInput_onStart()

        # Instrucciones a la terminal
        print('Escuchando, tocar la cabeza para finalizar escucha')
        print('Tocar una mano o decir adios para finalizar rutina')

        #Se inicia la grabacion con el micrófono del nao
        nao.startRecord()

        # Se continúa la grabación hasta que se diga la palabra clave, el usuario termine de hablar, se toque la cabeza o mano
        while not (SpeechRecClass.isSearchedWordSaid() 
                   or nao.speechStopped()  ###
                   or nao.updateHeadTouch() 
                   or nao.updateHandTouch()):
            time.sleep(0.25)

        # Se detiene la grabación
        nao.stopRecord()

        # Notifica por terminal el fin de la grabación y speech recognition
        print("Fin escucha")

        ## Si se dijo adios o se toca la mano, despedirse y terminar
        if SpeechRecClass.isWordSaid or nao.handTouched:
            escuchaActiva = False
            nao.despedida()
            break

        ## Si es el caso, se procesa el audio grabado 
        else:
            # Se pasa el archivo de audio al speech recognition
            with sr.WavFile(nao.audioFile) as source:
                try:
                    audio = recognizer.record(source)
                except Exception:
                    print('No fue posible procesar el audio')

                # Se procesa el audio por medio del SR de python y el robot dice la respuesta
                try:               
                    input_text = recognizer.recognize(audio)
                    print("Usuario: " + input_text)
                    print("Respuesta: ")
                    nao.responder(input_text,ia.respuesta)
                
                # Manejo de errores
                except LookupError:
                    print("No fue posible transcribir el audio")

                except Exception:
                    print("Error")

# Fin del programa
try:
    nao.leds.off('AllLeds')
except Exception:
    print('Error al apagar leds')
time.sleep(2)

# Colocar robot en postura inicial
nao.posturas.goToPosture('StandInit',0.5)
time.sleep(1)
print("PROGRAMA FINALIZADO")