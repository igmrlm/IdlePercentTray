from infi.systray import SysTrayIcon
from PIL import Image, ImageDraw,ImageFont
import time
import psutil
import threading
import wx
import wx.adv
import datetime
from wx.lib.embeddedimage import PyEmbeddedImage

def background():
    while True:
        uptime = time.time() - psutil.boot_time()
        global idle_ratio
        idle_ratio = psutil.cpu_times().idle / psutil.cpu_count() / uptime * 100
        d = uptime // (24 * 3600)
        uptime = uptime % (24 * 3600)
        h = uptime // 3600
        uptime %= 3600
        m = uptime // 60
        uptime %= 60
        s = uptime
        print(idle_ratio)
        time.sleep(10)
        if stop_threads:
            break
global stop_threads
stop_threads = False
# print(f"Uptime: {d:n}d {h:02n}:{m:02n}:{s:02n} - Idle Ratio: {idle_ratio:02.2f}%")


b = threading.Thread(name='background', target=background)
print("starting thread")
b.start()
print("\nIdle ratio:")
print(idle_ratio)
#
# A white box 28x28 pixels
#
toggletest = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAIAAAD9b0jDAAAACXBIWXMAAAsTAAALEwEAmpwY'
    b'AAAAB3RJTUUH4wMfCgElTFaeRQAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJ'
    b'TVBkLmUHAAAAKElEQVRIx2P8//8/A7UBEwMNwKiho4aOGjpq6Kiho4aOGjpq6OAzFADRYgM1'
    b'8cIRtgAAAABJRU5ErkJggg==')

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        self.toggle = 0
        wx.adv.TaskBarIcon.__init__(self)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.OnToggle)
        self.font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        self.font.SetPointSize(4)
        self.OnSetIcon(self.NewIcon())

    def CreatePopupMenu(self):
        menu = wx.Menu()
        togglem = wx.MenuItem(menu, wx.NewId(), 'Toggle Icon')
        menu.Bind(wx.EVT_MENU, self.OnToggle, id=togglem.GetId())
        menu.Append(togglem)
        menu.AppendSeparator()
        flashm = wx.MenuItem(menu, wx.NewId(), 'Flashing Icon')
        menu.Bind(wx.EVT_MENU, self.OnTimer, id=flashm.GetId())
        menu.Append(flashm)
        menu.AppendSeparator()
        quitm = wx.MenuItem(menu, wx.NewId(), 'Quit')
        menu.Bind(wx.EVT_MENU, self.OnQuit, id=quitm.GetId())
        menu.Append(quitm)
        return menu

    def NewIcon(self):
        bitmap = wx.Bitmap(toggletest.Bitmap)
        dc = wx.MemoryDC(bitmap)
        # Use current time as text, for want of something useful
        dc.SetFont(self.font)
        ratio = str(idle_ratio)
        dc.DrawText(ratio, 0, 7)
        del dc
        return bitmap

    def OnSetIcon(self, bitmap):
        icon = wx.Icon()
        icon.CopyFromBitmap(bitmap)
        self.SetIcon(icon)

    def OnToggle(self, event):
        bitmap = self.NewIcon()
        self.OnSetIcon(bitmap)

    def OnTimer(self,event):
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnUseTimer)
        self.timer.Start(10000)

    def OnUseTimer(self,event):
        self.OnToggle(None)

    def OnQuit(self, event):
        self.RemoveIcon()
        wx.CallAfter(self.Destroy)
        self.frame.Close()
        global stop_threads
        stop_threads = True


if __name__ == '__main__':
    app = wx.App()
    frame=wx.Frame(None)
    TaskBarIcon(frame)
    app.MainLoop()
