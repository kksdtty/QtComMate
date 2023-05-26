import serial
import queue
import threading


class SerialPortReceiveThread(threading.Thread):
    def __init__(self, parent):
        super(SerialPortReceiveThread, self).__init__()
        self.parent = parent
        self.thread = threading.Event()

    def stop(self):
        self.thread.set()

    def stopped(self):
        return self.thread.is_set()

    def run(self):
        while True:
            if self.stopped():
                break
            try:
                nums = self.parent.serial.inWaiting()
                if (nums > 0):
                    recData = self.parent.serial.read(nums)
                else:
                    continue
                if self.parent.receiveQueue.full():
                    self.parent.receiveQueue.get(False)
                self.parent.receiveQueue.put(recData.decode(errors='replace'))
            except Exception as e:
                print(e)
                continue


class SerialPortSendThread(threading.Thread):
    def __init__(self, parent):
        super(SerialPortSendThread, self).__init__()
        self.parent = parent
        self.thread = threading.Event()

    def stop(self):
        self.thread.set()

    def stopped(self):
        return self.thread.is_set()

    def run(self):
        while True:
            if self.stopped():
                break
            try:
                if not self.parent.sendQueue.empty():
                    send_data = self.parent.sendQueue.get(False)
                    self.parent.serial.write(send_data)
                else:
                    continue
            except queue.Empty as e:
                print(e)
                continue


class SerialPort(object):

    def __init__(self):
        self.serial = None
        self.receiveQueue = queue.Queue(1000)
        self.sendQueue = queue.Queue(1000)

    def open(self, port, baudrate, databit, checkbit, stopbit, xonxoff, rtscts, dsrdtr):
        if self.serial is None:
            try:
                self.serial = serial.Serial(port, baudrate, databit, checkbit, stopbit, None, xonxoff, rtscts, None, dsrdtr)
                self.receiveThread = SerialPortReceiveThread(self)
                self.sendThread = SerialPortSendThread(self)
                self.receiveThread.start()
                self.sendThread.start()
                return True
            except Exception as e:
                return False
                

    def close(self):
        if self.serial is not None:
            self.sendThread.stop()
            self.receiveThread.stop()
            self.serial.close()
            self.serial = None
            return True
        return False

    def write(self, data):
        if self.serial is not None:
            self.sendQueue.put(data)

    def read(self):
        if self.serial is not None:
            if not self.receiveQueue.empty():
                return self.receiveQueue.get(False)
            
