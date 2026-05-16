#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

#define IR_PIN 4

float ax_off = 0, ay_off = 0, az_off = 0;
float fx = 0, fy = 0, fz = 0;

void calibrate() {
  const int N = 1000;
  for (int i = 0; i < N; i++) {
    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);

    ax_off += ax;
    ay_off += ay;
    az_off += az;
    delay(2);
  }

  ax_off /= N;
  ay_off /= N;
  az_off /= N;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(21, 22);
  mpu.initialize();
  calibrate();

  pinMode(IR_PIN, INPUT);
}

void loop() {
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);

  float x = (ax - ax_off) / 16384.0;
  float y = (ay - ay_off) / 16384.0;
  float z = (az - az_off) / 16384.0;

  // smoothing
  float alpha = 0.6;
  fx = alpha * fx + (1 - alpha) * x;
  fy = alpha * fy + (1 - alpha) * y;
  fz = alpha * fz + (1 - alpha) * z;

  // noise filter
  float THRESH = 0.01;
  if (abs(fx) < THRESH) fx = 0;
  if (abs(fy) < THRESH) fy = 0;
  if (abs(fz) < THRESH) fz = 0;

  //IR STABILITY FILTER (KEY FIX)
  static int stableIR = 1;
  static int lastRead = 1;
  static unsigned long lastChange = 0;

  int current = digitalRead(IR_PIN);

  if (current != lastRead) {
    lastChange = millis();
  }

  if (millis() - lastChange > 50) {
    stableIR = current;
  }

  lastRead = current;

  int ir = stableIR;

  // output
  Serial.print(fx, 2);
  Serial.print(",");
  Serial.print(fy, 2);
  Serial.print(",");
  Serial.print(fz, 2);
  Serial.print(",");
  Serial.println(ir);

  delay(30);
}
