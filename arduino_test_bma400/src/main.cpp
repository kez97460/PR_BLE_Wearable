#include <Arduino.h>
#include <Wire.h>

#include "IN100_I2C.h"
#include "SparkFun_BMA400_Arduino_Library.h"
#include "BMA400_DataConverter.h"

TwoWire i2c((uint32_t) D4, (uint32_t) D5);
IN100_I2C in100(&i2c);

void setup()
{
    Serial.begin(115200);
    while (!Serial)
    {
        delay(50);
    }

    // i2c.begin();

    // while(accelerometer.beginI2C(BMA400_I2C_ADDRESS_DEFAULT, i2c) != BMA400_OK)
    // {
    //     // Not connected, inform user
    //     Serial.println("Error: BMA400 not connected, check wiring and I2C address!");

    //     // Wait a bit to see if connection is established
    //     delay(1000);
    // }
    // Serial.println("BMA400 connected!");

    in100.begin(0x14, false);
}

void loop()
{
    // Get measurements from the sensor. This must be called before accessing
    // the acceleration data, otherwise it will never update
    // accelerometer.getSensorData();

    // // Print acceleration data
    // Serial.print("Acceleration in g's");
    // Serial.print("\t");
    // Serial.print("X: ");
    // Serial.print(accelerometer.data.accelX, 3);
    // Serial.print("\t");
    // Serial.print("Y: ");
    // Serial.print(accelerometer.data.accelY, 3);
    // Serial.print("\t");
    // Serial.print("Z: ");
    // Serial.println(accelerometer.data.accelZ, 3);

    // delay(50);

    in100.i2c_write(0x19);
    in100.i2c_write(0x2);
    in100.delay_command(1000);
    uint8_t *x_data = in100.i2c_write_stop_read(0x4, 2);
    uint8_t *y_data = in100.i2c_write_stop_read(0x6, 2);
    uint8_t *z_data = in100.i2c_write_stop_read(0x8, 2);

    int12_t x_val = convertTo12Bit(x_data[1] * 256 + x_data[0]);
    int12_t y_val = convertTo12Bit(y_data[1] * 256 + y_data[0]);
    int12_t z_val = convertTo12Bit(z_data[1] * 256 + z_data[0]);

    Serial.printf("x_val : [%d], y_val : [%d], z_val : [%d]\n", x_val, y_val, z_val);

    delay(1000);
} 