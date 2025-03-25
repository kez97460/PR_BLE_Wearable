#ifndef BMA400_DATACONVERTER_H
#define BMA400_DATACONVERTER_H

#include <stdint.h>

typedef int16_t int12_t; // Because acceleration data is 12 bits...

int12_t convertTo12Bit(int16_t raw_data);

#endif /* BMA400_DATACONVERTER_H */
