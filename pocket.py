from window_tk import Window
from threading import Timer
import os
from random import randint as rand

startdir = 'list/'
ext = '.list'

class RecList:
    def __init__(self, name):
        self.filename = startdir+name+ext
        self._data = []
        if os.path.isfile(self.filename):
            f = open(self.filename, 'r')
            while True:
                s = f.readline()
                if not s: break
                self._data.append(s[:-1])
            f.close()
        else:
            f = open(self.filename, 'w')
            f.close()

    def save(self):
        f = open(self.filename, 'w')
        for i in self._data:
            f.write(i+"\n")
        f.close()

    def add(self, value):
        if value not in self._data:
            if not len(self._data):
                self._data.append('--')
            self._data = self._data[0:1] + [value] + self._data[1:]
            self.save()

    def first(self, value):
        if value not in self._data:
            self._data = [value] + self._data
            self.save()

    def info(self):
        return self._data

    def get(self, mode='random'):
        ret = ''
        if len(self._data) < 2:
            self._data = []
        elif mode == 'stack':
            self._data = self._data[1:]
            ret = self._data[0]
        elif mode == 'queue':
            self._data = [self._data[-1]] + self._data[1:-1]
            ret = self._data[0]
        elif mode == 'random':
            n = rand(1,len(self._data)-1)
            self._data = [self._data[n]] + self._data[1:n] + self._data[n+1:]
            ret = self._data[0]
        self.save()
        return ret

    def cut(self, n):
        if n < len(self._data):
            ret = self._data[n]
            self._data = self._data[:n] + self._data[n+1:]
            self.save()
            return ret
        return ''

    def clear(self):
        self._data = []
        self.save()

    def delete(self):
        os.remove(self.filename)

class Confirm:
    def __init__(self, txt, func):
        self.func = func
        w = Window('Вы уверены?')
        self.tk = w
        w.label(txt)
        w.startRow()
        w.firstCol(1,150)
        w.button('Да')
        w.onClick(self.submit)
        w.nextCol(1,150)
        w.button('Нет')
        w.onClick(w.close)
        w.endRow()
        w.go()
    def submit(self, tag):
        self.func()
        self.tk.close()

class AddForm:
    def __init__(self, func):
        self.func = func
        w = Window('Добавить список')
        self.tk = w
        w.label('Название списка:')
        w.nextCol()
        self.name = w.input()
        w.nextRow()
        w.button('OK')
        w.onSubmit(self.submit)
        w.nextCol()
        w.button('Отмена')
        w.onReset(w.close)
        w.go()
    def submit(self, tag):
        self.func(self.tk.read(self.name))
        self.tk.close()


