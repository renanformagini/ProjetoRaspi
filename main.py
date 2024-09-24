import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import csv
from datetime import datetime

rfid_reader = SimpleMFRC522()
usuarios = {761383686137: "Maria", 701577035323: "Pedro"}
usuarios_autorizados = {761383686137: "Maria", 701577035323: "Pedro"}
acesso_diario = {}
tempo_entrada = {}

led_verde = 5
led_vermelho = 3
buzzer = 37
dentro = False
tentativas_invasao = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_verde, GPIO.OUT)
GPIO.setup(led_vermelho, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)

def verificar_tag_rfid(tag):
    global dentro, tentativas_invasao
    if tag in usuarios_autorizados:
        if tag not in acesso_diario:
            print(f"Bem-vindo, {usuarios_autorizados[tag]}!")
            acesso_diario[tag] = usuarios_autorizados  
            dentro = True
            controlar_leds("verde", invasao=False)
            registrar_acesso(tag, {usuarios[tag]}, "Autorizado", "Entrada", None)
            tempo_entrada[tag] = datetime.now()
            print(tempo_entrada)
        elif dentro:
            print(f"Até logo, {usuarios_autorizados[tag]}!")
            duracao_entrada = datetime.now() - tempo_entrada[tag]
            dentro = False
            print(duracao_entrada)
            registrar_acesso(tag, {usuarios[tag]}, "Autorizado", "Saída", duracao_entrada)
        else:
            print(f"Bem-vindo de volta, {usuarios_autorizados[tag]}!")
            controlar_leds("verde", invasao=False)
            registrar_acesso(tag, {usuarios[tag]}, "Autorizado", "Entrada", None)
    elif tag in usuarios:
        print(f"Acesso negado, {usuarios[tag]}.")
        controlar_leds("vermelho", invasao=False)
        registrar_acesso(tag, {usuarios[tag]}, "Não autorizado", None, None)
    else:
        print("Tag desconhecida!")
        tentativas_invasao += 1
        controlar_leds("vermelho", invasao=True)
        registrar_acesso(tag, f"Tentativas de invasão: {tentativas_invasao}", None, None, None)

def controlar_leds(cor_led, invasao):
    if cor_led == "verde":
        GPIO.output(buzzer, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(buzzer, GPIO.LOW)
        for _ in range(5):
            GPIO.output(led_verde, GPIO.HIGH)
            GPIO.output(buzzer, GPIO.HIGH)
            print("LED verde ligado")
            time.sleep(1)
            GPIO.output(led_verde, GPIO.LOW)
            GPIO.output(buzzer, GPIO.LOW)
            print("LED verde desligado")
            time.sleep(1)
    elif cor_led == "vermelho" and not invasao:
        for _ in range(5):
            GPIO.output(led_vermelho, GPIO.HIGH)
            GPIO.output(buzzer, GPIO.HIGH)
            print("LED vermelho ligado")
            time.sleep(1)
            GPIO.output(led_vermelho, GPIO.LOW)
            GPIO.output(buzzer, GPIO.LOW)
            print("LED vermelho desligado")
            time.sleep(1)
    elif cor_led == "vermelho" and invasao:
        for _ in range(2):
            GPIO.output(led_vermelho, GPIO.HIGH)
            GPIO.output(buzzer, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(led_vermelho, GPIO.LOW)
            time.sleep(1)
    GPIO.output(buzzer, GPIO.LOW)

def registrar_acesso(id_log, usuario, status_autorizacao, tipo_acao, duracao):
    with open('logs_acesso.csv', mode='a', newline='') as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        escritor_csv.writerow([timestamp, id_log, usuario, status_autorizacao, tipo_acao, duracao])

try:
    while True:
        GPIO.output(led_verde, GPIO.LOW)
        GPIO.output(led_vermelho, GPIO.LOW)
        print(f"Tentativas de invasão: {tentativas_invasao}")
        print("Aguardando leitura da tag RFID...")

        tag_id, tag_text = rfid_reader.read() 
        print(f"ID da tag: {tag_id}")
        verificar_tag_rfid(tag_id)  
except KeyboardInterrupt:
    print("Programa interrompido pelo usuário.")

finally:
    GPIO.cleanup()  
    print("Programa finalizado.")
