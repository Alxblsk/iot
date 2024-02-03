## The following resources were used while connecting the moisture sensor 
# https://www.youtube.com/watch?v=9lelfdwoKKA
# https://peppe8o.com/capacitive-soil-moisture-sensor-with-raspberry-pi-pico-wiring-code-and-calibrating-with-micropython/

## These resources were used to get some knowledge about how to work with the isplay
# https://www.youtube.com/watch?v=YSqGV6NGWYM
# https://github.com/stlehmann/micropython-ssd1306/blob/master/ssd1306.py

from machine import ADC, Pin, I2C
from ssd1306 import SSD1306_I2C
import utime

# The allowed range of the sensor after calibration. By default, the range is between 0 and 65535.
# However, for more precise values, it's better to put the sensor in dry soil (MIN) and water (MAX) to understang the working range.
min_moisture = 18500
max_moisture = 43000

# The frequency of value reading.
# The value won't change much, but sensor is nor thatpresice, so it makes sense more often to get an average of multiple values.
read_delay = 1     # seconds

# GPIO Pins Used to read sensor values
soil_pin = Pin(26) # User selected pin for moisture sensor
air_pin = 4        # Embedded Pico pin that measures temperature

screen_data_pin = Pin(20)  # User selected pin for transforming data from Pico to screen
screen_clock_pin = Pin(21) # User selected pin from getting clock value

# Screen dimentions
screen_w = 128
screen_h = 32
screen_freq = 200000

# Letter size
letter_w = 8
letter_h = 8

# Position of each line
value1_x_offset = 78
value2_x_offset = 100
value1_y_offset = 4
value2_y_offset = 18
line_x_offset = 5

# Text for each line
line1_text = "MOISTURE:"
line2_text = "TEMPERATURE:"
    
def measure_and_display():
    # Conversion of analog signals to digital signals
    soil = ADC(soil_pin)
    air = ADC(air_pin)
    
    # display initialization
    display = init_display_state(line1_text, line2_text)
    
    while True:
        # Perform measurements
        moisture = read_moisture(soil)
        tC, tF = read_temperature(air)

        # Display measurements
        display_message(display, value1_x_offset, value1_y_offset, "%.1f" % moisture + "%")
        display_message(display, value2_x_offset, value2_y_offset,  "%.0f" % tF + "F")
        
        # Pause before the next iteration
        utime.sleep(read_delay)

def read_moisture(soil):
    # Read digital value of analog signal from moisture sensor (range 0-65535) 
    raw_m_value = soil.read_u16()
    
    # Main formula for moisture calculation
    moisture = (max_moisture - raw_m_value) * 100 / (max_moisture - min_moisture)
    
    # We're working with percentage, it should be exactly in between 0 an 100
    moisture = moisture if moisture < 100 else 100
    moisture = moisture if moisture > 0 else 0
    
    # Debug value
    print("Moisture: %.2f" % moisture + "% (ADC value: " + str(raw_m_value) + ")")
    
    # Calculated percentage
    return moisture
    
def read_temperature(air):
    pico_voltage = 3.3
    max_sensor_value = 65535
    
    # Read digital value of analog signal from temperature sensor (range 0-65535)
    raw_t_value = air.read_u16();
    
    # Common formula of measuring temperature
    t_volt = (pico_voltage / max_sensor_value) * raw_t_value
    
    # Calculating temperature in Celcius and Fahrenheit
    temperatureC = 27 - (t_volt - 0.706)/0.001721
    temperatureF = temperatureC * 9 / 5 + 32
    
    # Debug value
    print("Temperature: %2.f" % temperatureC + "C, %2.f" % temperatureF + "F")
    
    # A tuple with calculated values
    return temperatureC, temperatureF


def init_display_state(line1_message, line2_message):
    # Initialize I2C interface
    i2c = I2C(0, scl=screen_clock_pin, sda=screen_data_pin, freq=screen_freq)
    addr = i2c.scan()[0]
    
    # Get context from drivers
    oled = SSD1306_I2C(screen_w, screen_h, i2c, addr)
    
    # Clear the display
    oled.fill(0)
    
    # Pre-populate static text
    oled.text(line1_message, line_x_offset, value1_y_offset)
    oled.text(line2_message, line_x_offset, value2_y_offset)
    # Return context
    return oled

def display_message(oled, x_offset, y_offset, value_to_display):
    # Clear the part of display that will contain value
    oled.fill_rect(x_offset, y_offset, screen_w, letter_h, 0)
    
    # Render value
    oled.text(value_to_display, x_offset, y_offset)
    
    # Refresh screen
    oled.show()
        
# Start program
measure_and_display()
