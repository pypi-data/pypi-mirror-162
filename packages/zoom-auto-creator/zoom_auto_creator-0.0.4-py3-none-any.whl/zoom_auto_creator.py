import ctypes
import os
import sys
from datetime import datetime
from getpass import getuser
from pathlib import Path
from re import search

import pyautogui


class UkrainianWriter:
    __path = Path('text.txt')
    __notepad_butt = 'buttons/8.png'

    def __init__(self, ukrainian_text: str):
        self.__text = ukrainian_text

    def copy_ukrainian_text(self):
        self.__write_text_into_file()
        self.__open_file_by_notepad()
        self.__copy_text()
        self.__close_notepad()
        self.__delete_text_file()

    def __write_text_into_file(self):
        self.__check_file_exists()
        with open(f'{self.__path}', 'w', encoding='utf-8') as text_file:
            print(self.__text, end='', file=text_file)

    def __open_file_by_notepad(self):
        os.system(f'start notepad {self.__path}')

    def __copy_text(self):
        self.__find_butt(self.__notepad_butt)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')

    @staticmethod
    def __find_butt(butt_name: str) -> None:
        while True:
            butt_cord = pyautogui.locateOnScreen(butt_name)
            if butt_cord is not None:
                break

    @staticmethod
    def __close_notepad():
        pyautogui.hotkey('alt', 'f4')

    def __delete_text_file(self):
        os.remove(self.__path)

    def __check_file_exists(self):
        counter = 0
        while True:
            if not Path(self.__path).exists():
                break
            counter += 1
            self.__set_path(f'text{counter}.txt')

    def __set_path(self, new_path):
        self.__path = Path(new_path)


class ScheduleParser:
    __dir_path = Path('Schedule')
    __file_name = 'Schedule.txt'

    def __init__(self):
        self.__check_directory()
        self.__check_file()

    def __check_file(self) -> None:
        full_file_path = 'Schedule/Schedule.txt'
        list_dir = os.listdir('Schedule')
        if self.__file_name not in list_dir:
            with open(full_file_path, 'w') as _:
                pass
        if not os.path.getsize(full_file_path):
            pyautogui.alert(f'1. Here is an empty "Schedule.txt" file.\n'
                            f'2. Fill "Schedule.txt" file with your info.',
                            title='ATTENTION')
            self.__exit()

    @staticmethod
    def __check_directory() -> None:
        if not Path.is_dir(ScheduleParser.__dir_path):
            Path.mkdir(ScheduleParser.__dir_path)

    @staticmethod
    def __get_full_list(list_to_validate: list[str]) -> list[str]:
        return [row.strip() for row in list_to_validate
                if ('Інд' in row or 'Ст' in row)
                and '-' in row and ':' not in row]

    def __get_list_by_day(self, data_list: list[str]) -> list[str]:
        result_list = []
        week = {
            0: 'MONDAY',
            1: 'TUESDAY',
            2: 'WEDNESDAY',
            3: 'THURSDAY',
            4: 'FRIDAY',
        }
        weekday = week.get(datetime.now().weekday())
        if weekday == 'MONDAY':
            for row in data_list:
                if 'пн' in row or ('ср' in row and row.startswith('Ст')):
                    result_list.append(row)
        elif weekday == 'TUESDAY':
            for row in data_list:
                if 'вт' in row or ('чт' in row and row.startswith('Ст')):
                    result_list.append(row)
        elif weekday == 'WEDNESDAY':
            for row in data_list:
                if 'ср' in row or ('пн' in row and row.startswith('Ст')):
                    result_list.append(row)
        elif weekday == 'THURSDAY':
            for row in data_list:
                if 'чт' in row or ('вт' in row and row.startswith('Ст')):
                    result_list.append(row)
        elif weekday == 'FRIDAY':
            for row in data_list:
                if 'пт' in row:
                    result_list.append(row)
        else:
            pyautogui.alert(f'1. It\'s holiday today.\n'
                            f'2. Run program not on holiday.',
                            title='ATTENTION')
            self.__exit()
        return result_list

    def __get_all_rows_from_file(self) -> list[str]:
        file_path = self.__dir_path.joinpath(self.__file_name)
        with open(file_path, encoding='utf-8') as text_file:
            return text_file.readlines()

    @staticmethod
    def __get_sorted_list(list_to_sort: list[str]) -> list[str]:
        list_to_sort = list(set(list_to_sort))
        pattern = r"[0-9]{2}-[0-9]{2}"
        list_to_sort.sort(key=lambda row: search(pattern, row).group())
        return list_to_sort

    def get_schedule_list(self) -> list[str]:
        all_rows = self.__get_all_rows_from_file()
        full_list = self.__get_full_list(all_rows)
        list_by_day = self.__get_list_by_day(full_list)
        sorted_list = self.__get_sorted_list(list_by_day)
        return sorted_list

    @staticmethod
    def __exit():
        sys.exit()


