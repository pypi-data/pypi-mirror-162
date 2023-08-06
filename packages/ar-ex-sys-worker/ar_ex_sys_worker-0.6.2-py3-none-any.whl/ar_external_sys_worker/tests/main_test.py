import os
import unittest

import wsqluse.wsqluse

from ar_external_sys_worker import main


class TestCase(unittest.TestCase):
    sql_shell = wsqluse.wsqluse.Wsqluse(dbname=os.environ.get('DB_NAME'),
                                        user=os.environ.get('DB_USER'),
                                        password=os.environ.get('DB_PASS'),
                                        host=os.environ.get('DB_HOST'))
    pol_login = os.environ.get('POL_LOGIN')
    pol_pass = os.environ.get('POL_PASS')

    # inst = main.SignallActWorker(login=pol_login,
    #                             password=pol_pass,
    #                             sql_shell=sql_shell)

    @unittest.SkipTest
    def test_some(self):
        list_name = ['1', '2']
        command = "SELECT * FROM records WHERE trash_cat IN {} and time_in > '06.05.2022'"
        command = command.format(tuple(list_name))
        res = self.sql_shell.try_execute_get(command)

    @unittest.SkipTest
    def testNewSignallActWorker(self):
        inst = main.SignallActWorker(self.sql_shell,
                                     self.pol_login, self.pol_pass)
        inst.send_unsend_acts()

    @unittest.SkipTest
    def testSignallActWorker(self):
        response = self.inst.send_and_log_act(car_number='В060ХА702',
                                              ex_id=19,
                                              gross=1488,
                                              tare=1377,
                                              cargo=111,
                                              alerts=['alert0'],
                                              carrier='263028743',
                                              operator_comments={
                                                  'gross': 'grosComm',
                                                  'tare': '',
                                                  'additional': 'addComm',
                                                  'changing': '',
                                                  'closing': 'closingComm'},
                                              photo_in=None,
                                              photo_out=None,
                                              time_in='2022-07-15 13:37:00',
                                              time_out='2022-07-15 14:38:00',
                                              trash_cat='ТКО',
                                              trash_type='4 класс')

    @unittest.SkipTest
    def test_send_unsent(self):
        self.inst.send_unsend_acts()

    @unittest.SkipTest
    def test_photo_mark(self):
        resp = self.inst.get_photo_path(197924, 1)

    @unittest.SkipTest
    def test_SignallActChecker(self):
        ins = main.SignallActChecker(self.sql_shell, "1", "071298")
        ins.work('2022-05-01', '2022-05-30', 'ООО «Мохит-СТР»')

    @unittest.SkipTest
    def test_SignallActCheckerTLB(self):
        sql_shell = wsqluse.wsqluse.Wsqluse(dbname='wdb',
                                            user='qodex',
                                            password='en23',
                                            host='127.0.0.1')
        ins = main.SignallActCheckerOldWDB(self.sql_shell, "1", "071298")
        ins.work('2022-03-01', '2022-03-31', 'ООО «Грин Сити»')

    @unittest.SkipTest
    def test_SignallActDel(self):
        with open('no_photo_records.txt', 'r') as fobj:
            lines = ['208944']
            for line in lines:
                line = line.replace('\n', '')
                inst = main.SignallActReuploder(self.sql_shell)
                res = inst.delete_act(line)
                print(res)

    @unittest.SkipTest
    def test_asu_main(self):
        inst = main.ASUActsWorker(sql_shell=self.sql_shell,
                                  trash_cats_list=['ТКО'],
                                  time_start='2022.04.07')
        print(inst.send_unsend_acts())

    @unittest.SkipTest
    def test_signall_main(self):
        inst = main.SignallActWorker(sql_shell=self.sql_shell,
                                     trash_cats_list=['ТКО'],
                                     time_start='2022.04.07')
        print(inst.send_unsend_acts())

    def test_change_act(self):
        inst = main.SignallActUpdater(sql_shell=self.sql_shell)
        print(inst.headers)
        #res = inst.work(record_id=207950,
        #                car_number='А001ХО992',
        #                transporter_inn='0278957459',
        #                trash_cat='ПО',
         #               trash_type='Прочее',
         #               comment='ТЕСТ')
        #rint("RES", res.json())

    @unittest.SkipTest
    def test_auto_getter(self):
        inst = main.SignallAutoGetter(self.sql_shell, 'http://192.168.100.118')
        resp = inst.get_cars()
        for auto in resp['cars']:
            print(f'working with {auto}')
            resp = inst.insert_car_to_gravity(car_number=auto['car_number'],
                                              ident_number=auto[
                                                  'ident_number'],
                                              ident_type=auto['ident_type'],
                                              auto_chars=auto['auto_chars'])
            print(f"resp: {resp}")

    @unittest.SkipTest
    def test_clients_getter(self):
        inst = main.SignallClientsGetter(self.sql_shell,
                                         'http://127.0.0.1')
        resp = inst.get_cars()
        for client in resp['transporters']:
            resp = inst.insert_client_to_gravity(name=client['name'],
                                                 inn=client['inn'],
                                                 kpp=client['kpp'])
            print(resp.json())


if __name__ == '__main__':
    unittest.main()
