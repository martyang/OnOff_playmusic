import os
import threading
import time
import serial
import pyvisa as visa
from pyvisa import VisaIOError
from serial import SerialException


class runThread(threading.Thread):

    def __init__(self, sercom, filename):
        super().__init__()
        self.sercom1 = sercom
        self.filename = filename
        self.running = True

    def stopThread(self):
        self.running = False

    def run(self):
        Connected = 'a2dp connected'
        play = 'AUDIO SYNC START'
        connect_count = 0
        play_count = 0
        time_str = time.strftime('%Y%m%d%H%M%S', time.localtime())
        result_file = open(self.filename + 'result.txt', 'a')
        cycle = 0
        while self.running:
            file1 = open(self.filename + ' %s.txt' % time_str, 'a')
            if self.sercom1.inWaiting():
                data1 = self.sercom1.readline().decode("utf-8")
                if 'Welcome Beken.BT' in data1:
                    file1.write('cycle : %d \n' % cycle)
                    cycle += 1
                elif Connected in data1:
                    connect_count += 1
                elif play in data1:
                    play_count += 1
                file1.write(data1)
                print(data1)
            file1.close()
        time_str2 = time.strftime('%Y:%m:%d:%H:%M:%S', time.localtime())
        result_file.write(time_str2 + '\n')
        result_file.write('开机次数：%d \n' % cycle)
        result_file.write('连接成功次数：%d \n' % connect_count)
        result_file.write('播放音乐次数：%d \n' % play_count)
        result_file.close()
        self.sercom1.close()


class OnOffCycle:

    def __init__(self):
        path = os.getcwd()
        config_file = open(path + '\\config.txt', 'rb')
        content = config_file.read().decode('utf-8')
        self.address = content.split('\n')[0].strip().split(' ')[1]
        self.cycle_time = int(content.split('\n')[1].strip().split(' ')[1])
        self.port1 = content.split('\n')[2].strip().split(' ')[1]
        self.port2 = content.split('\n')[3].strip().split(' ')[1]
        self.baud = content.split('\n')[4].strip().split(' ')[1]
        print(self.baud)

    def start_test(self):
        try:
            sercom1 = serial.Serial(self.port1, self.baud, timeout=5)
            sercom2 = serial.Serial(self.port2, self.baud, timeout=5)
            rm = visa.ResourceManager()
            power = rm.open_resource(self.address, open_timeout=1000)
        except SerialException:
            print('串口无法打开！')
            time.sleep(2)
        except VisaIOError:
            print('电源无法打开！')
            time.sleep(2)
        else:
            power.write('INST:COUP:TRIG CH1,CH2\n')
            power.write('APPL:VOLT 4.0,4.0\n')
            power.write('APPL:CURR 0.2,0.2\n')
            power.write('APPL:OUTP OFF,OFF\n')
            time.sleep(1)
            test_time = 0
            thread1 = runThread(sercom1, self.port1)
            thread2 = runThread(sercom2, self.port2)
            thread1.start()
            thread2.start()
            power.write('APPL:OUTP ON,OFF\n')
            time.sleep(0.4)
            power.write('APPL:OUTP ON,ON\n')
            time.sleep(10)
            sercom1.write(bytes.fromhex('01 E0 FC 02 B2 01 '))
            print('播放音乐')
            time.sleep(10)
            sercom1.write(bytes.fromhex('01 E0 FC 02 B2 01 '))
            print('暂停')
            power.write('APPL:OUTP OFF,OFF\n')
            time.sleep(5)
            test_time += 1
            while test_time < self.cycle_time:
                power.write('APPL:OUTP ON,OFF\n')
                time.sleep(0.4)
                power.write('APPL:OUTP ON,ON\n')
                time.sleep(6)
                sercom1.write(bytes.fromhex('01 E0 FC 02 B2 01 '))
                print('播放音乐')
                time.sleep(10)
                sercom1.write(bytes.fromhex('01 E0 FC 02 B2 01 '))
                print('暂停')
                time.sleep(0.1)
                power.write('APPL:OUTP OFF,OFF\n')
                time.sleep(5)
                test_time += 1
            power.close()
            thread1.stopThread()
            thread1.join()
            thread2.stopThread()
            thread2.join()
            print('completed test')


if __name__ == "__main__":
    cycle = OnOffCycle()
    cycle.start_test()


