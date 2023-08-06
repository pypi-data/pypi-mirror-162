from functions import *

from colorama import init
from termcolor import colored
import random, os
from time import sleep
init(autoreset = False)

def start():
    try:
        input(colored("Добро Пожаловать в MiniFunc \nДля активации определённого раздела просто введите любые данные. ", "white"))     
   #ввод данных
        writer = input(colored("Запись? ", "green"))
        if writer:
          write()
        else:
            reader = input(colored("Чтение? ", "blue"))
            if reader:
                read()
            else:
                 calcer = input(colored("Калькулятор? ", "yellow"))
                 if calcer:
                     calc()
                 else:
                     scanner = input(colored("Сканнер? ", "red"))
                     if scanner:
                         scan()
                     else:
                         oser = input(colored("Командный Консоль? ", "white"))
                         if oser:
                             os_start()
                         else:
                             print("\nПерезапуск...\n")
                             sleep(1)
                             
                             start()  
    except Exception as e:
      print(e)
      print(colored("Ошибка.  Проверьте правильность ввода", "red"))  #вывод при ошибке
if __name__ == "__main__":
    start()