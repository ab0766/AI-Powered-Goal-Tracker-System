# def add():
#     print("Function started")
#     print("Adding numbers")

# def delete():
#     print("Function started")
#     print("Deleting file")

# def save():
#     print("Function started")
#     print("Saving data")

def log(func):
    def wrapper():
        print("Function started")
        func()
    return wrapper

@log  #@log means add = log(add) and so on for the other functions
def add():
    print("Adding numbers")

  
def delete ():
    print("Deleting file")
delete = log(delete)


@log
def save():
    print("Saving data")

add()
save()
delete()







def log(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

@log
def say_hello():
    print("Hello")

say_hello()




def say_hello():
    print("Hello")

say_hello = log(say_hello)