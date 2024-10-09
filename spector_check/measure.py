import pandas as pd
import os
from time import sleep
from threading import Thread
import serial
from serial.tools import list_ports

# CONSTANT
BAUDRATE = 115200
DMA_LENGTH = 512


class Monitor:
    def __init__(self, master: serial.Serial) -> None:
        self.master: serial.Serial = master
        self.is_recording = False          # データの保存を開始したかどうか
        self.file_name = "measurement_data3"  # デフォルトのファイル名

        self.measure_data_37 = []          # 37列のデータ
        self.measure_data_38 = []          # 38列のデータ

        self.poll = Thread(target=self.polling)
        self.poll.start()

    def __del__(self):
        print("Close port.")
        self.master.close()

    def send_command(self, command):

        if command is None:
            return

        for chr in command:
            self.master.write(chr.encode("utf-8"))
            sleep(1e-3)

        self.master.write("\r\n".encode())

    def polling(self):

        while self.master.is_open:
            try:
                receive = self.master.readline().decode().strip()

                if not receive:
                    continue

                try:
                    param0, param1 = (int(i) for i in receive.split(","))
                except ValueError:
                    continue

                if param1 == 0:
                    print(param0, param1)

                self.handle_receive(param0, param1)

            except Exception as e:
                print(f"Error during polling: {e}")
                continue

    def handle_receive(self, param0: int, param1: int) -> None:

        # param0が30の場合
        if param0 == 30:

            # 測定開始のトリガーが設定されている場合に限りデータを処理
            if param1 == 22:
                print(">> Data recording started.")
                self.is_recording = True

            if param1 == 23:
                print(">> Data recording and measurement ended.")
                self.is_recording = False
                self.save()

        if self.is_recording:
            self.process_data(param0, param1)

    def process_data(self, param0: int, param1: int) -> None:
        """受信したデータを処理して、それぞれの列（37, 38）に格納"""

        if param0 == 37:
            self.measure_data_37.append(param1)

        if param0 == 38:
            self.measure_data_38.append(param1)

    def end_polling(self):
        """ポーリングを終了して接続を閉じる"""
        self.master.close()
        self.poll.join()

    def save(self):
        """データをCSVファイルに保存する"""
        # データを保存するファイルパスの設定
        file_path = f'./result/{self.file_name}.csv'

        # ディレクトリが存在しない場合は作成
        if not os.path.exists('./result'):
            os.makedirs('./result')

        # 37列と38列のデータをCSVに保存
        with open(file_path, "w") as f:
            f.write("Col37,Col38\n")

            for idx, (data_37, data_38) in enumerate(zip(self.measure_data_37, self.measure_data_38, strict=True)):
                f.write(f"{idx},{data_37},{data_38}\n")

        print(f'Saved measurement data to {file_path}')

        # データをクリア
        self.measure_data_37 = []
        self.measure_data_38 = []


def connect_port() -> Monitor:
    while True:
        ports = list_ports.comports()

        if not ports:
            print("No device found.\nRescan in 1 second...")
            sleep(1)
            continue

        print("Select open port.\nInput index number.")
        for i, device in enumerate(ports):
            print(f"{i + 1} : {device}")

        try:
            inpt = int(input(">")) - 1

            if inpt > len(ports):
                raise IndexError

            connect = serial.Serial(ports[inpt].device, BAUDRATE)

            if connect.isOpen():
                print("Port open.")
                return Monitor(connect)

            else:
                print("Open failed.")
                continue
        except ValueError:
            print("Input index number.")
            continue
        except IndexError:
            print("Invalid value.")
            continue
        except serial.serialutil.SerialException:
            print("Access denied.")
            continue
        except Exception as e:
            print(f"Unknown Error.\n{e}")
            continue


def main():

    monitor = connect_port()

    # メインループでのコマンド受付
    while True:
        try:
            command = input(">")

            if not command:
                continue

            monitor.send_command(command)

            if command == "exit":
                monitor.end_polling()
                exit(0)

        except:
            monitor.end_polling()
            exit(0)


if __name__ == '__main__':
    main()