class ZoomStarter:
    __butt_1 = r'buttons/1.png'
    __butt_2 = r'buttons/2.png'
    __butt_3 = r'buttons/3.png'
    __butt_4 = r'buttons/4.png'
    __butt_5 = r'buttons/5.png'
    __butt_6 = r'buttons/6.png'
    __butt_7 = r'buttons/7.png'

    __schedule_without_free_rooms = ScheduleParser().get_schedule_list()
    __free_rooms = [f'Вільна зала {i}' for i in range(1, 5)]
    __schedule = __schedule_without_free_rooms + __free_rooms

    __schedule_len = len(__schedule)

    def run(self):
        CreateImages().create_buttons_images()
        self.__check_language()
        self.__start_zoom()
        self.__start_conference()
        self.__create_rooms()
        self.__fill_info()
        self.__open_rooms()

    @staticmethod
    def __start_zoom():
        os.system(rf'start C:\Users\{getuser()}\AppData\Roaming\Zoom\bin\Zoom.exe')

    def __start_conference(self):
        self.__click_butt(self.__butt_1)
        self.__click_butt(self.__butt_2)

    def __create_rooms(self):
        self.__click_butt(self.__butt_3)
        self.__click_butt(self.__butt_4)
        self.__click_butt(self.__butt_5)
        self.__enter_count_of_rooms()
        self.__click_butt(self.__butt_6)
        pyautogui.moveTo(1, 1)

    @staticmethod
    def __find_butt(butt_name: str) -> tuple:
        while True:
            butt_cord = pyautogui.locateOnScreen(butt_name)
            if butt_cord is not None:
                return butt_cord

    def __click_butt(self, name: str):
        pyautogui.sleep(0.25)
        pyautogui.click(self.__find_butt(name))

    def __enter_count_of_rooms(self):
        pyautogui.sleep(0.25)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.sleep(0.25)
        pyautogui.write(f'{self.__schedule_len}')

    def __fill_info(self):
        for i in range(self.__schedule_len):
            UkrainianWriter(self.__schedule[i]).copy_ukrainian_text()

            pyautogui.press('tab')
            pyautogui.press('down')
            pyautogui.press('tab')
            pyautogui.press('enter')

            pyautogui.hotkey('ctrl', 'v')

            pyautogui.press('enter')

    def __open_rooms(self):
        self.__click_butt(self.__butt_7)
        pyautogui.sleep(0.25)
        pyautogui.press('escape')

    @staticmethod
    def __check_language():
        while True:
            current_lang = LanguageChecker().get_keyboard_language()
            if not current_lang.startswith('English'):
                pyautogui.hotkey('alt', 'shift')


