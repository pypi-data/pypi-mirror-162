﻿import tkinter.filedialog

from cm.terminal import Terminal
from tkinter import *
from gtki_module_treeview.main import CurrentTreeview, NotificationTreeview, \
    HistroryTreeview
from cm.widgets.dropDownCalendar import MyDateEntry
from cm.widgets.drop_down_combobox import AutocompleteCombobox
import datetime
from cm.styles import color_solutions as cs
from cm.styles import fonts
from cm.styles import element_sizes as el_sizes
from gtki_module_exex.main import CreateExcelActs


class SysNot(Terminal):
    """ Окно уведомлений"""

    def __init__(self, root, settings, operator, can):
        Terminal.__init__(self, root, settings, operator, can)
        self.name = 'SysNot'
        self.buttons = settings.toolBarBtns
        self.tar = NotificationTreeview(self.root, operator, height=35)
        self.tar.createTree()
        self.tree = self.tar.get_tree()
        self.btn_name = self.settings.notifBtn

    def drawing(self):
        Terminal.drawing(self)
        self.drawWin('maincanv', 'sysNot')
        self.drawTree()
        self.buttons_creation(tagname='winBtn')

    def destroyBlockImg(self, mode='total'):
        Terminal.destroyBlockImg(self, mode)
        self.drawTree()

    def drawTree(self):
        # self.tar.fillTree(info)
        self.can.create_window(self.w / 1.9, self.h / 1.95, window=self.tree,
                               tag='tree')


