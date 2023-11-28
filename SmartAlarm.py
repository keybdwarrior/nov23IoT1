import serial
import time
import datetime
import smtplib
import speech_recognition as sr

# 이메일 설정
sender_email = "@gmail.com"
receiver_email = "receiver_email@gmail.com"
password = "your_email_password"

# 아두이노 시리얼 포트 설정
arduino_port = "/dev/ttyUSB0"  # 수정해야함
baud_rate = 9600

# 아두이노와 시리얼통신 설정
ser = serial.Serial(arduino_port, baud_rate, timeout=1)

# 아두이노에 명령 전송 기능
def send_command(command):
    ser.write(command.encode())

# 이메일 전송 기능
def send_email(subject, body):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(sender_email, receiver_email, message)

# 음성인식 기능
def recognize_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("마이크에서 명령을 기다리고 있습니다...")
        audio = recognizer.listen(source)

        try:
            print("명령을 인식 중입니다...")
            command = recognizer.recognize_google(audio, language='ko-KR')
            print(f"인식된 명령: {command}")
            return command
        except sr.UnknownValueError:
            print("음성을 인식할 수 없습니다. 다시 시도해주세요.")
            return ""
        except sr.RequestError as e:
            print(f"음성 인식 서비스에 오류가 있습니다: {e}")
            return ""

# 메인 루프
while True:
    # 아두이노로부터 데이터 읽어오기
    arduino_data = ser.readline().decode('utf-8').strip()

    if arduino_data.startswith("BUTTON1=CLICK"):
        # 버튼 1 클릭
        print("Button 1 clicked")

    elif arduino_data.startswith("BUTTON2=CLICK"):
        # 버튼 2 클릭
        print("Button 2 clicked")

    elif arduino_data.startswith("LIGHT_LEVEL="):
        # 아두이노로부터 밝기 읽어오기
        light_level = int(arduino_data.split("=")[1])
        if light_level > 700:  # Adjust this threshold based on your environment
            # 점진적으로 LED 발광
            for i in range(256):
                send_command(f"RGB={i},{i},{i}\n")
                time.sleep(0.01)

    elif arduino_data.startswith("ALARM_SET="):
        # 아두이노로부터 알람 설정 시간 읽어오기
        alarm_set_time = datetime.datetime.strptime(arduino_data.split("=")[1], "%H:%M:%S")
        print(f"Alarm set for {alarm_set_time}")

    elif arduino_data.startswith("ALARM_TRIGGER"):
        # 알람이 트리거되면 액션을 실행
        send_command("FND=12.34\n")  # Replace with actual time
        for _ in range(5):
            send_command("BUZZER=1000\n")
            time.sleep(1)

    elif arduino_data.startswith("VOICE_COMMAND"):
        # 음성 명령에 따른 작업 수행
        voice_command = recognize_voice()
        if "알람 꺼줘" in voice_command:
            send_command("BUZZER=0\n")
        elif "불 꺼줘" in voice_command:
            send_command("RGB=0,0,0\n")
        elif "날씨 알려줘" in voice_command:
            # 낭씨 정보 받아와 이메일로 전송
            ### 구현해야함 ###
            weather_info = "Sunny"
            send_email("Today's Weather", weather_info)
            print("날씨 정보를 이메일로 전송했습니다.")     #############
    
    time.sleep(1)  # 안정성을 도모하기 위한 지연