class CreateImages:
    __folder_name = Path('buttons')
    __img_1 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01&\x00\x00\x00-\x08\x06\x00\x00\x00\x03t\xc6\xad\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x07\x97IDATx^\xed\x99On\xdc:\x0c\xc6\xdfYz\x82w\x92\xac{\x8e\x00Y\x15=Av]f\xd3\xcdlz\x86 @\xce\x10\xa0\xdb\xa0\xdb\xf4\x12~\xa6mY\x14ER\xd4LfFy\xf9~\x80\x01\xcb"%\xea\x0f?k<\xffL\x00\x000\x18\x10&\x00\xc0p@\x98\x00\x00\xc3\x01a\x02\x00\x0c\x07\x84\t\x000\x1c\x10&\x00\xc0p@\x98\xae\xc5\xeb\xcf\xe9\xe6\xcb\xbf\xd3\x17\xe5\xba{\xdal\x12\x95\xed\xf7I\x9a,(mVmY\x84|\x9f\xa7;aS\xc5\xe2\x8ck\xbf\xee\x9e7c\xc1\xb1\xbe\xbb\xdf\xd7\xe9\xe1u{\x96p\xda,\xc7\x17\x18\x1b\xb8\x18\x10\xa6k\xf1\xf4]$A\xbex\xc2\xbc>|Um\xaa$t\xda\xbby\xf8\xb3\x19\x19\x04}\xedXX\x02\x07\xc4\xc5\x8c\xa7\xdbW\x8a\x89"L\'\xcf3\xc4\xe9\x1a@\x98\xae\xc5\x9e0\xde\xc6\xe7\x89\x97\xec\xd8\xb3\x9b\x9f\xd3\x9a\x87\x7f\xa6\x87\x1bi\xa7=\xd3\x88\xfb\xbe>|/\x12\xff\xe9.\xd9\xb4Of9\xf1\xbdXtT_Up<a\xf2\xfb=el\xe0\xfd\x810]\x89=\xd9vqQ`\xc9\xa7\x9f\\R"2\xb1b?ubbp\x82/\x8b\xcfM^v\x12j\x9e\xde$\x96\xef\xd67=\xcb"R\x0bSh\x9e5\xa2c\x03g\x01\xc2t%\xdeG\x98r\xd2\xec\xc9\xc9\xda\xd3\x9ei\x1c\xe7\x1b=\x91\xb1\xb6\x1av\x1a\x11\xdfl\xf3^\xc2\x14\x1f\x1b8\x0f\x10\xa6+\xc1\xc5%_"\xb1\xf87\x97=\xb1x\xd2p\xc1\x92\xdf[\xd2\x15I\xac\xb8o\x16\x01\xdb\xa6\x80\x8f\xc1\xfa\xe8m\x11\xf4\r\tSq\xd5vD\xf7\xd8\xc0\xd9\x800]\x89:\t\xf2\x95\x7f:\x94"\xa4]\xfc$\xa5\xb6\x19<)D}U;G4\xb20\xe8b\xe0\x11\xf5\xcd1\xd5v\xb1y^\xe9\x1d\x1b8\x1f\x10\xa6A(\xde\xecB\x10\xca\x84\x99\xdf\xe2\xd5\xf7\x0f.`[r\xaa\xa7-\x8d\xe3}y\\\xc5\xf7\x9f\x1d\xedC}\x94\xb8\xaf\'L\x12o\x9e9\xed\xb1\x81s\x02a\x1a\x86\xf8w\x8d\xea$a}\xa8\x8d|\xc0=\xc5\xb7%\x1e\xac\x8d\xee\xe4\xee\xf0\xed\x11\xa6\xf8<\x9f"\xaa\xe0T L\xc3\xc0\x12\xc6M\x04\xc5\xce\x12\x11v\xf21\x93\xfb\x14\xdfF\xf2\xf6\tFI\x8f\xef\xd1\xc2\xe4\xce3\x84\xe9\x9a@\x98\xae\xc2\x9c\x1cw\xe5f/~b\xb0\xef\x1aOO\xe57\x0e\xfe\x13c\x17\x12\xe3#\xb1j+\t\xfb\xce\x89*\x12\xd4\x8ay%*\x00\x1a}\xbe\xb60E\xe7\xb9wl\xe0\xdc@\x98\xae\x02K\xbc\xea*\x7f^p\x81(.\x91,\xa6\x1d]\x8d\xc4\x8a\xf9\xb2\x13Du)?\x89\x0c\xc1\x0b\xd1\xe9\xeb\nSh\x9e;\xc7\x06\xce\x0e\x84\xe9J\xa8b\xa0$\xa1fg\x9e~\xd8\xcf\xb2\xa6\xad$\xe0\x1b\x8dy\xa1\xe3\x1bQE\xa7\xaf-L\xf1\x98\xbb\xc6\x06\xce\x0e\x84\t\x000\x1c\x10&\x00\xc0p@\x98\x00\x00\xc3\x01a\x02\x00\x0c\x07\x84\t\x000\x1c\x10&\x00\xc0p@\x98\x00\x00\xc3\x01a\x02\x00\x0c\x07\x84\t\x000\x1c\x10&\x00\xc0p@\x98\x00\x00\xc3q\x19az\xf95\xdd\xde?OoK\xe1\xf7t\xb8\xfd1=\xae\x85\x8f\xc1G\x8f\x1f\x80\x0f\x86"L\x94x\xdf\xa6\xdb\xc3\xef\xad\xac@\x89\xda\x99\x9c/\x87\xb9Mjw\xbe\x0e/\xdb\xc3\x0f\xc4G\x8f\xbf\x06\x02\x1b\xe7s\xce\xd5\xdb\xe3\x8fM\x076M\xd8/>\x17\xbdzA\xf6\xbf&J\xa1%\xa7\x0c?C\x98~L\xf7\xf7\xd6B\xfc\x9d\x1e\xe7:\xbb\x1e|\x0c>g\xb2\x1d\xc7\'\x9c\xab\xb7\xe79\xc7\xf5_\t\x8b`\x89\xba\xb8^\x90\xfd*L\xa9N\xf33\x85\xe9pHjYBA\xdd?>W\x0b\xc5O\x149hB,j\xf3\xb4E\xc1\xb2\xb6v[\xaf\x1dQW\x94{\xea\x12\x8e\x8d\x1b\x7f\xdbvY\xd4jl\x04\x1f7\x7f.cLe9O\xc9\xaf\x15\x83\xe6\x976\n\xe1\xf9\x97u\xeb\x9ao\xbe\x8b]ns=UZ1R]\xf2\xdf.m\xcf\xbc\xcc\xc9\xb1\xfb\xf1\x18%N\\{y\xbb\xbc\xbdY\x95[sE4\xd6\xcd\x1dC\xc3W-\xd3=o\x87\x97\x85\x9f\xb3v\xda\xde\xe4\xd0\x9c\xdd?\xfe\xddJ\xc2\xb7(\xaf\xf7q\xbd {\x16?\xc5\xa1\xf8\x99\xc2Tm\xf0\x05\xbd\xaeT\xd0m#\xec\x9dq\xdby!\xe6\x01\xdcW\xedr\xb8\xbdu/\xdb)\xe3\xb1\xfd\x08\xaf.a\xd9\xb4\xe2o\xdb\xd2\xdc\xacI[\xf6]\xcc\x99\xf3\xb6\xea+\xd71\xe4~\x98\xdd\xb2I\xb5\xcdm\xcfs\xb9\xe6d\xc7\x12\xbeh\x8f\x901F\xf6\xcc\\f\xf5\xd2\xbe\xc4\x8a+\xd2\x0f\x8f\xab,\xb7\xe7J\xb4W\xad\x9b?\x06\xdf\xd7\x8a\x8b\xee\xe5\xdc\xf6\xad\x9d\xb573s}q\x92\xe1\xbe\x04/\xa7{iChut\xcf\xe2/\xc6\x9dq\x84i\x9b\xc8}\x11yYv\xa4\x05\xa4L\xd6\xbc\xa8\x87\x17\xcd\x9ec\xf8\xba\xed\xc86\x8f\xadK\x186\xcd\xf8[\xb6|\xc1\x8d>\x16,;\xa2\xa3\xec\xce\x13\xbf\xa7\xfe\x14\xc1\xb4\xfc\x1f\xa5\xf0H\xb8\x0f\xd1*\x13\xf4L[\xf7\x84\xf6,\xb1\xd5Uq\xf5\xf6\xc3\xcb\xd6\xbd1W\x0b\xde\xba\x11V\x9bDt\xcd\xe9^\x8eQ\x19\x8f\xb7\xf6\xa1}l\xcfc)\xb0\xb9.\xae\x17V\xfc\x19W\x98\xe2\xf7\xb2a\xcd\x96&\x9e\xecx\x9d\x82\xf9\xe6\xf0\xda\xe1\x9b\x85\x90~\xf3\x9b\xa9\xb8\xec\xba\xf5\xf8*\xfd\xad~%-[*\xa7\xb9\xe2ut_\xc6\xe1\xc5\x18;\xf6+1\xd0\xdc\xaa\xfd\xcf{u~{\x97c\xd7\xc6@\xf7k\x0cy\xaeW\x96M\xd8\x15c\x8a#!\xfb\xe1\xf6\x04\xc5#\x9f%\xac\xb8"\xfd\xf0\x98Y\xdc\xe1\xb92\xfc\x85\xcf\n\x1fC\xcb\xd7\xab\xe3c\xe2\xe5\xd4\xa7\xb5vV\x9d\xa0:\xc5\x90-\x8fE\xf6/\xfbh\xdds\x7f}]\x1b\xc2\xb4m\xb8Y\xf5J5\xb4:M\xf0\xce\xb7\xfa\xf9mV\'}M\xb3\x1f\xab\x9d\xf9-`/$\xefOi3\xd5-\x9b\x91\xca\x8aM(~\xdf\x96\xc6\xb6>\'\x94>\xbc6\xf7\xba`Y\x8d\xc1\xba\xa7\xcd!N\x01\x9e\xff\xf2\xdd$=\x9b\xa1\xb9\xaf62\xabo\x96\tz&\xf6\x8cY/\xd9\xece\\\xdd\xfd\xf0\xb2u\xaf\xccU\xd1~B\xab\xa3g\xde\x18\x13\xb2\x8e\x97y\x1b\x84\xd2\xa6\xb7v\xe1},\xfb\xf0ls]L/\xac\xf83MaZ\xcb<\xd1\x89\xd2f\xf9\xad\xcc6f\xf1\xdby\xf7\x17\x93\xb7\xb7\xc5\xe1\x8bNp\xdb\x9ev\xa4\x1f\xb7s\xeaLa\xea\xe9\xd7\xb2\x95~e\xb9\x9c3\x8e\xef\xa7\x97\xedxs?\xec\xf9"\xea\xdc>0\x86\xc5\x87\xdd\xb3\xf5_6%\xebS\xc6@\x84\xf6\x0c\x9b\x0f{~\x08#.*6\xfb\xb1\xe3\xcc\xb6\xb2\xfd47\xb2=N{\x0c\xbe\xaf\x15\x17\xdd\xe7\xfe\xcb\xf2\xd6\xa7\xb9vV\x9dD\x9eb<[Y\x97\xfa\xb1\xfc\xe9\xde\x8a?\x13\x10\xa6\xac\x82\x99\xdaf\x99\xe4%\xa0\xf9\xaa\xde\x9e\xde\x17\xfe\xc4*J\xb5/\x1fP\xa4\x1dB\xfaq\xbb\xbaM~\xd2\xd2\xdf4=\xfdj\xb6\xebs\xdeO\xbe\xe4\xa6\xda\xae}\x1ed\x7f\x91\xb2\x17\xef6\xcf\xbc\xaf\xb0\x7f\xd9\xd6*@\xf4")\xdb\xac\xff\xb5\x951\xac\xf8{f\xb6\x9f\xdf\xeez\xbd\xc4\x8ak-7\xfb\xd9\x1f\xc8rk\xae\x08\xf2a\xf5r\xdd\xdc14|wc^\x16>\xe9Z\xf2s\xad\xb3\xd7\xce\xdb\x17%4g\xfa\x01AR\xd7\xf9zA\xf7L\x88H\xe8\x15qV\x84\t\xbc?b1v\xac\xe7\x97\xa0\xdeP\xe30Zl\xc7\xc4s\xc11\x18\xc9}\x12\xd5w\xa6s Of\x19\x08\xd3E\xb0\x04\xc8z~\tFK~\xceh\xb1\x1d\x13\xcf\x05\xc7p\x0ea\x9a\xa9O>\xef\x8b\xfdS\x16\xc2\xf4\x89\x810\xc5\x19\\\x98\xfe\x87@\x98\x00\x00\xc3\x01a\x02\x00\x0c\xc64\xfd\x07xFP8\r\xd7\xf3\r\x00\x00\x00\x00IEND\xaeB`\x82'
    __img_2 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00A\x00\x00\x00\x17\x08\x06\x00\x00\x00T "\xaf\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x01\x05IDATXG\xed\x93\xcd\r\x830\x0cF;Awb\x9e\xdeX\x83#+\xb0\x04b\x15\x16\xe0\xc0\x01q@HH\xae\xf3\x03$&\x84\x80R\x89\xb6\xfe\xa4w\xc0I\x8c\xf3Z\x1e\xcf\xb4\x85\x7f\x87% ,\x01a\t\x08K@\x02$t\x907 S\x16d\xad\x18\xd5B3@b\xd6\xbf\x0c\x96\x80\xb0\x04$\xb2\x84u\xef\x9a\x11^\x01\xfbUo\xdf\xf9\x1eJ]\xb1#\xd6\xe7\xb5\t\xf2L\xbf\xeb\x04\xa7$\xec\xc6+AD_\xe4\x92\x04\x11\xf3\xa24\xb7\x93@!\xc3\x1dJ\xa0\xb8.\x17Z\x0b\'\xf2\xe70\x0fCC$\xd0\x7f\x06F\xf5>8o\xbd\xc3U#\xd9\xfdql\xa2JH\xaaI>\xd6U\xa7\xd6\xb3\x01jY\xd1\x03/\xcf\xdb\x88\xde\x87\xe7\xe5{}\x12\xe6\xda:\xf3\xd2\xcb\xc3G$,i\xa6\xcd%\xcc=u\xd5[\xbdC\xce\xdf^\x82\xb9W\r\xe4\x1a\xd8\x84\xf6\x0e9\xef\xab\x91\xc4\xfb\x1c~\x1f\x96\x80\xb0\x04\x84% ,\x01a\t\x08K@XB\xda\xc2\x1bw\x83j\x0f\xed\xc1\xd5\x15\x00\x00\x00\x00IEND\xaeB`\x82'
    __img_3 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x1c\x00\x00\x00\x1e\x08\x06\x00\x00\x00?\xc5~\x9f\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\xbfIDATHK\xed\x941\x0e\xc3 \x10\x04\xf3\x0e>\x06|\x0e((\xf8%\xd1\x15\x1b\xed\xd9\x10l\t\x119\xa2\x98\x06/;\x92u\xc7\xcb\x18SW\xb2\x85\xd3QB\xe7\\M)\xd5R\xca\t9\xf7\xde\x7f\xb2\xd6\xda\xafY\xe9\xe2n\xa0\x841\xc6f\x01\x90"dC\x08\xcd\x0c\xe0,\xa3\x84\xad\x8bG\x90\xcd97\xbf3\xdc\r\xb6\xf0\x04\xb2\xcf\x14\xf6\xc6\x1c\xdc\x99R\x99x\xee\x06J({\xd6\x93\xca9\xef\xe1\x9d\x9de\x94p\x05\xbf\x15\x8e~\x93<gW\xb3S\x9e6\x19\x14d{2 \xdf\xb9\x1b(a\xeb"#\xabp5+p7\xd8B\xc5\xf3\x85\xa3\xc9\x9b>\xa5\xa3\xa7\x8dw\xeb\xce3\xc8(\xe1\n\xb6p:\xff.4\xf5\r\x93nM\xa1\xdc\xaen\xe0\x00\x00\x00\x00IEND\xaeB`\x82'
    __img_4 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00z\x00\x00\x00\x13\x08\x06\x00\x00\x00_\xa2\x19v\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x02\x18IDAThC\xed\x95\xcd\x8d\xc4 \x0c\x85\xb7\x96\xa9`+\xc9y\x1a\xc9q\x1a\xc9e*\x19i*\x89\xa6\x13\x96\x07\t\xd8\xe6\'&\x9b=\xac\xe0\x93"%`\x1b\xdb\x0f\xc8\x97\x19t\xc1\x10\xba\x13\x86\xd0\x9d\xb0\t\xfd6\xf3\xedn\x96\xd5\x7fEJ\xe3\x83\xff\xc6\x10\xba\x13\xda\x84~=\xcc\xed\xf6\x1d\x9e\xf9\x95\x1f\x9f\x96\xcf6!\xe3*\xe3\x9d\xf2\xfb\x98e\x8ac\xfe\x81\x8f\x8cU\x03\xb6<FR\xcb\xebi\xa60\xff0\xa1\x053\xb5\xb5 \xc7\xe9i\xd6j-\xe59}<o\x1brv6)\rB\xdbF\xce$\x88kv,4\xb0\xa2\x11\xfbx\xb9\x90z\xbc\xb3~\xa0\xe6{\x84\xb0Mj\xe1\x8d\\\x97{\xfcF\x1e\xf3\xdb\x8d\x83(T-\x9f\xca\x9c2\x1e\xcb\xc1\xe2D\'~;Dh\xb2+\xd8C\x13\xa1\xc8$7\xd0\x9c\xb0p\xa5\x90\x04:w\xd6\x0f\xb4\xf8J\x84m\xb5\x16@\xc7\xf0\xbeo\n\xdc.\x9aM{4w\x14\x0f\xe3\xf4&\xb4\xb0\xcd\x19i\xba\xba\xdd\xee)m\x02w\xb20F\x17\x81?\xb5\xe7>\xe5x\xb2\x80\x86<\x92Z\xd2\x1c\xd8\x95\xc8\x90\xb6\xb2\x16\x1a\x17 \xcf8\x86\xd3\xe4rF\xb3\xc3\xa9\xaa\xd5\x92\xe6Fk\xc9\xc7\x93>2\xa7\\\x9e-BCHrE\xa8|\x12\x9b\x86xa\xe3\x88\x82\x0e\xf3h\xfd\xa6\xd4ls~\x18#\x9b\x01\xb9YA\xb0\x11\xd9)+\xd5R]\xcf\x92\x8dGm\xfe\xe2D\x8b\x06\xfbSu\xe0\x93\xc4=\x13\x0f\xb4\xf8U\xd6\x04\xae\x11\x8au\x1c\xf4\x1b\xefV$\xf2\xffK\xff\x87\xd6\xc6^\xb1xd\xa3#2fi=\x90\x8b\xc7m\\\x0e\xa4\x1f\x8a\x7f4]`\x87\x8e\xfb\xdd\xb3\xef\xcaiy\x869\xdfl:\xb7_\x8d\x99\xc4\x15\xf1RZ\xfcrkF{\xef\xa3\xbd\xba3\xb5,\xe4t\xb2\x9b\xc5Sjt\x84\xe6\x97\xcb\x95~\x176\x13\xb3\xe1\xfd\xc8\xe5\x046\xa1\x07\xc7\xa4"\xe4\x800\xec*\xfd%W\xc5\x1bB\xabQ\x08]\xf8?\x9e\xe6\xc2xCh5u\xa1\xdd\x15\xab8\xf1Z\xae\x8e7\x84\xee\x84!t\'\x0c\xa1;a\x08\xdd\x05\xc6\xfc\x00\x87\xff\x12J\xf75\xeaM\x00\x00\x00\x00IEND\xaeB`\x82'
    __img_5 = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00+\x00\x00\x00\x12\x08\x06\x00\x00\x00\xc2('\xa5\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\xa3IDATHK\xed\xd5\xc1\t\xc3 \x18\x86\xe1\xce\xe2\x04\x9d\xa4\xe7N\xe0\x06=f\x06\x05=\xb9\x80\x8e\xd1IB\x87\xd0\x9b\xf2\xb5\xbf\xb4`\x03\xa9\xd0b0\xc5\x07\xc2\xcfw{\x0f\x01\x0f\xd8\x91\x11\xfb\x8b\x10\x02\xb4\xd6\xf9.u\x15\x9bR\x82\x94\x12\x9c\xf3|i\x97*\xb1W\\\xd8\x11's{\xee\xb6\x9cs9\xf4\xf5\xd1.\xad\xc6\xce\xe6\x0c\xc6&\x98\xc7\xdd*\xb6\xa6\xfa\x1bP\xf4\x88\xfd\xc2\x88me\xc4\xb6\xf2_\xb1[\xb2\xd6\xbe=\n\xb4K]\xc5\xc6\x18!\x84\xc8\xa1\xf4\xdc\xd2.u\x15K\xbc\xf7PJ\xe5\xbb\xd4]\xec';\x8a\x05\xee\x02\x05\xd7]\xfe\x86k\xda\x00\x00\x00\x00IEND\xaeB`\x82"
    __img_6 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00C\x00\x00\x00\x17\x08\x06\x00\x00\x00P\xd5\xf2\x92\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x01iIDATXG\xed\x96A\x8e\xc20\x0cE\xe7\x04s\'\xce\xc3n\xae\xc1\x92+\xf4\x12\x15\xb7`\xcd\x05\xba`\x81X \xa4J\x9e4\x8d\x93/\xc7q\xab\xd1 @\xf8K\x7fA\x9c:\xf1s\x9a\xf2\xf5\xfds&\xf7l\x87\x01v\x18`\x87\x01v\x18\xe0U06\x87\x91\xa4N\x87\x8b:\xf7\x9d\xbd\x00\xe3J}*^\xea\xc3`\\h?\xa4\xcai\xa4\xfd\x0eb\xbb\x1b\xf5\x1f\x05#\x14|\xd2@(\xde\x1e\xe3\xc4\xa2\xe3\x15\xe2\xf5\xe9\x92\xa7\xaaz>\xa8\xcc\xc1\xa6\xb0\xee\xb4m\xe4\x9e5\xc59\xb6\xbc\x7fv\x1bFw\x8f\xa9h\xb8\xd1F\x8bGk\x1bM\xca\xcfi\x1b\xc6\r\xea9l\x18\x93\xb0`\xa9\x7f\x86\x91/M\x0b\x06\x03\xc3\x05\xf3\x89"\xea;\x98\x1b\xcd\x1b\xe4\xce\xca\xb1Rx\xfbN\xd2\x8a\\;f{\xf9d\x18\xc9t`\xa5\xa0\x0c#\xe7\n\x92p9\x16_-\r\x06\x17%\xb5\x16\x86\x90\xd1\\\xe3\x02\xc5d\xd8\xc9`\xbe@s\x91\x107\xef\x1a.\x96c\xad\xdf\x05\x06\x03\xcfp\xd4\xfc\x16\x8cvni\x03F0vThNX\x16\xa8\xc4\x1dh\xe4\xe8;\xe3\xd9\xa4i\x8d\xea?\xce0>\tF4\x9e\x10\x16.\xaa\x14\x85_\x13\x05\xc6"\xc8\xa4z\xde\xb4\xee\x9a\xc2qL\xe8o\xaf\xc9\xa3\x9d\x8a\xd46\x97\x00\xb6:\xf8(;\x0c\xb0\xc3\x00?\x11\xc6\xeb\xd9a\x80\x1d\x06\xd8a\x80\x1dF\xf6\x99~\x01t\xa2\x11b \x82\x079\x00\x00\x00\x00IEND\xaeB`\x82'
    __img_7 = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00:\x00\x00\x00\x0f\x08\x02\x00\x00\x00:nKa\x00\x00\x00\tpHYs\x00\x00\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x02\x1eIDATH\x89\xd5U1k\xdb@\x18}\xf6\t\x1f\x08d\x110U\xc8\xaa\xc5\x04\x04E\xfe\x07\xc6qi\x86\x0c\x85l\xf6\x90\xfd\x96\x88@\x0b\x9e\x03\r\x18u\xd1\x96\xa1\x83\xbd\x05:tH\xa9k\xfc\x0fl\n\x82\xd2\xc5\xab\x89\x12\x81Q\x05\x82\x0b\x11t\x90d\xcb\xa9m\xb5\xc5\xd4\xcd\x9b\x8eO\xa7w\xef\xfb\xbew\xdf\xe5\x8a\xa7wx:\x10RkzeJ\xf5x\x1dZ\xedik\xb2\rEk\x91\x8b\xab\xabK^\x83>\xfa6\xeeO\xf5\xebp\x0b\xa2V#\x0f\x00\xa0W\x91V\xdb\x97\rW6\xdcj?\x04\xa0\xd6\xc4\xe66\xb5-\x81\x00\x00z\xa1\x0e\x00\x9c\xbd\xe7Qtx\xfd\xc3\xd2v\x98B\x8f\xf4\xa0|\xb0\xc3\x94\xd4\x1f\xb6/\x7f&\xa33Qu\x82\xeaE\xb0\x7fR\xb24\xc0\t\xaa\x1d\\F\xc1/d\xd0\xa0\x987'\xf2\x18g\x86\xdf\x99\xb3\xcc\x82A\xf9\xf5:\xfe\xe1\xa2\xdc<\x80\xca\xae\x00\x00\xf6}\x8a.\xfc~\x0b\x00\xea\xae\x805\xd0%K\x03\xc0\xd9\x9c\x97^&\xa6Rk\xc5\xf3\xbd\xec\x82\xfd\x11\xf2Y\x1b\x1eZ\x17\xael\xf8=\x00\xe0\xccp\xe5\xa4\x03\x00ys@\x01\xf4\xba\xa9\xb2)\xf8\xd4ve\xc3e6\x00\xf2\xf29\xc9\xe2\x0fW\xf3/\x81\x00`x\xf3\x00\x10h\x85&xr0)?\x03\x80\xf1\xcd\xea\xab\xa6\xd0\xc8B\x1fG\xa9\xa0\xc3?L\x00\xe0\x9b\x13BKk\xa5\x96I-\x00\xb1I\xb2\xb2\x00\xa0\x88\x03S\x8cR\x9a\x8d\xa9<\x00\x8c\xee{\x11\xe3I\xdc\xc7\xcaa\x91)\xbfHy\x04\x87\xf7\x1c\x00\xf4\xf40%K!\xfb\x00@^i\x04\x0b\xd9rf\xc4U\xfc\xdd\x1b\xec\x04U\xc3\x95\xbb\x1c \xecE,,\xb2&?\xee\x16\xbc\x06\x85&y\xa64\xdb\xbf\xd0\xe5%\x08\xdfv\x02\xf5LTk\xc5\xf3\xaf\xd3V\x1c\x9cW1#\xdb\xbfB\xe2\xdd\x91/\xb7\x83qJ\x8a\xd5v\x8f3\x0f\x9b\x04\xefl\x00\x845\xc5J\x14q\x02\xd6\x0f\x13\x86\x85Q`\x99%\xcf\x94\xea\xd9UH\xa0\x88\x03\xb3\xe45hzd\xe56\xf6\x08\xef\x89\xab\xa6\xcf\x06\x919\x19\xfe/<1\xb9\x9b3\xc3?\xc1O\x15\xa5\xe5[\x0b\x8c4v\x00\x00\x00\x00IEND\xaeB`\x82"
    __img_8 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xc2\x00\x00\x00\xaa\x08\x06\x00\x00\x00\xffF\x90\x06\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x01\x80IDATx^\xed\xd3\x01\x01\x00\x00\x08\xc3 \xfb\x97\xbe\x0b\x02\x1d\xb8\x01\x13\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01"\x02D\x04\x88\x08\x10\x11 "@D\x80\x88\x00\x11\x01\xb6=\x8f\xd2j\xc0\xa7\xa8\xa4z\x00\x00\x00\x00IEND\xaeB`\x82'

    __images = (
        __img_1,
        __img_2,
        __img_3,
        __img_4,
        __img_5,
        __img_6,
        __img_7,
        __img_8
    )

    def __init__(self):
        self.__check_folder()

    def __check_folder(self):
        if not self.__folder_name.exists():
            Path.mkdir(self.__folder_name)

    def create_buttons_images(self):
        for i in range(len(self.__images)):
            with open(f'{self.__folder_name}/{i + 1}.png', 'wb') as img_file:
                img_file.write(self.__images[i])


class LanguageChecker:
    __languages = {'0x436': "Afrikaans - South Africa", '0x041c': "Albanian - Albania",
                   '0x045e': "Amharic - Ethiopia",
                   '0x401': "Arabic - Saudi Arabia",
                   '0x1401': "Arabic - Algeria", '0x3c01': "Arabic - Bahrain", '0x0c01': "Arabic - Egypt",
                   '0x801': "Arabic - Iraq", '0x2c01': "Arabic - Jordan",
                   '0x3401': "Arabic - Kuwait", '0x3001': "Arabic - Lebanon", '0x1001': "Arabic - Libya",
                   '0x1801': "Arabic - Morocco", '0x2001': "Arabic - Oman",
                   '0x4001': "Arabic - Qatar", '0x2801': "Arabic - Syria", '0x1c01': "Arabic - Tunisia",
                   '0x3801': "Arabic - U.A.E.", '0x2401': "Arabic - Yemen",
                   '0x042b': "Armenian - Armenia", '0x044d': "Assamese", '0x082c': "Azeri (Cyrillic)",
                   '0x042c': "Azeri (Latin)", '0x042d': "Basque",
                   '0x423': "Belarusian", '0x445': "Bengali (India)", '0x845': "Bengali (Bangladesh)",
                   '0x141A': "Bosnian (Bosnia/Herzegovina)", '0x402': "Bulgarian",
                   '0x455': "Burmese", '0x403': "Catalan", '0x045c': "Cherokee - United States",
                   '0x804': "Chinese - People's Republic of China",
                   '0x1004': "Chinese - Singapore", '0x404': "Chinese - Taiwan",
                   '0x0c04': "Chinese - Hong Kong SAR",
                   '0x1404': "Chinese - Macao SAR", '0x041a': "Croatian",
                   '0x101a': "Croatian (Bosnia/Herzegovina)", '0x405': "Czech", '0x406': "Danish",
                   '0x465': "Divehi",
                   '0x413': "Dutch - Netherlands", '0x813': "Dutch - Belgium",
                   '0x466': "Edo", '0x409': "English - United States", '0x809': "English - United Kingdom",
                   '0x0c09': "English - Australia", '0x2809': "English - Belize",
                   '0x1009': "English - Canada", '0x2409': "English - Caribbean",
                   '0x3c09': "English - Hong Kong SAR",
                   '0x4009': "English - India", '0x3809': "English - Indonesia",
                   '0x1809': "English - Ireland", '0x2009': "English - Jamaica", '0x4409': "English - Malaysia",
                   '0x1409': "English - New Zealand", '0x3409': "English - Philippines",
                   '0x4809': "English - Singapore", '0x1c09': "English - South Africa",
                   '0x2c09': "English - Trinidad",
                   '0x3009': "English - Zimbabwe", '0x425': "Estonian",
                   '0x438': "Faroese", '0x429': "Farsi", '0x464': "Filipino", '0x040b': "Finnish",
                   '0x040c': "French - France", '0x080c': "French - Belgium",
                   '0x2c0c': "French - Cameroon", '0x0c0c': "French - Canada",
                   '0x240c': "French - Democratic Rep. of Congo", '0x300c': "French - Cote d'Ivoire",
                   '0x3c0c': "French - Haiti", '0x140c': "French - Luxembourg", '0x340c': "French - Mali",
                   '0x180c': "French - Monaco", '0x380c': "French - Morocco",
                   '0xe40c': "French - North Africa", '0x200c': "French - Reunion", '0x280c': "French - Senegal",
                   '0x100c': "French - Switzerland",
                   '0x1c0c': "French - West Indies", '0x462': "Frisian - Netherlands",
                   '0x467': "Fulfulde - Nigeria",
                   '0x042f': "FYRO Macedonian", '0x083c': "Gaelic (Ireland)",
                   '0x043c': "Gaelic (Scotland)", '0x456': "Galician", '0x437': "Georgian",
                   '0x407': "German - Germany",
                   '0x0c07': "German - Austria", '0x1407': "German - Liechtenstein",
                   '0x1007': "German - Luxembourg", '0x807': "German - Switzerland", '0x408': "Greek",
                   '0x474': "Guarani - Paraguay", '0x447': "Gujarati", '0x468': "Hausa - Nigeria",
                   '0x475': "Hawaiian - United States", '0x040d': "Hebrew", '0x439': "Hindi",
                   '0x040e': "Hungarian",
                   '0x469': "Ibibio - Nigeria", '0x040f': "Icelandic",
                   '0x470': "Igbo - Nigeria", '0x421': "Indonesian", '0x045d': "Inuktitut",
                   '0x410': "Italian - Italy",
                   '0x810': "Italian - Switzerland", '0x411': "Japanese",
                   '0x044b': "Kannada", '0x471': "Kanuri - Nigeria", '0x860': "Kashmiri",
                   '0x460': "Kashmiri (Arabic)",
                   '0x043f': "Kazakh", '0x453': "Khmer", '0x457': "Konkani",
                   '0x412': "Korean", '0x440': "Kyrgyz (Cyrillic)", '0x454': "Lao", '0x476': "Latin",
                   '0x426': "Latvian",
                   '0x427': "Lithuanian", '0x043e': "Malay - Malaysia",
                   '0x083e': "Malay - Brunei Darussalam", '0x044c': "Malayalam", '0x043a': "Maltese",
                   '0x458': "Manipuri",
                   '0x481': "Maori - New Zealand", '0x044e': "Marathi",
                   '0x450': "Mongolian (Cyrillic)", '0x850': "Mongolian (Mongolian)", '0x461': "Nepali",
                   '0x861': "Nepali - India", '0x414': "Norwegian (Bokmål)",
                   '0x814': "Norwegian (Nynorsk)", '0x448': "Oriya", '0x472': "Oromo", '0x479': "Papiamentu",
                   '0x463': "Pashto", '0x415': "Polish", '0x416': "Portuguese - Brazil",
                   '0x816': "Portuguese - Portugal", '0x446': "Punjabi", '0x846': "Punjabi (Pakistan)",
                   '0x046B': "Quecha - Bolivia", '0x086B': "Quecha - Ecuador",
                   '0x0C6B': "Quecha - Peru", '0x417': "Rhaeto-Romanic", '0x418': "Romanian",
                   '0x818': "Romanian - Moldava", '0x419': "Russian", '0x819': "Russian - Moldava",
                   '0x043b': "Sami (Lappish)", '0x044f': "Sanskrit", '0x046c': "Sepedi",
                   '0x0c1a': "Serbian (Cyrillic)",
                   '0x081a': "Serbian (Latin)", '0x459': "Sindhi - India",
                   '0x859': "Sindhi - Pakistan", '0x045b': "Sinhalese - Sri Lanka", '0x041b': "Slovak",
                   '0x424': "Slovenian", '0x477': "Somali", '0x042e': "Sorbian",
                   '0x0c0a': "Spanish - Spain (Modern Sort)", '0x040a': "Spanish - Spain (Traditional Sort)",
                   '0x2c0a': "Spanish - Argentina", '0x400a': "Spanish - Bolivia",
                   '0x340a': "Spanish - Chile", '0x240a': "Spanish - Colombia", '0x140a': "Spanish - Costa Rica",
                   '0x1c0a': "Spanish - Dominican Republic",
                   '0x300a': "Spanish - Ecuador", '0x440a': "Spanish - El Salvador",
                   '0x100a': "Spanish - Guatemala",
                   '0x480a': "Spanish - Honduras", '0xe40a': "Spanish - Latin America",
                   '0x080a': "Spanish - Mexico", '0x4c0a': "Spanish - Nicaragua", '0x180a': "Spanish - Panama",
                   '0x3c0a': "Spanish - Paraguay", '0x280a': "Spanish - Peru",
                   '0x500a': "Spanish - Puerto Rico", '0x540a': "Spanish - United States",
                   '0x380a': "Spanish - Uruguay",
                   '0x200a': "Spanish - Venezuela", '0x430': "Sutu",
                   '0x441': "Swahili", '0x041d': "Swedish", '0x081d': "Swedish - Finland", '0x045a': "Syriac",
                   '0x428': "Tajik", '0x045f': "Tamazight (Arabic)",
                   '0x085f': "Tamazight (Latin)", '0x449': "Tamil", '0x444': "Tatar", '0x044a': "Telugu",
                   '0x041e': "Thai", '0x851': "Tibetan - Bhutan",
                   '0x451': "Tibetan - People's Republic of China", '0x873': "Tigrigna - Eritrea",
                   '0x473': "Tigrigna - Ethiopia", '0x431': "Tsonga", '0x432': "Tswana",
                   '0x041f': "Turkish", '0x442': "Turkmen", '0x480': "Uighur - China", '0x422': "Ukrainian",
                   '0x420': "Urdu", '0x820': "Urdu - India", '0x843': "Uzbek (Cyrillic)",
                   '0x443': "Uzbek (Latin)", '0x433': "Venda", '0x042a': "Vietnamese", '0x452': "Welsh",
                   '0x434': "Xhosa",
                   '0x478': "Yi", '0x043d': "Yiddish", '0x046a': "Yoruba",
                   '0x435': "Zulu", '0x04ff': "HID (Human Interface Device)"
                   }

    def get_keyboard_language(self):
        """
        Gets the keyboard language in use by the current
        active window process.
        """

        user32 = ctypes.WinDLL('user32', use_last_error=True)

        # Get the current active window handle
        handle = user32.GetForegroundWindow()

        # Get the thread id from that window handle
        threadid = user32.GetWindowThreadProcessId(handle, 0)

        # Get the keyboard layout id from the threadid
        layout_id = user32.GetKeyboardLayout(threadid)

        # Extract the keyboard language id from the keyboard layout id
        language_id = layout_id & (2 ** 16 - 1)

        # Convert the keyboard language id from decimal to hexadecimal
        language_id_hex = hex(language_id)

        # Check if the hex value is in the dictionary.
        if language_id_hex in self.__languages.keys():
            return self.__languages[language_id_hex]
        else:
            # Return language id hexadecimal value if not found.
            return str(language_id_hex)


if __name__ == '__main__':
    ZoomStarter().run()