class Statistic(Terminal):
    """ Окно статистики """

    def __init__(self, root, settings, operator, can):
        Terminal.__init__(self, root, settings, operator, can)
        self.btns_height = self.h / 4.99
        self.name = 'Statistic'
        self.buttons = settings.statBtns
        # self.font = '"Montserrat SemiBold" 14'
        self.history = {}
        self.chosenType = ''
        self.chosenContragent = ''
        self.choosenCat = ''
        self.typePopup = ...
        self.carnums = []
        self.filterColNA = '#2F8989'
        self.filterColA = '#44C8C8'
        self.tar = HistroryTreeview(self.root, operator, height=28)
        self.tar.createTree()
        self.tree = self.tar.get_tree()
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        self.posOptionMenus()
        self.calendarsDrawn = False
        self.btn_name = self.settings.statisticBtn
        self.weight_sum = 0
        self.records_amount = 0

    def excel_creator(self):
        file_name = self.get_excel_file_path()
        data_list = self.generate_excel_content()
        self.form_excel(file_name, data_list)

    def generate_excel_content(self):
        items = self.tree.get_children()
        data_list = []
        for item in items:
            record_id = self.tree.item(item, 'text')
            data = self.tree.item(item, 'values')
            data = list(data)
            data.insert(0, record_id)
            data_list.append(data)
        return data_list

    def get_excel_file_path(self):
        name = tkinter.filedialog.asksaveasfilename(defaultextension='.xlsx',
                                                    filetypes=[("Excel files",
                                                                "*.xls *.xlsx")])
        return name

    def form_excel(self, file_name, data_list):
        inst = CreateExcelActs(file_name, data_list, self.amount_weight)
        inst.create_document()

    def OnDoubleClick(self, event):
        ''' Реакция на дабл-клик по заезду '''
        item = self.tree.selection()[0]
        self.chosenStr = self.tree.item(item, "values")
        self.record_id = self.tree.item(item, "text")
        self.draw_change_records(self.chosenStr)

    def draw_change_records(self, string):
        self.parsed_string = self.parse_string(string)
        self.orupState = True
        btnsname = 'record_change_btns'
        record_info = self.history[self.record_id]
        self.initBlockImg('record_change_win', btnsname=btnsname,
                          hide_widgets=self.statisticInteractiveWidgets)
        self.posEntrys(
            carnum=self.parsed_string["car_number"],
            trashtype=self.parsed_string["trash_type"],
            trashcat=self.parsed_string["trash_cat"],
            contragent=self.parsed_string["carrier"],
            client=self.parsed_string['client'],
            notes=self.parsed_string["notes"],
            polygon=self.operator.get_polygon_platform_repr(record_info['id']),
            object=self.operator.get_pol_object_repr(record_info['object_id']),
            spec_protocols=False,
            call_method='manual',
        )
        self.root.bind('<Return>', lambda event: self.change_record())
        self.root.bind('<Escape>',
                       lambda event: self.destroyORUP(mode="decline"))
        self.root.bind("<Button-1>",
                       lambda event: self.clear_optionmenu(event))
        self.unbindArrows()

    def parse_string(self, string):
        # Парсит выбранную строку из окна статистики и возвращает словарь с элементами
        parsed = {}
        parsed["car_number"] = string[0]
        parsed["carrier"] = string[2]
        parsed["trash_cat"] = string[6]
        parsed["trash_type"] = string[7]
        parsed["notes"] = string[10]
        parsed['client'] = string[1]
        return parsed

    def change_record(self):
        info = self.get_orup_entry_reprs()
        self.try_upd_record(info['carnum'], info['carrier'], info['trash_cat'],
                            info['trash_type'], info['comm'],
                            info['polygon_platform'], info['client'],
                            info['polygon_object'])

    def try_upd_record(self, car_number, carrier, trash_cat, trash_type,
                       comment, polygon, client, pol_object):
        self.car_protocol = self.operator.fetch_car_protocol(car_number)
        data_dict = {}
        data_dict['car_number'] = car_number
        data_dict['chosen_trash_cat'] = trash_cat
        data_dict['type_name'] = trash_type
        data_dict['carrier_name'] = carrier
        data_dict['sqlshell'] = object
        data_dict['photo_object'] = self.settings.redbg[3]
        data_dict['client'] = client
        response = self.operator.orup_error_manager.check_orup_errors(
            orup='brutto',
            xpos=self.settings.redbg[1],
            ypos=self.settings.redbg[2],
            **data_dict)
        print("RESP", response)
        if not response:
            auto_id = self.operator.get_auto_id(car_number)
            carrier_id = self.operator.get_client_id(carrier)
            trash_cat_id = self.operator.get_trash_cat_id(trash_cat)
            trash_type_id = self.operator.get_trash_type_id(trash_type)
            polygon_id = self.operator.get_polygon_platform_id(polygon)
            client_id = self.operator.get_client_id(client)
            pol_object_id = self.operator.get_polygon_object_id(pol_object)
            self.operator.ar_qdk.change_opened_record(record_id=self.record_id,
                                                      auto_id=auto_id,
                                                      carrier=carrier_id,
                                                      trash_cat_id=trash_cat_id,
                                                      trash_type_id=trash_type_id,
                                                      comment=comment,
                                                      car_number=car_number,
                                                      polygon=polygon_id,
                                                      client=client_id,
                                                      pol_object=pol_object_id)
            self.destroyORUP()
            self.upd_statistic_tree()

    def upd_statistic_tree(self):
        """ Обновить таблицу статистики """
        self.get_history()
        self.draw_stat_tree()

    def draw_add_comm(self):
        btnsname = 'addCommBtns'
        self.add_comm_text = self.getText(h=5, w=42, bg=cs.orup_bg_color)
        self.initBlockImg(name='addComm', btnsname=btnsname,
                          seconds=('second'),
                          hide_widgets=self.statisticInteractiveWidgets)
        self.can.create_window(self.w / 2, self.h / 2.05,
                               window=self.add_comm_text, tag='blockimg')
        self.root.bind('<Return>', lambda event: self.add_comm())
        self.root.bind('<Escape>',
                       lambda event: self.destroyBlockImg(mode="total"))

    def add_comm(self):
        comment = self.add_comm_text.get("1.0", 'end-1c')
        self.operator.ar_qdk.add_comment(record_id=self.record_id,
                                         comment=comment)
        self.destroyBlockImg()
        self.upd_statistic_tree()

    def posOptionMenus(self):
        self.placeTypeOm()
        self.placeCatOm(bg=self.filterColNA)
        self.placeContragentCombo()
        self.placePoligonOm()
        self.placeObjectOm()
        self.placeCarnumCombo()
        self.placeClientsOm()

        self.statisticInteractiveWidgets = [self.stat_page_polygon_combobox,
                                            self.trashTypeOm, self.trashCatOm,
                                            self.contragentCombo,
                                            self.stat_page_carnum_cb,
                                            self.clientsOm,
                                            self.stat_page_pol_object_combobox]
        self.hide_widgets(self.statisticInteractiveWidgets)

    def abortFiltres(self):
        """ Сбросить все фильтры на значения по умолчанию
        """
        for combobox in self.statisticInteractiveWidgets:
            if isinstance(combobox, AutocompleteCombobox):
                combobox.set_default_value()
        self.startCal.set_date(datetime.datetime.today())
        self.endCal.set_date(datetime.datetime.today())
        self.upd_statistic_tree()

    def placeClientsOm(self):
        listname = ['клиенты'] + self.operator.get_clients_reprs()
        self.stat_page_clients_var = StringVar()
        self.clientsOm = AutocompleteCombobox(self.root,
                                              textvariable=self.stat_page_clients_var,
                                              default_value=listname[0])
        self.configure_combobox(self.clientsOm)
        self.clientsOm['style'] = 'orup.TCombobox'
        self.clientsOm.set_completion_list(listname)
        self.clientsOm.config(width=12, height=30,
                              font=fonts.statistic_filtres)
        self.can.create_window(self.w / 1.278, self.btns_height,
                               window=self.clientsOm,
                               tags=('filter', 'typeCombobox'))

    def placePoligonOm(self):
        listname = ['площадка'] + self.operator.get_polygon_platforms_reprs()
        self.poligonVar = StringVar()
        self.stat_page_polygon_combobox = AutocompleteCombobox(self.root,
                                                               textvariable=self.poligonVar,
                                                               default_value=
                                                               listname[0])
        self.configure_combobox(self.stat_page_polygon_combobox)
        self.stat_page_polygon_combobox.set_completion_list(listname)
        self.stat_page_polygon_combobox.config(width=8, height=30,
                                               font=fonts.statistic_filtres)
        self.can.create_window(self.w / 2.475, self.btns_height,
                               window=self.stat_page_polygon_combobox,
                               tags=('filter', 'typeCombobox'))

    def placeObjectOm(self):
        listname = ['объект'] + self.operator.get_pol_objects_reprs()
        self.pol_object_var = StringVar()
        self.stat_page_pol_object_combobox = AutocompleteCombobox(self.root,
                                                                  textvariable=self.pol_object_var,
                                                                  default_value=
                                                                  listname[0])
        self.configure_combobox(self.stat_page_pol_object_combobox)
        self.stat_page_pol_object_combobox.set_completion_list(listname)
        self.stat_page_pol_object_combobox.config(width=16, height=36,
                                                  font=fonts.statistic_filtres)
        self.can.create_window(self.w / 1.91, self.h / 3.85,
                               window=self.stat_page_pol_object_combobox,
                               tags=('filter', 'typeCombobox'))

    def placeTypeOm(self):
        listname = ['вид груза'] + self.operator.get_trash_types_reprs()
        self.stat_page_trash_type_var = StringVar()
        self.trashTypeOm = AutocompleteCombobox(self.root,
                                                textvariable=self.stat_page_trash_type_var,
                                                default_value=listname[0])
        self.configure_combobox(self.trashTypeOm)
        self.trashTypeOm.set_completion_list(listname)
        self.trashTypeOm.config(width=9, height=30,
                                font=fonts.statistic_filtres)
        self.can.create_window(self.w / 3.435, self.btns_height,
                               window=self.trashTypeOm,
                               tags=('filter', 'typeCombobox'))

    def placeCatOm(self, bg, deffvalue='кат. груза'):
        listname = ['кат. груза'] + self.operator.get_trash_cats_reprs()
        self.stat_page_trash_cat_var = StringVar()
        self.trashCatOm = AutocompleteCombobox(self.root,
                                               textvariable=self.stat_page_trash_cat_var,
                                               default_value=listname[0])
        self.trashCatOm.set_completion_list(listname)
        self.trashCatOm.config(width=9, height=30,
                               font=fonts.statistic_filtres)
        self.can.create_window(self.w / 5.45, self.btns_height,
                               window=self.trashCatOm,
                               tags=('filter', 'catOm'))
        self.configure_combobox(self.trashCatOm)

    def placeContragentCombo(self):
        carriers = ['перевозчики'] + self.operator.get_clients_reprs()
        self.stat_page_carrier_var = StringVar()
        self.contragentCombo = AutocompleteCombobox(self.root,
                                                    textvariable=self.stat_page_carrier_var,
                                                    default_value=carriers[0])
        self.configure_combobox(self.contragentCombo)
        self.contragentCombo.set_completion_list(carriers)
        self.contragentCombo.config(width=11, height=30,
                                    font=fonts.statistic_filtres)
        self.can.create_window(self.w / 1.91, self.btns_height,
                               window=self.contragentCombo,
                               tags=('filter', 'stat_page_carrier_var'))

    def placeCarnumCombo(self):
        listname = ['гос.номер'] + self.operator.get_auto_reprs()
        self.stat_page_carnum_cb = AutocompleteCombobox(self.root,
                                                        default_value=listname[
                                                            0])
        self.stat_page_carnum_cb.set_completion_list(listname)
        self.configure_combobox(self.stat_page_carnum_cb)
        self.stat_page_carnum_cb.config(width=11, height=20,
                                        font=fonts.statistic_filtres)
        self.can.create_window(self.w / 1.53, self.btns_height,
                               window=self.stat_page_carnum_cb,
                               tags=('stat_page_carnum_cb', 'filter'))

    def place_amount_info(self, weight, amount, tag='amount_weight'):
        """ Разместить итоговую информацию (количество взвешиваний (amount), тоннаж (weigh) )"""
        if self.operator.current == 'Statistic' and self.blockImgDrawn == False:
            self.can.delete(tag)
            weight = self.formatWeight(weight)
            self.amount_weight = 'ИТОГО: {} ({} взвешиваний)'.format(weight,
                                                                     amount)
            self.can.create_text(self.w / 2, self.h / 1.113,
                                 text=self.amount_weight,
                                 font=self.font, tags=(tag, 'statusel'),
                                 fill=self.textcolor, anchor='s')

    def formatWeight(self, weight):
        weight = str(weight)
        print('**WEIGHT', weight)
        if len(weight) < 4:
            ed = 'кг'
        elif len(weight) >= 4:
            weight = int(weight) / 1000
            ed = 'тонн'
        weight = str(weight) + ' ' + ed
        return weight

    def placeText(self, text, xpos, ypos, tag='maincanv', color='black',
                  font='deff', anchor='center'):
        if font == 'deff': font = self.font
        xpos = int(xpos)
        ypos = int(ypos)
        self.can.create_text(xpos, ypos, text=text, font=self.font, tag=tag,
                             fill=color, anchor=anchor)

    def placeCalendars(self):
        self.startCal = MyDateEntry(self.root, date_pattern='dd/mm/yy')
        self.startCal.config(width=7, font=fonts.statistic_calendars)
        self.endCal = MyDateEntry(self.root, date_pattern='dd/mm/yy')
        self.endCal.config(width=7, font=fonts.statistic_calendars)
        # self.startCal['style'] = 'stat.TCombobox'
        # self.endCal['style'] = 'stat.TCombobox'
        self.startCal['style'] = 'orup.TCombobox'
        self.endCal['style'] = 'orup.TCombobox'

        self.can.create_window(self.w / 3.86, self.h / 3.85,
                               window=self.startCal,
                               tags=('statCal'))
        self.can.create_window(self.w / 2.75, self.h / 3.85,
                               window=self.endCal,
                               tags=('statCal'))
        self.statisticInteractiveWidgets.append(self.startCal)
        self.statisticInteractiveWidgets.append(self.endCal)
        self.calendarsDrawn = True

    def drawing(self):
        Terminal.drawing(self)
        self.drawWin('maincanv', 'statisticwin')
        self.hiden_widgets += self.buttons_creation(tagname='winBtn')
        if not self.calendarsDrawn:
            self.placeCalendars()
        self.get_history()
        self.draw_stat_tree()
        self.show_widgets(self.statisticInteractiveWidgets)

    def get_history(self):
        """ Запрашивает истоию заездов у GCore """
        trash_cat = self.operator.get_trash_cat_id(
            self.stat_page_trash_cat_var.get())
        trash_type = self.operator.get_trash_type_id(
            self.stat_page_trash_type_var.get())
        carrier = self.operator.get_client_id(self.stat_page_carrier_var.get())
        auto = self.operator.get_auto_id(self.stat_page_carnum_cb.get())
        platform_id = self.operator.get_polygon_platform_id(
            self.stat_page_polygon_combobox.get())
        pol_object_id = self.operator.get_polygon_object_id(
            self.stat_page_pol_object_combobox.get())
        client = self.operator.get_client_id(self.stat_page_clients_var.get())
        self.operator.ar_qdk.get_history(
            time_start=self.startCal.get_date(),
            time_end=self.endCal.get_date(),
            trash_cat=trash_cat,
            trash_type=trash_type,
            carrier=carrier, auto_id=auto,
            polygon_object_id=pol_object_id,
            client=client, platform_id=platform_id
        )

    def draw_stat_tree(self):
        self.can.create_window(self.w / 1.9, self.h / 1.7,
                               window=self.tree,
                               tag='tree')
        self.tar.sortId(self.tree, '#0', reverse=True)

    def openWin(self):
        Terminal.openWin(self)
        self.root.bind("<Button-1>",
                       lambda event: self.clear_optionmenu(event))

    def page_close_operations(self):
        self.hide_widgets(self.statisticInteractiveWidgets)
        self.root.unbind("<Button-1>")
        self.can.delete('amount_weight', 'statusel')

    def initBlockImg(self, name, btnsname, slice='shadow', mode='new',
                     seconds=[], hide_widgets=[], **kwargs):
        Terminal.initBlockImg(self, name, btnsname,
                              hide_widgets=self.statisticInteractiveWidgets)


