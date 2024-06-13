from requests import get
import json


class Client:
    def __init__(self):
        try:
            self.offsets = get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
            self.client = get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client.dll.json').json()                  
            self.button = get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/buttons.json').json()
            # shoutout to a2x's cs2 dumper https://github.com/a2x/cs2-dumper
        except:
            print('Error getting offests')
            exit()
    def offset(self, a):
        try:
            return self.offsets['client.dll'][a] 
        except:
            print(f'Error getting {a}')
            exit()
    def clientdll(self, a, b):
        try:
            return self.client['client.dll']['classes'][a]['fields'][b] 
        except:
            print(f'Error getting {a}, {b}.')
            exit()
    def buttons(self, a):
        try:
            return self.button['client.dll'][a] 
        except:
            print(f'Error getting {a}')
            exit()

if __name__ == '__main__':
    print('hi')


