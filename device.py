import os
import time
import codecs

from skabenclient.device import BaseDevice
from config import BoilerplateConfig


class BoilerplateDevice(BaseDevice):

    """ Test device should be able to generate all kind of messages

        state_reload -> загрузить текущий конфиг из файла
        state_update(data) -> записать конфиг в файл (и послать на сервер)
        send_message(data) -> отправить сообщение от имени девайса во внутреннюю очередь
    """

    config_class = BoilerplateConfig

    def __init__(self, system_config, device_config, **kwargs):
        super().__init__(system_config, device_config)
        self.running = None

    def run(self):
        """ Main device run routine

            в супере он создает сообщение во внутренней очереди что девайс запущен.
        """
        super().run()
        self.running = True
        while self.running:
            # main routine
            time.sleep(100)
    
    def loadWords(self, wordLen):    
        words = []
        with codecs.open(self.system.get('word_path') + 'words' + str(wordLen) + '.txt','r', 'utf-8') as f:
            for word in f:
                words.append(word.strip("\r\n\t "))
        return words
    
    def getStrPos(self, x, y):
        if x<32:
            yNew = y
            xNew = x-8
        else:
            yNew = y+17
            xNew = x-32
        return (yNew*12+xNew)

    def getStrCoords(self, strPos):
        if strPos<204:
            y = int(strPos / 12)
            x = strPos%12 + 8
        else:
            y = int(strPos / 12) - 17
            x = strPos%12 + 32
        return (x, y)

    def checkWordPosition(charIndex, wordStr):   # Символ проверим на всякий случай
        if not wordStr[charIndex].isalpha():
            return ('', -1, -1)
        i = charIndex
        while wordStr[i].isalpha():
            if i == 0:
                i = -1
                break
            i -= 1
        startPos = i + 1
        i = charIndex
        while wordStr[i].isalpha():
            if i == len(wordStr)-1:
                i = len(wordStr)
                break
            i += 1
        endPos = i - 1
        selWord = wordStr[startPos:endPos+1]
        return (selWord, startPos, endPos)