class AuthWin(Terminal):
    '''Окно авторизации'''

    def __init__(self, root, settings, operator, can):
        Terminal.__init__(self, root, settings, operator, can)
        self.name = 'AuthWin'
        self.buttons = settings.authBtns
        self.s = settings
        self.r = root
        self.currentUser = 'Андрей'
        self.font = '"Montserrat Regular" 14'

    def send_auth_command(self):
        """ Отправить команду на авторизацию """
        pw = self.auth_page_password_entry.get()
        login = self.auth_page_login_var.get()
        self.operator.ar_qdk.try_auth_user(username=login, password=pw)
        self.currentUser = login

    def createPasswordEntry(self):
        var = StringVar(self.r)
        bullet = '\u2022'
        pwEntry = Entry(self.r, border=0,
                        width=
                        el_sizes.entrys['authwin.password'][self.screensize][
                            'width'], show=bullet,
                        textvariable=var, bg=cs.auth_background_color,
                        font=self.font, fg='#BABABA',
                        insertbackground='#BABABA', highlightthickness=0)
        pwEntry.bind("<Button-1>", self.on_click)
        pwEntry.bind("<BackSpace>", self.on_click)

        return pwEntry

    def on_click(self, event):
        event.widget.delete(0, END)
        self.auth_page_password_entry.config(show='\u2022')

    def incorrect_login_act(self):
        self.auth_page_password_entry.config(show="", highlightthickness=1,
                                             highlightcolor='red')
        self.auth_page_password_entry.delete(0, END)
        self.auth_page_password_entry.insert(END, 'Неправильный пароль!')

    def get_login_type_cb(self):
        self.auth_page_login_var = StringVar()
        self.usersComboBox = AutocompleteCombobox(self.root,
                                                  textvariable=self.auth_page_login_var)
        self.usersComboBox['style'] = 'authwin.TCombobox'
        self.configure_combobox(self.usersComboBox)
        self.usersComboBox.set_completion_list(self.operator.get_users_reprs())
        self.usersComboBox.set("")
        self.usersComboBox.config(
            width=el_sizes.comboboxes['authwin.login'][self.screensize][
                'width'],
            height=el_sizes.comboboxes['authwin.login'][self.screensize][
                'height'],
            font=self.font)
        self.usersComboBox.bind('<Return>',
                                lambda event: self.send_auth_command())
        return self.usersComboBox

    def rebinding(self):
        self.usersComboBox.unbind('<Return>')
        self.auth_page_password_entry.unbind('<Return>')
        self.bindArrows()

    def drawing(self):
        Terminal.drawing(self)
        self.auth_page_password_entry = self.createPasswordEntry()
        self.auth_page_password_entry.bind('<Return>', lambda
            event: self.send_auth_command())
        self.usersChooseMenu = self.get_login_type_cb()
        self.can.create_window(self.s.w / 2, self.s.h / 1.61,
                               window=self.auth_page_password_entry,
                               tags=('maincanv', 'pw_win'))
        self.can.create_window(self.s.w / 2, self.s.h / 1.96,
                               window=self.usersChooseMenu, tag='maincanv')
        self.drawSlices(mode=self.name)
        self.buttons_creation(tagname='winBtn')

    def openWin(self):
        Terminal.openWin(self)
        self.drawWin('maincanv', 'start_background', 'login', 'password')
        self.can.delete('toolbar')
        self.can.delete('clockel')
        self.can.itemconfigure('btn', state='hidden')
        self.auth_page_password_entry.config(show='\u2022',
                                             highlightthickness=0)

    def page_close_operations(self):
        self.can.itemconfigure('btn', state='normal')


