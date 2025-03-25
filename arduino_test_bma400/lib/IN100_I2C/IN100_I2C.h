#ifndef IN100_I2C_H
#define IN100_I2C_H

#include <Arduino.h>
#include <Wire.h>

class IN100_I2C
{
private:
    TwoWire *_i2c;
    uint8_t _slave_address;
    bool _serial_debug = false;
public:
    IN100_I2C(TwoWire *i2c = &Wire);

    void begin(uint8_t slave_address, bool serial_debug = true, uint32_t frequency = 100000);

    uint8_t *i2c_read(uint32_t r_len);

    void i2c_write(uint8_t *w_data, uint32_t w_len);
    void i2c_write(uint8_t w_data);

    uint8_t *i2c_write_stop_read(uint8_t *w_data, uint32_t w_len, uint32_t r_len);
    uint8_t *i2c_write_stop_read(uint8_t w_data, uint32_t r_len);

    void delay_command(uint32_t time_us);

    void setDebugMode(bool mode);
};

#endif /* IN100_I2C_H */
