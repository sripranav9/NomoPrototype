#include <Servo.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_CAP1188.h>

// CAP1188 Pin Definitions
#define CAP1188_CS 10
#define CAP1188_MOSI 11
#define CAP1188_MISO 12
#define CAP1188_CLK 13
Adafruit_CAP1188 cap = Adafruit_CAP1188();

Servo bottomServo;
Servo upServo;

const int motorPin = 9;     // Motor control pin
const int ledPin = 2;       // LED pin (PWM-capable for brightness)
const int buzzer = 8;       // Buzzer connected to pin 8

void setup() {
  Serial.begin(115200);
  while (!Serial) {
   ; // Wait for serial port to connect
  }

  // Initialize the CAP1188 sensor
  Serial.println("CAP1188 test!");
  if (!cap.begin()) {
    Serial.println("CAP1188 not found");
    while (1);
  }
  Serial.println("CAP1188 found!");

  // Initialize servos
  bottomServo.attach(6);
  upServo.attach(3);

  // Initialize pins
  pinMode(motorPin, OUTPUT);
  digitalWrite(motorPin, LOW); // Ensure vibration motor is off
  pinMode(ledPin, OUTPUT);
  pinMode(buzzer, OUTPUT);

  // Set initial servo positions
  bottomServo.write(50);
  upServo.write(5);
}

void servoResting() {
  unsigned long currentMillis = millis();
  static unsigned long lastMoveTime = millis(); // Start timer
  int step = 0; // Initialize the step counter

  while (step < 2) { // Loop through all steps of the sequence
    currentMillis = millis();

    // Wait until 300ms has passed for each step
    if (currentMillis - lastMoveTime >= 300) {
      lastMoveTime = currentMillis; // Update the timer

      switch (step) {
        case 0:
          bottomServo.write(50);     // Move servo to position 35
          break;

        case 1:
          upServo.write(5);      // Move servo to position 65
          break;
      }
      step++; // Move to the next step
    }
  }
}

void lookUp() {
  unsigned long currentMillis = millis();
  static unsigned long lastMoveTime = millis(); // Start timer
  int step = 0; // Initialize the step counter

  while (step < 2) { // Loop through all steps of the sequence
    currentMillis = millis();

    // Wait until 300ms has passed for each step
    if (currentMillis - lastMoveTime >= 300) {
      lastMoveTime = currentMillis; // Update the timer

      switch (step) {
        case 0:
          bottomServo.write(50);     // Move servo to position 35
          break;

        case 1:
          upServo.write(10);      // Move servo to position 65
          break;
      }
      step++; // Move to the next step
    }
  }
}

void lookDown() {
  unsigned long currentMillis = millis();
  static unsigned long lastMoveTime = millis(); // Start timer
  int step = 0; // Initialize the step counter

  while (step < 2) { // Loop through all steps of the sequence
    currentMillis = millis();

    // Wait until 300ms has passed for each step
    if (currentMillis - lastMoveTime >= 300) {
      lastMoveTime = currentMillis; // Update the timer

      switch (step) {
        case 0:
          bottomServo.write(50);     // Move servo to position 35
          break;

        case 1:
          upServo.write(0);      // Move servo to position 65
          break;
      }
      step++; // Move to the next step
    }
  }
}

void faceWave() {
  unsigned long currentMillis = millis();
  static unsigned long lastMoveTime = millis(); // Start timer
  int step = 0; // Initialize the step counter

  while (step < 3) { // Loop through all steps of the sequence
    currentMillis = millis();

    // Wait until 300ms has passed for each step
    if (currentMillis - lastMoveTime >= 300) {
      lastMoveTime = currentMillis; // Update the timer

      switch (step) {
        case 0:
          digitalWrite(ledPin, HIGH); // Turn LED on
          bottomServo.write(35);      // Move servo to position 35
          break;

        case 1:
          bottomServo.write(65);      // Move servo to position 65
          break;

        case 2:
          digitalWrite(ledPin, LOW); // Turn LED off
          bottomServo.write(50);      // Move servo back to neutral
          break;
      }
      step++; // Move to the next step
    }
  }
}

