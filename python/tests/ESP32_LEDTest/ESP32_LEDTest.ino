void setup() {
  // put your setup code here, to run once:
  //https://randomnerdtutorials.com/esp32-cam-ai-thinker-pinout/
  // https://i0.wp.com/randomnerdtutorials.com/wp-content/uploads/2020/03/ESP32-CAM-AI-Thinker-schematic-diagram.png?quality=100&strip=all&ssl=1
pinMode(4, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
//digitalWrite(4, HIGH);
delay(1000);
digitalWrite(4, LOW);
delay(1000);
}