class MainPage(Terminal):
    def __init__(self, root, settings, operator, can):
        Terminal.__init__(self, root, settings, operator, can)
        self.name = 'MainPage'
        self.buttons = settings.gateBtns + settings.manual_gate_control_btn
        self.count = 0
        self.orupState = False
        self.errorShown = False
        self.chosenTrashCat = 'deff'
        self.tar = CurrentTreeview(self.root, operator, height=18)
        self.tar.createTree()
        self.tree = self.tar.get_tree()
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        self.win_widgets.append(self.tree)
        self.btn_name = self.settings.mainLogoBtn
        self.abort_round_btn = self.get_create_btn(settings.abort_round[0])
        self.make_abort_unactive()

    def create_abort_round_btn(self):
        self.can.create_window(self.settings.abort_round[0][1],
                               self.settings.abort_round[0][2],
                               window=self.abort_round_btn,
                               tag='winBtn')

    def make_abort_active(self):
        btn = self.abort_round_btn
        btn['state'] = 'normal'
        # try:
        #    self.buttons.remove(self.settings.abort_round_unactive[0])
        #    self.buttons.append(self.settings.abort_round[0])
        # except ValueError:
        #   pass

    def make_abort_unactive(self):
        btn = self.abort_round_btn
        btn['state'] = 'disabled'

    def drawMainTree(self):
        self.operator.ar_qdk.get_unfinished_records()
        self.can.create_window(self.w / 1.495, self.h / 2.8, window=self.tree,
                               tag='tree')
        self.tar.sortId(self.tree, '#0', reverse=True)

    def drawing(self):
        Terminal.drawing(self)
        self.operator.ar_qdk.get_status()
        print('Создаем основное дерево')
        self.drawMainTree()
        self.drawWin('win', 'road', 'order', 'currentEvents',
                     'entry_gate_base', 'exit_gate_base')
        self.hiden_widgets += self.buttons_creation(tagname='winBtn')

    # self.draw_gate_arrows()

    def drawRegWin(self):
        self.draw_block_win(self, 'regwin')

    def destroyBlockImg(self, mode='total'):
        Terminal.destroyBlockImg(self, mode)
        self.drawMainTree()

    def updateTree(self):
        self.operator.ar_qdk.get_unfinished_records()
        self.tar.sortId(self.tree, '#0', reverse=True)

    def OnDoubleClick(self, event):
        '''Реакция на дабл-клик по текущему заезду'''
        item = self.tree.selection()[0]
        self.chosenStr = self.tree.item(item, "values")
        self.record_id = self.tree.item(item, "text")
        if self.chosenStr[2] == '-':
            self.draw_rec_close_win()
        else:
            self.draw_cancel_tare()

    def draw_rec_close_win(self):
        btnsname = 'closeRecBtns'
        self.initBlockImg(name='ensureCloseRec', btnsname=btnsname,
                          seconds=('second'),
                          hide_widgets=self.win_widgets)
        self.root.bind('<Return>', lambda event: self.operator.close_record(
            self.record_id))
        self.root.bind('<Escape>',
                       lambda event: self.destroyBlockImg(mode="total"))

    def draw_cancel_tare(self):
        btnsname = 'cancel_tare_btns'
        self.initBlockImg(name='cancel_tare', btnsname=btnsname,
                          seconds=('second'),
                          hide_widgets=self.win_widgets)
        self.root.bind('<Escape>',
                       lambda event: self.destroyBlockImg(mode="total"))

    def page_close_operations(self):
        self.can.delete('win', 'statusel')
        # self.hide_widgets(self.abort_round_btn)
        self.unbindArrows()

    def openWin(self):
        Terminal.openWin(self)
        self.bindArrows()
        self.operator.draw_road_anim()
        self.draw_gate_arrows()
        self.draw_weight()
        if not self.operator.main_btns_drawn:
            self.create_main_buttons()
            self.operator.main_btns_drawn = True
        self.create_abort_round_btn()


