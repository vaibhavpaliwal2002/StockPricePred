import sys
import webbrowser
from threading import Thread

from kivy.app import App
from kivy.graphics import Rectangle, Color, Callback, RoundedRectangle
from kivy.resources import resource_add_path
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.progressbar import ProgressBar
from kivy.properties import StringProperty
from kivy.clock import Clock

from time import sleep
import os
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
from pygooglenews import GoogleNews as pgn
import matplotlib.dates as mdates


from keras.models import load_model
import numpy as np
model = [load_model(r"C:\Users\vaibh\Downloads\model_ver_new_sgd.h5",compile=False)]

class LoginPage(Screen):
    def __init__(self,**kwargs):
        super(LoginPage, self).__init__(**kwargs)
        self.thread=None
        self.open=True
    def login_press(self,instance):
        # print(instance.ids)
        loading_popup(self)
        Window.maximize()
        instance.current="home"
        Clock.schedule_interval(update_callback,300)
    def reg_press(self, username, password):
        print(username.text)
        print(password.text)
        username.text = ""
        password.text = ""

class BackgroundColor(Widget):
    pass
class HomePage(Screen):
    pass
class WindowManager(ScreenManager):
    pass

class ImageButton(ButtonBehavior,Image):
    def __init__(self,**kwargs):
        super(ImageButton,self).__init__(**kwargs)
        self.id=None
        self.instance=None
        self.thread=None

    def predict(self):
        company=companies[self.id][:-4]
        info = yf.download(company, period='63d')
        info['dt'] = info.index.values
        info['year'] = info['dt'].apply(lambda ts: int(str(ts)[:4])).astype('float')
        info['month'] = info['dt'].apply(lambda ts: int(str(ts)[5:7])).astype('float')
        index = np.zeros((1, 1, 51))
        index[0, 0, self.id] = 1
        # print(adani)
        lowmax = info['Low'].max()
        highmax = info['High'].max()

        info = info.drop(columns=['dt'], axis=0)
        for i in info.columns:
            info[i] = info[i] / info[i].max()
        pred = model[0].predict([np.expand_dims(np.expand_dims(info['Open'][:-1].to_numpy(), axis=0), axis=0),
                              np.expand_dims(np.expand_dims(info['Close'][:-1].to_numpy(), axis=0), axis=0),
                              np.expand_dims(np.expand_dims(info['Adj Close'][:-1].to_numpy(), axis=0), axis=0),
                              np.expand_dims(np.expand_dims(info['High'][:-1].to_numpy(), axis=0), axis=0),
                              np.expand_dims(np.expand_dims(info['Low'][:-1].to_numpy(), axis=0), axis=0),
                              np.expand_dims(np.expand_dims(info['Volume'][:-1].to_numpy(), axis=0), axis=0),
                              np.expand_dims(np.expand_dims(info['year'].iloc[-1], axis=0), axis=0),
                              np.expand_dims(np.expand_dims(info['month'].iloc[-1], axis=0), axis=0),
                              index])
        print(pred[0, 0, 0] * lowmax)
        print(info.iloc[-1]['Low'] * lowmax)
        print()
        print(pred[0, 0, 1] * highmax)
        print(info.iloc[-1]['High'] * highmax)
        return

    def on_press(self):
        # self.thread=Thread(target=daily,args=(companies[self.id][:-4],))
        # self.thread.start()

        # self.instance.update("Test")
        self.popup = Popup(title=companies[self.id][:-7],
                      size_hint=(None,None),
                      size=(dp(500),dp(500)),
                      content=Label(text='Hello world'),
                      separator_color=(.1,.1,.1,1))
        self.thread = Thread(target=self.predict)
        self.thread.start()
        daily(companies[self.id][:-4])
        self.popup.open()

#-----------------------------------------------------------------------------

companies = list(os.listdir(r"logos"))
prevPrices=list(list([0.001])*50)
currentPrices=list(list([0.001])*50)
currentColor=list(list(["000000"])*50)
companyStockInstance=list(list(["None"])*50)
newsInstance=[]
newsList=list(list([list([])])*50)
googlenews=pgn()

class RoundedBox(BoxLayout):
    pass

def loading_popup(self):
    self.progress = ProgressBar(max=49,y=dp(40))
    self.popup = Popup(title="",
                       size_hint=(None, None),
                       size=(dp(300), dp(300)),
                       separator_color=(.1, .1, .1, 0),
                       separator_height=dp(0),
                       auto_dismiss=False)
    self.layout = RoundedBox(padding=(dp(50),dp(100)),orientation="vertical")
    self.layout.add_widget(CustomLabel(text="Loading......",halign="center"))
    self.layout.add_widget(self.progress)
    self.popup.content=self.layout
    self.popup.open()
    self.thread = Thread(target=load_values, args=(self,))
    self.thread.start()
    # self.thread.join()

