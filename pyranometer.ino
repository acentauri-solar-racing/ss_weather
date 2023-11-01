#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads1115;

float S = 10.19; // from device in uV/(W/m^2)
int wait_time = 10; // in seconds

void setup(void) {
    Serial.begin(19200);
    Serial.println("--- Starting Program ---");
    ads1115.begin(0x48);  // Initialize ads1115
}

void loop(void) {
    float adc0;
    adc0 = ads1115.readADC_SingleEnded(0);
    float E = adc0 / S * 1000;
    Serial.print("E in W/m^2: "); Serial.println(E);  // Print the value of E
    delay(wait_time*1000);
}
