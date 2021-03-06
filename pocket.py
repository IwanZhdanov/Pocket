from window_tk import Window
from threading import Timer
import os
import re
import time
from random import randint as rand

startdir = 'list/'
ext = '.list'
sett = 'data/settings.dat'
ico = 'data/1.png'

class Modes:
    def __init__(self, items):
        self._items = items
        self._act = [0, 0]

    def sw(self):
        if self._act[1] < time.time():
            self._items = [self._items[self._act[0]]] + self._items[0:self._act[0]] + self._items[self._act[0]+1:]
            self._act[0] = 1
        else:
            self._act[0] = (self._act[0] + 1) % len(self._items)
        self._act[1] = time.time() + 3
        return self.get()
    def get(self):
        return self._items[self._act[0]][0]
    def text(self):
        return self._items[self._act[0]][1]


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

    def change(self, old_txt, new_txt):
        for i in range(len(self._data)):
            if self._data[i] == old_txt:
                self._data[i] = new_txt
        self.save()

    def first(self, value):
        if value not in self._data:
            self._data = [value] + self._data
            self.save()

    def append(self, value):
        if value not in self._data:
            self._data.append(value)
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

    def removeByRegExp(self, reg):
        lst = []
        for i in self._data:
            if not re.search('(?i)'+reg, i):
                lst.append(i)
        self._data = lst;
        self.save()

    def clear(self):
        self._data = []
        self.save()

    def delete(self):
        os.remove(self.filename)

class Confirm:
    def __init__(self, txt, func):
        self.func = func
        w = Window('???? ???????????????')
        self.tk = w
        w.label(txt)
        w.startRow()
        w.firstCol(1,150)
        w.button('????')
        w.onClick(self.submit)
        w.nextCol(1,150)
        w.button('??????')
        w.onClick(w.close)
        w.endRow()
        w.go()
    def submit(self, tag):
        self.func()
        self.tk.close()

class AddForm:
    def __init__(self, func, txt=""):
        self.func = func
        w = Window('???????????????? ????????????')
        self.tk = w
        w.label('???????????????? ????????????:')
        w.nextCol()
        self.name = w.input(txt)
        w.nextRow()
        w.button('OK')
        w.onSubmit(self.submit)
        w.nextCol()
        w.button('????????????')
        w.onReset(w.close)
        w.go()
    def submit(self, tag):
        self.func(self.tk.read(self.name))
        self.tk.close()

class RemarkForm:
    def __init__(self, func, txt=""):
        self.func = func
        w = Window('????????????????')
        self.tk = w
        w.label('??????????????:')
        w.nextCol(1, 400)
        self.name = w.input(txt)
        w.nextRow()
        w.button('OK')
        w.onSubmit(self.submit)
        w.nextCol()
        w.button('????????????')
        w.onReset(w.close)
        w.go()
    def submit(self, tag):
        self.func(self.tk.read(self.name))
        self.tk.close()

class RenameForm:
    def __init__(self, name, func):
        self.func = func
        self.old_name = name
        w = Window('??????????????????????????')
        self.tk = w
        w.label('???????????? ????????????????:')
        w.label('?????????? ????????????????:')
        w.nextCol()
        w.label(name)
        self.new_name = w.input(name)
        w.nextRow()
        w.button('OK')
        w.onSubmit(self.submit)
    def submit(self, tag):
        self.func(self.old_name, self.tk.read(self.new_name))
        self.tk.close()


class DeleteFromList:
    def __init__(self, name, func):
        self.func = func
        w = Window('?????????????? ?????????????????? ??????????????')
        self.tk = w
        w.label('??????????????????:')
        w.nextCol(1, 400)
        self.reg = w.input(self.toReg(name))
        w.nextRow()
        w.button('OK')
        w.onSubmit(self.submit)
        w.nextCol()
        w.button('????????????')
        w.onReset(w.close)
        w.go()
    def submit(self, tag):
        self.func(self.tk.read(self.reg))
        self.tk.close()
    def toReg(self, s):
        if '\r' in s: s = s[:s.index('\r')]
        while s and s[0] in ['\t', ' ']: s = s[1:]
        while s and s[-1] in ['\t', ' ']:  s = s[:-1]
        scr = '.\\/{}[]()|^&*+?'
        ret = ''
        for ch in s:
            if ch in scr: ret += '\\'
            ret += ch
        ret = '^'+ret+'$'
        return ret

