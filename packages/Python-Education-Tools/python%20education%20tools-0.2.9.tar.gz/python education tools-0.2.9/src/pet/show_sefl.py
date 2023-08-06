import pet.textbook1.download
import datetime
print(datetime.datetime.now())
def show_self(s=__file__):
    print(open(s).read())

show_self()