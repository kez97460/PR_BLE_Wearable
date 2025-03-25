#include "IN100_I2C.h"

IN100_I2C::IN100_I2C(TwoWire *i2c)
{
    _i2c = i2c;
}

void IN100_I2C::begin(uint8_t slave_address, bool serial_debug, uint32_t frequency)
{
    _slave_address = slave_address;

    _i2c->begin();
    _i2c->setClock(frequency);

    setDebugMode(serial_debug);

    if (_serial_debug)
    {
        Serial.printf("[IN100] Initialzed I2C, slave at address [%d]\n", slave_address);
    }
}

uint8_t *IN100_I2C::i2c_read(uint32_t r_len)
{
    uint8_t *buffer = new uint8_t[r_len];

    _i2c->requestFrom(_slave_address, r_len);

    _i2c->readBytes(buffer, r_len);

    if (_serial_debug)
    {
        String str = "";
        for (size_t i = 0; i < r_len; i++)
        {
            str += buffer[i];
            if (i < r_len - 1)
                str += ", ";
        }

        Serial.printf("[IN100] Read %d bytes from slave, data : [%s]\n", r_len, str);
    }

    return buffer;
}

void IN100_I2C::i2c_write(uint8_t *w_data, uint32_t w_len)
{
    _i2c->beginTransmission(_slave_address);
    _i2c->write(w_data, w_len);
    _i2c->endTransmission();

    if (_serial_debug)
    {
        String str = "";
        for (size_t i = 0; i < w_len; i++)
        {
            str += w_data[i];
            if (i < w_len - 1)
                str += ", ";
        }

        Serial.printf("[IN100] Wrote %d bytes to slave, data : [%s]\n", w_len, str);
    }
}

void IN100_I2C::i2c_write(uint8_t w_data)
{
    _i2c->beginTransmission(_slave_address);
    _i2c->write(w_data);
    _i2c->endTransmission();

    if (_serial_debug)
    {
        Serial.printf("[IN100] Wrote 1 byte to slave, data : [%s]\n", w_data);
    }
}

uint8_t *IN100_I2C::i2c_write_stop_read(uint8_t *w_data, uint32_t w_len, uint32_t r_len)
{
    i2c_write(w_data, w_len);
    return i2c_read(r_len);
}

uint8_t *IN100_I2C::i2c_write_stop_read(uint8_t w_data, uint32_t r_len)
{
    i2c_write(w_data);
    return i2c_read(r_len);
}

void IN100_I2C::delay_command(uint32_t time_us)
{
    if (_serial_debug)
    {
        Serial.printf("[IN100] Delaying program for %d us\n", time_us);
    }
    delayMicroseconds(time_us);
}

void IN100_I2C::setDebugMode(bool mode)
{
    _serial_debug = mode;
    if (mode)
    {
        Serial.println("Debug prints ON");
    } else
    {
        Serial.println("Debug prints OFF");
    }
}