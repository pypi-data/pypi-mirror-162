from pytunelogix.pidlogger import clxlogger
from pytunelogix.stage1 import csvtuner
from pytunelogix.clxpidsim import clxsim
from pytunelogix.simulate import simulator
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
Window.size = (300, 400)

class ButtonApp(App):     
    def build(self):
        self.title = 'pytunelogix'
        button1 = Button(text="PID Logger", size_hint=(1, 1))
        button1.bind(on_press=self.callPIDLogger)
        button2 = Button(text="PID Tuner", size_hint=(1, 1))
        button2.bind(on_press=self.callCSV)
        button3 = Button(text="PID Simulator", size_hint=(1, 1))
        button3.bind(on_press=self.callsim)
        button4 = Button(text="PID CLX Sim", size_hint=(1, 1))
        button4.bind(on_press=self.callclxsim)
        boxlayout = BoxLayout(orientation='vertical')
        boxlayout.add_widget(button1)
        boxlayout.add_widget(button2)
        boxlayout.add_widget(button3)
        boxlayout.add_widget(button4)
        return boxlayout

    def callPIDLogger(self,obj):
        clxlogger.main()

    def callCSV(self,obj):
        csvtuner.main()

    def callsim(self,obj):
        simulator.main()
    
    def callclxsim(self,obj):
        clxsim.main()

if '__main__' == __name__:
    root = ButtonApp()
    root.run()