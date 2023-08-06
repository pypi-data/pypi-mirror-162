import minifunc
import os
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
