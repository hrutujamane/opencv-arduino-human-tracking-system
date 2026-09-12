#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo trackingServo;

const int trigPin = 2;
const int echoPin = 3;

const int buzzerPin = 8;
const int servoPin = 9;

const int redPin = 10;
const int greenPin = 11;
const int bluePin = 6;

long duration;
int distance;

char command = 'N';

int servoAngle = 90;

// For danger sweeping
int sweepAngle = 30;
int sweepDirection = 3;

unsigned long previousSweep = 0;

void setup() {

  Serial.begin(9600);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  pinMode(buzzerPin, OUTPUT);

  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  trackingServo.attach(servoPin);
  trackingServo.write(90);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("AI Robot Ready");

  delay(1500);
  lcd.clear();
}

void loop() {

  // Receive OpenCV command
  if (Serial.available() > 0) {
    command = Serial.read();
  }


  // -----------------------
  // ULTRASONIC
  // -----------------------

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH, 30000);

  if (duration == 0) {
    distance = 999;
  }
  else {
    distance = duration * 0.034 / 2;
  }


  // =====================================
  // DANGER CONDITION
  // =====================================

  if (distance <= 50 && command != 'N') {

    // RED
    setRGB(255, 0, 0);

    // BUZZER ON
    digitalWrite(buzzerPin, HIGH);

    // Servo moves LEFT ↔ RIGHT
    if (millis() - previousSweep >= 25) {

      previousSweep = millis();

      sweepAngle += sweepDirection;

      if (sweepAngle >= 150) {
        sweepAngle = 150;
        sweepDirection = -3;
      }

      if (sweepAngle <= 30) {
        sweepAngle = 30;
        sweepDirection = 3;
      }

      trackingServo.write(sweepAngle);
    }
  }


  // =====================================
  // NORMAL MODE
  // =====================================

  else {

    digitalWrite(buzzerPin, LOW);

    // Face tracking
    if (command == 'L') {

      servoAngle += 3;

      if (servoAngle > 170)
        servoAngle = 170;

      trackingServo.write(servoAngle);
    }

    else if (command == 'R') {

      servoAngle -= 3;

      if (servoAngle < 10)
        servoAngle = 10;

      trackingServo.write(servoAngle);
    }


    // LED based on distance

    if (command == 'N') {

      // No face
      setRGB(0, 0, 0);
    }

    else if (distance <= 100) {

      // Yellow
      setRGB(255, 100, 0);
    }

    else if (distance <= 150) {

      // Blue
      setRGB(0, 0, 255);
    }

    else {

      // Green
      setRGB(0, 255, 0);
    }
  }


  // -----------------------
  // LCD
  // -----------------------

  lcd.setCursor(0, 0);

  if (command == 'N') {
    lcd.print("NO FACE        ");
  }
  else {
    lcd.print("FACE DETECTED  ");
  }

  lcd.setCursor(0, 1);

  if (distance < 999) {

    lcd.print("DIST:");
    lcd.print(distance);
    lcd.print("cm     ");
  }

  else {

    lcd.print("DIST: ---      ");
  }
}


void setRGB(int red, int green, int blue) {

  analogWrite(redPin, red);
  analogWrite(greenPin, green);
  analogWrite(bluePin, blue);
}