class ManualGateControl(Terminal):
    def __init__(self, root, settings, operator, can):
        Terminal.__init__(self, root, settings, operator, can)
        self.name = 'ManualGateControl'
        self.buttons = self.settings.auto_gate_control_btn + self.settings.manual_open_internal_gate_btn + self.settings.manual_close_internal_gate_btn + self.settings.manual_open_external_gate_btn + self.settings.manual_close_external_gate_btn
        self.btn_name = self.settings.mainLogoBtn
        self.external_gate_state = 'close'
        self.enternal_gate_state = 'close'

    def send_gate_comm(self, gate_num, operation):
        """ Отправить на AR комманду закрыть шлагбаум """
        msg = {}
        msg['gate_manual_control'] = {'gate_name': gate_num,
                                      'operation': operation}
        response = self.send_ar_sys_comm(msg)
        print(response)

    def drawing(self):
        Terminal.drawing(self)
        self.drawWin('maincanv', 'road', 'manual_control_info_bar',
                     'entry_gate_base', 'exit_gate_base')
        self.hiden_widgets += self.buttons_creation(tagname='winBtn')

    def openWin(self):
        Terminal.openWin(self)
        self.operator.draw_road_anim()
        self.draw_gate_arrows()
        self.draw_weight()

    def page_close_operations(self):
        self.can.delete('win', 'statusel')