def load_values(self):
    for i in range(50):
        comp = yf.Ticker(companies[i][:-4])
        info=comp.info
        newsList[i] = googlenews.search(info['longName'],helper=True)['entries'][:8]
        currentPrices[i] = info['currentPrice']
        prevPrices[i] = info['previousClose']
        if currentPrices[i] > prevPrices[i]:
            currentColor[i] = "22ff22"
        else:
            currentColor[i] = "ff0000"
        self.progress.value = i
        del comp
    for i in range(50):
        currentPrice = currentPrices[i]
        color = currentColor[i]
        label=companyStockInstance[i]
        label.text=f"[b]{companies[i][:-7].upper()}\n[color={color}][size=40]{currentPrice}[/size][/b]\n{round(currentPrices[i]-prevPrices[i],2)} ({round(((currentPrices[i]-prevPrices[i])/prevPrices[i])*100,2)}%)[/color]"
        news = newsInstance[i]
        instance = news[0]
        for article in range(8):
            news[1][article].text=f"[ref={newsList[i][article]['link']}]{newsList[i][article]['title']}[/ref]\n\n[color=b1b1b1][size=12]{' '.join(newsList[i][article]['published'].split()[1:4])}[/size][/color]"
    self.popup.dismiss()
    return


def update_callback(dt):
    for i in range(4):
        comp = yf.Ticker(companies[i][:-4])
        info = comp.info
        newsList[i] = comp.news
        currentPrices[i] = info['currentPrice']
        prevPrices[i] = info['previousClose']
        if currentPrices[i] > prevPrices[i]:
            currentColor[i] = "22ff22"
        else:
            currentColor[i] = "ff0000"
    for i in range(4):
        currentPrice = currentPrices[i]
        color = currentColor[i]
        label=companyStockInstance[i]
        label.text=f"[b]{companies[i][:-7].upper()}\n[color={color}][size=40]{currentPrice}[/size][/b]\n{round(currentPrices[i]-prevPrices[i],2)} ({round(((currentPrices[i]-prevPrices[i])/prevPrices[i])*100,2)}%)[/color]"
        news = newsInstance[i]
        instance = news[0]
        for article in range(8):
            news[1][article].text=f"[ref={newsList[i][article]['link']}]{newsList[i][article]['title']}[/ref]\n\n[color=b1b1b1]{' '.join(newsList[i][article]['published'].split()[1:4])}[/color]"
    return


#-----------------------------------------------------------------------------


class CustomLabel(Label):
    pass
class BackgroundBox():
    pass
class LineRectangle(BoxLayout):
    pass

#----------------------------------------------------------------------------




def daily(company):
    data = yf.download(tickers=company, period="1d", interval="1m")
    data['dt']=data.index
    data.index=data.dt.dt.tz_localize(None)
    xformatter=mdates.DateFormatter('%H:%M')
    plt.plot(data['Close'])
    plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    plt.show()

#---------------------------------------------------


class CompanyStack(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "lr-tb"
        size = dp(100)
        self.spacing=dp(10)
        self.padding=(dp(0),dp(5),dp(5),dp(5))
        # self.size_hint_max_x=dp(300)
        for i in range(50):
            container=LineRectangle(size_hint=(1,None),
                                    height=size)
            container.padding=(dp(20),dp(0))
            container.spacing=dp(0)

            info = CustomLabel()
            info.markup = True
            info.size_hint = (None, 1)
            info.halign='center'
            info.width = dp(200)
            info.font_size = dp(20)
            info.id=companies[i][:-7]

            img_but=ImageButton()
            img_but.source=os.path.join("logos",companies[i])
            img_but.size_hint=(None,None)
            img_but.size=(size*4/5,size*4/5)
            img_but.pos_hint={"center_y":0.5}
            img_but.id=i
            img_but.instance=info
            companyStockInstance[i]=info

            container.add_widget(img_but)
            container.add_widget(info)

            self.add_widget(container)

class Link(Label):
    def pressed(self, link):
        webbrowser.open(link)

class Heading(Link):
    pass

class NewsStack(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "lr-tb"
        size = dp(100)
        self.spacing = dp(10)
        self.padding = (dp(0), dp(5), dp(0), dp(5))
        self.add_widget(CustomLabel(markup=True, text='Top Stories', size_hint=(1, None), height=size / 5,
                               font_size=dp(20), color=(1, 1, 1, 1),halign='left'))
        for i in range(50):
            news=newsList[i]
            index=len(newsInstance)
            newsInstance.append([])
            newsInstance[index].append(self)
            newsInstance[index].append([])
            self.add_widget(Heading(markup=True,text=f"[b]{companies[i][:-7]}[/b]",size_hint=(1,None),height=size/2,font_size=dp(40),color=(1,1,1,1)))
            for j in range(8):
                link=Link()
                link.text=""
                link.size_hint=(.25,None)
                link.height=size*2
                self.add_widget(link)
                newsInstance[index][1].append(link)
            self.add_widget(BoxLayout(size_hint=(1,None),height=dp(50)))

kv = Builder.load_file("stockpred.kv")

class StockApp(App):
    def build(self):
        Window.clearcolor=(0,0,0,0)
        return kv

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    StockApp().run()