void knod() {
  unsigned long currentMillis = millis();
  static unsigned long lastMoveTime = millis(); // Start timer
  int step = 0; // Initialize the step counter

  while (step < 2) { // Loop through all steps of the sequence
    currentMillis = millis();

    // Wait until 300ms has passed for each step
    if (currentMillis - lastMoveTime >= 300) {
      lastMoveTime = currentMillis; // Update the timer

      switch (step) {
      case 0: upServo.write(5); upServo.write(0); break;
      case 1: upServo.write(5); break;
    }
    step++;
    }
  }
}

void playTone() {
  unsigned long currentMillis = millis();
  static unsigned long lastMoveTime = millis(); // Start timer
  int step = 0; // Initialize the step counter

  while (step < 4) { // Loop through all steps of the sequence
    currentMillis = millis();

    // Wait until 300ms has passed for each step
    if (currentMillis - lastMoveTime >= 350) {
      lastMoveTime = currentMillis; // Update the timer

      switch (step) {
      case 0: 
        tone(buzzer, 1000); // Start the tone
        break;

      case 1: 
        noTone(buzzer); // Stop the tone
        break;

      case 2: 
        tone(buzzer, 1000); // Start the tone again
        break;

      case 3: 
        noTone(buzzer); // Final stop
        break;
      }
      step++;
    }
  }
}

void blinkLED(int totalBlinks, String speed) {
  unsigned long currentMillis = millis();
  unsigned long lastBlinkTime = millis(); // Initialize the timer
  bool ledState = LOW; // Start with LED off
  int blinkCount = 0; // Count the number of blinks
  int blinkSpeed = 350; // Default to fast speed

  // Adjust blink speed based on input
  if (speed == "slow") {
    blinkSpeed = 650;
  }

  // Loop through the total number of blinks
  while (blinkCount <= totalBlinks) {
    currentMillis = millis();

    // Toggle LED state every `blinkSpeed` milliseconds
    if (currentMillis - lastBlinkTime >= blinkSpeed) {
      lastBlinkTime = currentMillis; // Update the timer
      ledState = !ledState;          // Toggle the LED state
      digitalWrite(ledPin, ledState); // Write the LED state

      if (ledState == HIGH) { // Increment blink count only on LED ON
        blinkCount++;
      }
    }
  }

  // Ensure the LED is off at the end of the sequence
  digitalWrite(ledPin, LOW);
}


void loop() {
  int8_t touched = cap.touched();
  digitalWrite(motorPin, LOW); // Ensure motor is off by default

  // Check for individual touch events
  for (uint8_t i = 0; i < 8; i++) {
    if (touched & (1 << i)) {
      digitalWrite(motorPin, HIGH);  // Activate motor
      break;
    }
  }

  char newCase = '\0';
  if (Serial.available() > 0) {
    newCase = Serial.read(); // Read the case number
  }

  switch (newCase) {

    case '1': // No people detected
      playTone();
      blinkLED(2, "");
      break;

    case '2': // More than 3 people detected
      lookDown();
      break;

    case '3': // 1-2 people detected
      lookUp();
      blinkLED(1, "");
      break;

    case '4':
      faceWave();
      break;

    case '5': // Case 3 + thumb up -> case 3 + blink LED + nod
      lookUp();
      knod();
      blinkLED(1, "");
      break;

    case '6': // Case 3 + desk mode -> case 3 + slow LED blink
      lookUp();
      blinkLED(3, "slow"); //mention "slow" for the blinking to be slow
      break;

    case '7': // No people but gesture detected
      lookDown();
      break; 

    case '8':
      servoResting();
      break;

    default:
      // servoResting();
      break;
  }
}