class Basket:
    def __init__(self, main, listName):
        self._main = main
        self._listName = listName

        w = Window(listName)
        self.tk = w
        w.flags(top=True)
        w.firstRow(1,50)
        w.firstCol(1,120)
        self.btn = w.button('0')
        w.onClick(self.change)
        w.nextCol(1,60)
        self.mark = w.button('x')
        w.onClick(self.another)

        self.getQuaTmr()

        w.go()

    def change(self, tag):
        self._main.readNext(self._listName)
        self.getQua()

    def another(self, tag):
        self._main.another(self._listName)
        self.getQua()

    def getQua(self):
        self.tk.write(self.btn, str(self._main.readQua(self._listName)))
        self.tk.write(self.mark, 'L' if self._main.isLinkInClipboard() else 'not L')

    def getQuaTmr(self):
        self.getQua()
        Timer(1, self.getQuaTmr).start()


class MainForm:
    def __init__(self):
        self.currentName = ''
        self.run = True
        self.lastInfo = ''
        self.lastMode = 'random'
        self.mode = Modes([('link','????????????'),('off','????????'),('nopassw','????????'),('all','??????')])
        self.canon = Modes([('off','??????'),('on','????')])

        sz = 100

        w = Window('???????????? v2.0')
        self.tk = w
        w.flags(ico=ico)
        w.startRow(0,30)
        w.button('????????????????')
        w.onClick(lambda x: AddForm(self.addList, self.tk.read(self.searchName) if self.tk.read(self.searchName) else self.getListName()+' R'))
        w.nextRow(0,30)
        w.button('??????????????????????????')
        w.onClick(self.prep_rename)
        w.nextRow(0,30)
        w.startCol()
        self.searchName = w.input()
        w.onChange(lambda x: self.drawFileList())
        w.nextCol(0,30)
        w.button('x')
        w.onClick(lambda x: self.drawFileList(''))
        w.endCol()
        w.nextRow(1, 100)
        self.filelist = w.listbox()
        w.onSelect(self.showList)
        w.onDoubleClick(self.forceAdd)
        w.nextRow(0,30)
        w.startCol()
        w.button('??????????????')
        w.onClick(self.prep_removeList)
        w.nextCol()
        w.button('????????????????')
        w.onClick(self.prep_deleteFromList)
        w.endCol()
        w.endRow()
        w.nextCol(3, 200)
        w.startRow(0,30)
        w.firstCol(1,sz)
        w.button('????????????')
        w.onClick(self.restore)
        w.nextCol(1,sz)
        w.button('????????????????')
        w.onClick(self.another)
        w.nextCol(1,sz)
        w.button('??????????????')
        w.onClick(self.asStart_soft)
        w.nextRow(0,60)
        w.firstCol(1,sz)
        self.mode_stack = w.button('????????')
        w.onClick(self.readAsStack)
        w.nextCol(1,sz)
        self.mode_random = w.button('????????????')
        w.onClick(self.readAsRandom)
        w.nextCol(1,sz)
        self.mode_queue = w.button('??????????????')
        w.onClick(self.readAsQueue)
        w.nextRow(0,30)
        w.startCol(0,30)
        w.button('?')
        w.onClick(lambda x: self.find_sublist())
        w.nextCol()
        self.listcapt = w.button('')
        w.onClick(self.listNameToClipboard)
        w.nextCol(0,30)
        w.button('+')
        w.onClick(lambda x: RemarkForm(self.addToList, self.getFromClipboard()))
        w.endCol()
        w.nextRow(3,50)
        self.records = w.listbox()
        w.onSelect(self.makeMenu)
        w.onDoubleClick(self.removeRecord)
        w.nextRow(0,50)
        self.variants = w.listbox()
        w.onSelect(self.pickVariant)
        w.onDoubleClick(self.forceAdd)
        w.nextRow(0,30)
        w.firstCol(1,sz)
        self.can_btn = w.button('??????.')
        w.onClick(self.chCan)
        w.nextCol(1,sz)
        self.mod_btn = w.button('??????.')
        w.onClick(self.chMod)
        w.nextCol(1,sz)
        w.button('??????????????')
        w.onClick(lambda x: Basket(self, self.getListName()))
        w.endRow()

        self.drawFileList()
        self.checkClipboard()
        self.showStates()
        w.go()
        self.run = False

    def is_passw(self, s):
        if re.search('^[A-Za-z0-9]{10,20}$', s):
            return True
        return False

    def make_canonical(self, txt):
        ret = txt
        if os.path.isfile(sett):
            f = open (sett, 'r')
            found = False
            while True:
                s = f.readline()
                if not s: break
                s = s[:-1]
                if s[0] == '#':
                    found = re.search(s[1:], txt)
                elif found:
                    cmd = re.search('([^:]*):(.*)', s)
                    if not cmd[1]:
                        mem = cmd[2]
                        last = found.lastindex
                        for i in range(0,last+1):
                            mem = mem.replace('$'+str(i), found[i])
                        ret = mem
            f.close()
        return ret

    def checkStopList(self, txt):
        x = RecList('z_STOPLIST')
        ret = txt in x.info()
        if not ret: x.add(txt)
        return ret

    def checkClipboard(self):
        info = self.getFromClipboard()
        info = re.search('^[^\r\n]*', info)[0]
        flag = True
        if not info or info == self.lastInfo: flag = False
        mod = self.mode.get()
        if mod == 'off': flag = False
        if mod == 'link' and info[0:4] != 'http' and info[0:7] != 'file://': flag = False
        if mod == 'nopassw' and self.is_passw(info): flag = False
        if self.canon.get() == 'on': info = self.make_canonical(info)
        if not info or info == self.lastInfo: flag = False
        if flag:
            flag = not self.checkStopList(info)
        if flag:
            self.lastInfo = info
            self.addToList(info)
        if self.run: Timer(0.3, self.checkClipboard).start()

    def getMultilangRegExp(self, txt):
        ret = "(?i)"
        gr = {'w':'??', 'e':'??????', 'r':'??', 't':'??', 'y':'??', 'u':'????',
         'i':'??', 'o':'??', 'p':'??', 'a':'????', 's':'??????', 'd':'??',
         'f':'??', 'g':'????', 'h':'??', 'j':'????', 'k':'??', 'l':'??', 'z':'??',
         'c':'????', 'v':'??', 'b':'??', 'n':'??', 'm':'??',"'":"????",
         '2':'????????abc??????', '3':'??????????def????', '4':'????????ghi??????',
         '5':'????????jkl????????', '6':'????????mno??????', '7':'????????pqrs??????????',
         '8':'????????tuv????????', '9':'????????wxyz??????', '0':' '}
        s = txt.lower()
        for ch in s:
            if ch in gr:
                ret += '['+ch+gr[ch]+']'
            else:
                ret += ch
        return ret

    def getFileList(self):
        M = os.listdir(startdir)
        N = []
        for i in M:
            if i[-5:] == '.list':
                N.append(i[:-5])
        N.sort(key=lambda x: x.lower())
        return N
    def drawFileList(self, search=None):
        if search == None:
            search = self.tk.read(self.searchName)
        else:
            self.tk.write(self.searchName, search)
        N = self.getFileList()
        if not search:
            M = N
        else:
            M = []
            for i in N:
                if re.search(self.getMultilangRegExp(search), i):
                    M.append(i)
        self.tk.write(self.filelist, M)
    def addList(self, s):
        x = RecList(s)
        self.drawFileList()
    def getListName(self):
        options = self.tk.selection(self.filelist)
        if not options: return self.currentName
        name = self.tk.read(self.filelist)[options[0]]
        self.currentName = name
        return name

    def getListQuaOne(self, name):
        x = RecList(name)
        info = x.info()
        q = 0
        for i in info:
            if not os.path.isfile(startdir+i+ext):
                q += 1
        if q > 0: q -= 1
        return q
    def getListQua(self, name, first=True):
        x = RecList(name)
        info = x.info()
        q = 0
        for i in info:
            if os.path.isfile(startdir+i+ext):
                q += self.getListQua(i)
            else:
                q += 1
        if q > 0: q -= 1
        return q
    def readQua(self, name=None):
        if not name: name = self.getListName()
        if name:
            return str(self.getListQuaOne(name)) + ' / ' + str(self.getListQua(name))
        return 0

    def showList(self, tag):
        name = self.getListName()
        if name:
            x = RecList(name)
            M = x.info()
            self.tk.write(self.records, M)
            self.tk.write(self.listcapt, name + ' ('+str(self.getListQuaOne(name))+' / '+str(self.getListQua(name))+')')

    def addToList(self, txt):
        name = self.getListName()
        if name:
            x = RecList(name)
            x.add(txt)
            self.tk.write(self.records, x.info())
            self.tk.write(self.listcapt, name + ' ('+str(self.getListQuaOne(name))+' / '+str(self.getListQua(name))+')')

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

    def readCurrentValue(self, mode, name=None):
        self.lastMode = mode
        if not name: name = self.getListName()
        val = ''
        if name:
            val = self.readValue(name, mode)
        self.setToClipboard(val)
        self.lastInfo = val
        self.showList(None)
        self.makeMenuByStr(val)
        self.showStates()
    def readAsStack(self, tag):
        self.readCurrentValue('stack')
    def readAsQueue(self, tag):
        self.readCurrentValue('queue')
    def readAsRandom(self, tag):
        self.readCurrentValue('random')
    def readNext(self, tag=None):
        self.readCurrentValue(self.lastMode, tag)

    def listNameToClipboard(self, tag):
        name = self.getListName()
        self.lastInfo = name
        self.setToClipboard(name)

    def rename(self, old_name, new_name):
        x = RecList(old_name)
        y = RecList(new_name)
        if not y.info():
            for i in x.info():
                y.append(i)
            x.delete()
            self.currentName = new_name
            files = self.getFileList()
            for i in files:
                z = RecList(i)
                z.change(old_name, new_name)
        self.drawFileList()
    def prep_rename(self, tag):
        name = self.getListName()
        if name:
            RenameForm(name, self.rename)

    def restore(self, tag):
        name = self.getListName()
        if name:
            x = RecList(name)
            M = x.info()
            if M:
                self.setToClipboard(M[0])
                self.makeMenuByStr(M[0])

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

    def markAsStart_soft(self, name, value=""):
        x = RecList(name)
        info = x.info()
        if info and not value: value = info[0]
        ret = value in info
        for inf in info[1:]:
            if os.path.isfile(startdir+inf+ext):
                if self.markAsStart_soft(inf, value):
                    x.get('stack')
                break
        if '--' not in x.info():
            x.first('--')
        return ret
    def asStart_soft(self, tag=None):
        if tag: name = tag
        else: name = self.getListName()
        if name:
            self.markAsStart_soft(name)
        self.showList(None)

    def another(self, tag=None):
        if self.lastMode == 'stack':
            self.lastMode = 'random'
        if tag: name = tag
        else: name = self.getListName()
        if name:
            x = RecList(name)
            info = x.info()
            if info:
                start = info[0]
                for loop in range(100):
                    self.asStart_soft(name)
                    self.readCurrentValue(self.lastMode, name)
                    y = RecList(name)
                    info2 = y.info()
                    if not info2 or info2[0] != start: break

    def getFromClipboard(self):
        try:
            data = self.tk.tk.clipboard_get()
        except Exception:
            data = ''
        return data

    def setToClipboard(self, data):
        self.tk.tk.clipboard_clear()
        self.tk.tk.clipboard_append(data)

    def isLinkInClipboard(self):
        s = self.getFromClipboard()
        return s[:4] == 'http' or s[:7] == 'file://'

    def makeMenuOptions(self, txt):
        ret = []
        if os.path.isfile(sett):
            f = open(sett, 'r')
            cond = False
            while True:
                s = f.readline()
                if not s: break
                s = s[:-1]
                if not s: continue
                if s[0] == '#':
                    cond = re.search(s[1:], txt)
                elif cond:
                    cmd = re.search('([^:]*):(.*)', s)
                    if cmd[1]:
                        opt = cmd[2]
                        q = cond.lastindex
                        for i in range(0,q+1):
                            opt = opt.replace('$'+str(i), cond[i])
                        ret.append(cmd[1]+': '+opt)
            f.close()
        return ret

    def makeMenu(self, tag):
        name = self.getListName()
        options = self.tk.selection(self.records)
        txt = ''
        if name and options:
            x = RecList(name)
            n = options[0]
            info = x.info()
            if len(info) > n: txt = info[n]
            self.tk.write(self.variants, self.makeMenuOptions(txt))

    def makeMenuByStr(self, txt):
        self.tk.write(self.variants, self.makeMenuOptions(txt))

    def pickVariant(self, tag):
        options = self.tk.selection(self.variants)
        if options:
            n = options[0]
            vars = self.tk.read(self.variants)
            line = vars[n]
            a = line.index(': ')
            txt = line[a+2:]
            self.lastInfo = txt
            self.setToClipboard(txt)

    def prep_removeList(self, tag):
        name = self.getListName()
        if name:
            Confirm('?????????????? ?????????????', self.removeList)

    def removeList(self):
        name = self.getListName()
        if name:
            x = RecList(name)
            x.delete()
            self.currentName = ''
            self.tk.write(self.records, [])
            self.drawFileList()

    def prep_deleteFromList(self, tag):
        name = self.getListName()
        if name:
            DeleteFromList(self.getFromClipboard(), self.deleteFromList)

    def delRegFromList(self, name, reg):
        files = self.getFileList()
        x = RecList(name)
        for i in x.info():
            if i in files:
                self.delRegFromList(i, reg)
        x.removeByRegExp(reg)

    def deleteFromList(self, reg):
        name = self.getListName()
        if name:
            x = RecList(name)
            self.delRegFromList(name, reg)
            self.showList(None)

    def find_sublist_by(self, name, search):
        ret = ''
        files = self.getFileList()
        x = RecList(name)
        for i in x.info():
            if i == search: ret = name
            if i in files:
                ret = self.find_sublist_by(i, search)
                if ret: break
        return ret

    def find_sublist(self):
        cont = True
        if cont:
            name = self.getListName()
            if not name: cont = False
        if cont:
            x = RecList(name)
            inf = x.info()
            if len(inf) == 0: cont = False
        if cont:
            search = inf[0]
            found = self.find_sublist_by(name, search)
            if not found: cont = False
        if cont:
            self.currentName = found
            self.drawFileList()
            self.showList(None)

    def showStates(self):
        self.tk.write(self.can_btn, '??:'+self.canon.text())
        self.tk.write(self.mod_btn, '??:'+self.mode.text())
        m = (
            ('stack','????????',self.mode_stack),
            ('queue','??????????????',self.mode_queue),
            ('random','????????????',self.mode_random),
            )
        for i in m:
            s = i[1]
            if self.lastMode == i[0]: s = '['+s+']'
            self.tk.write(i[2], s)

    def chCan(self, tag):
        self.canon.sw()
        self.showStates()

    def chMod(self, tag):
        self.mode.sw()
        self.showStates()

MainForm()
