PyTechBrain - innowacyjna nauka programowania

Chciałbym przedstawić inspirację dla nauczycieli, w pełni zgodną z nową podstawą programową. To innowacyjny projekt - wprowadzający do tematu IoT. 
Łączy elektronikę i programowanie w jednym pudełku, pozwala uczyć od klasy 4 szkoły podstawowej do końca liceum. 
Zaczynamy środowiskiem opartym o Scratch, po czym przechodzimy do Pythona. Wszystko z czujnikami i diodami w tle...

PyTechBrain to nowa platforma wprowadzająca uczniów w dziedzinę IoT - Internet of Things (Internet Rzeczy). 
Pozwala na nauczanie elektroniki i programowania w jednym. Jest w pełni zgodna z nową Podstawą Programową. 
Łaczy prostotę wykonania i olbrzymie mozliwości nauczania programowania. Możemy wykorzystywać ją do budowania stacji pogodowych, podstaw inteligentnego miasta.  Kompatybilny z Arduino UNO R3, obsługiwany przez Scratch 2.0 offline i Python 3

==============================================


Dla układów PyTechBrain z firmy ABIX Edukacja biblioteka samodzielnie znajduje port COM (ttyUSB) - nie ma potrzeby niczego sprawdzać.

Dla innych układów kompatybilnych z Arduino UNO R3 należy samodzielnie sprawdzić port COM (ttyUSB) i podac jako parametr, np.:



Aby zainicjować układ w programie, konieczne są polecenia:



```python

```python
print("This is sample of using PyTechBrain module.")
print("===========================================")

# creating board object with default debugging with no output
test_board = PyTechBrain()

# the same, but with full debugging during using module
# test_board = PyTechBrain(debug=True)

# Initializing board - first thing we need to do:
# automatic
# if test_board.board_init():
#     print("Super!")
# else:
#     print("Something went wrong... check output.")
#
# or manual
# if test_board.board_init("COM3"):
#     print("Super!")
# else:
#     print("Something went wrong... check output.")

# manual
if test_board.board_init():
    print("Super!")
    test_board.set_buzzer("beep")  # demo, on, off

    for _ in range(300):
        print(test_board.get_fotoresistor_raw())
        print(test_board.get_potentiometer_scale())
        print(test_board.get_temperature_celcius())
        print(test_board.get_volume_sensor_raw())
        s(0.1)

    test_board.set_rgb_red(255)
    s(0.2)
    test_board.set_rgb_red(0)
    test_board.set_rgb_green(255)
    s(0.2)
    test_board.set_rgb_green(0)
    test_board.set_rgb_blue(255)
    s(0.2)
    test_board.set_rgb_blue(0)
    s(0.2)
    test_board.set_pwm_diode(300)
    s(0.2)
    #
    test_board.set_signal_red("on")
    s(0.3)
    test_board.set_signal_yellow("on")
    s(0.3)
    test_board.set_signal_green("on")
    s(0.5)
    test_board.set_signal_red("off")
    s(0.3)
    test_board.set_signal_yellow("off")
    s(0.3)
    test_board.set_signal_green("off")
else:
    print("Something went wrong... check output.")

test_board.full_debug_output()
```

```