class MainForm:
    def __init__(self):
        self.currentName = ''
        self.run = True
        self.lastInfo = ''
        self.lastMode = 'random'

        w = Window('Карман v2.0')
        self.tk = w
        w.startRow()
        w.firstRow(0,30)
        w.button('Добавить')
        w.onClick(lambda x: AddForm(self.addList))
        w.nextRow(0,30)
        w.button('Переименовать')
        w.nextRow(1, 400)
        self.filelist = w.listbox()
        w.onSelect(self.showList)
        w.onDoubleClick(self.forceAdd)
        w.nextRow(0,30)
        w.button('Удалить')
        w.onClick(self.prep_removeList)
        w.endRow()
        w.nextCol(2, 300)
        w.startRow(0,30)
        w.firstCol(1,100)
        w.button('Повтор')
        w.onClick(self.restore)
        w.nextCol(1,100)
        w.button('Заменить')
        w.onClick(self.another)
        w.nextCol(1,100)
        w.button('Сначала')
        w.onClick(self.asStart)
        w.nextRow(0,60)
        w.firstCol(1,100)
        w.button('Стек')
        w.onClick(self.readAsStack)
        w.nextCol(1,100)
        w.button('Рандом')
        w.onClick(self.readAsRandom)
        w.nextCol(1,100)
        w.button('Очередь')
        w.onClick(self.readAsQueue)
        w.nextRow()
        self.records = w.listbox()
        w.onDoubleClick(self.removeRecord)
        w.nextRow(0,30)
        w.firstCol(1,100)
        w.button('Кан.')
        w.onClick(lambda x: AddForm(self.test))
        w.nextCol(1,100)
        w.button('Реж.')
        w.nextCol(1,100)
        w.button('Корзина')
        w.endRow()
        self.drawFileList()
        self.checkClipboard()
        w.go()
        self.run = False

    def checkClipboard(self):
        info = self.getFromClipboard()
        if info != self.lastInfo:
            self.lastInfo = info
            self.addToList(info)
        if self.run: Timer(1, self.checkClipboard).start()

    def getFileList(self):
        M = os.listdir(startdir)
        N = []
        for i in M:
            if i[-5:] == '.list':
                N.append(i[:-5])
        N.sort()
        return N
    def drawFileList(self):
        N = self.getFileList()
        self.tk.write(self.filelist, N)
    def addList(self, s):
        x = RecList(s)
        self.drawFileList()
    def getListName(self):
        options = self.tk.selection(self.filelist)
        if not options: return self.currentName
        name = self.tk.read(self.filelist)[options[0]]
        self.currentName = name
        return name
    def showList(self, tag):
        name = self.getListName()
        if name:
            x = RecList(name)
            M = x.info()
            self.tk.write(self.records, M)

    def addToList(self, str):
        name = self.getListName()
        if name:
            x = RecList(name)
            x.add(str)
            self.tk.write(self.records, x.info())

    def forceAdd(self, tag):
        self.addToList(self.getFromClipboard())

    def removeRecord(self, tag):
        name = self.getListName()
        options = self.tk.selection(self.records)
        if name and options:
            n = options[0]
            x = RecList(name)
            str = x.cut(n)
            self.lastInfo = str
            self.setToClipboard(str)
            self.showList(None)

    def readValue(self, name, mode):
        x = RecList(name);
        mod = mode
        for loop in range(100):
            ret = x.get(mod)
            if not os.path.isfile(startdir+ret+ext):
                return ret
            ret = self.readValue(ret, mode)
            if ret: break
            if mod == 'stack': mod = 'queue'
        x.first(ret)
        return ret

    def readCurrentValue(self, mode):
        self.lastMode = mode
        name = self.getListName()
        val = ''
        if name:
            val = self.readValue(name, mode)
        self.setToClipboard(val)
        self.lastInfo = val
        self.showList(None)
    def readAsStack(self, tag):
        self.readCurrentValue('stack')
    def readAsQueue(self, tag):
        self.readCurrentValue('queue')
    def readAsRandom(self, tag):
        self.readCurrentValue('random')

    def restore(self, tag):
        name = self.getListName()
        if name:
            x = RecList(name)
            M = x.info()
            if M: self.setToClipboard(M[0])

    def markAsStart(self, name):
        x = RecList(name)
        flag = False
        for i in x.info():
            if os.path.isfile(startdir+i+ext):
                self.markAsStart(i)
                flag = True
        if flag:
            x.get('stack')
        if '--' not in x.info():
            x.first('--')
    def asStart(self, tag):
        name = self.getListName()
        if name:
            self.markAsStart(name)
        self.showList(None)

    def another(self, tag):
        if self.lastMode == 'stack':
            self.lastMode = 'random'
        self.asStart(None)
        self.readCurrentValue(self.lastMode)

    def getFromClipboard(self):
        try:
            data = self.tk.tk.clipboard_get()
        except Exception:
            data = ''
        return data

    def setToClipboard(self, data):
        self.tk.tk.clipboard_clear()
        self.tk.tk.clipboard_append(data)

    def prep_removeList(self, tag):
        name = self.getListName()
        if name:
            Confirm('Удалить список?', self.removeList)

    def removeList(self):
        name = self.getListName()
        if name:
            x = RecList(name)
            x.delete()
            self.currentName = ''
            self.tk.write(self.records, [])
            self.drawFileList()

MainForm()
