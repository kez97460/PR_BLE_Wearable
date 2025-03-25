#include "BMA400_DataConverter.h"

int12_t convertTo12Bit(int16_t raw_data)
{
    int12_t signed_data = raw_data << 4;
    return (signed_data / 16);
}