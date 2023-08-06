

from colorama import init
from termcolor import colored
import random, os
from time import sleep
init(autoreset = False)

if not os.path.exists("./files"):
    os.mkdir("files")

def os_start():
    command = input("Введите команду в Терминал: ")
    os.system(command)
#MINIFUNCT

def write():
    #запись в файл
    files = os.listdir("./files")
    if len(files) >= 5:
        print("Лимит Файлов! ")
        sleep(1)
        
    else:
        name =  input("Введите имя файла: ")
        text=input("Введите текст:") 
        f = open("files/" + name + ".txt", "a+")
        #если файл не создан, он создаётся
        #формат .doc
        f.write("\n")
        f. write(text)
        print("Записано. ")
        f.close()
        
def read():
    #чтение с файла
    name =  input("Введите имя файла: ")
    f = open("files/" + name  + ".txt", "r")
    print(f.read())
    f.close()

def calc():
    #подсчёт
    calc = input("Введите пример: ")
    print(calc, "= " + str(eval(calc)))
    
    
def count_char(text, char):
  count = 0
  for c in text:
    if c == char:
      count += 1
  return count  
def scan():
  name =  input("Введите имя файла: ")
  f = open(name + ".txt", "r")
  text = f.read()
  letters = input("Введите буквы для поиска: ")  #ввод
  for char in letters:
    perc = 100 * count_char(text, char) / len(text)
    print("\'{0}\' - {1} - {2}%".format(char, count_char(text, char), round(perc, 2)))
    f.close()
#конец определений функций

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