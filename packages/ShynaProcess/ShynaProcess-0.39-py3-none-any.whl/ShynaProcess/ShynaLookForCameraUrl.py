from genericpath import exists
import socket
import urllib.request
from ShynaDatabase import Shdatabase
from Shynatime import ShTime


class LookForCameraUrl:
    """
    Run update_cam_url function from the class. It will update the camera url in the database under cam_url table.
    it will automatically detect the router possible IP and then it tries to connect all possible devices.
    Cam return with data hence add that specific IP in the database.
    Obsolete
    """
    base_ip = ""
    st_port = ":8080"
    s_data = Shdatabase.ShynaDatabase()
    s_time = ShTime.ClassTime()
    result = False
    cam_url = []

    def get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                # doesn't even have to be reachable
                s.connect(('10.255.255.255', 1))
                self.base_ip = s.getsockname()[0]
                # print(s.getsockname())
            except Exception as e:
                print(e)
                self.base_ip = '127.0.0.1'
            finally:
                s.close()
            return self.base_ip
        except Exception as e:
            print(e)

    def update_cam_url(self):
        exists_url = []
        exists_url = self.get_cam_url()
        print("Already URLS in the database are:")
        print(exists_url)
        try:
            self.base_ip = self.get_ip()
            self.base_ip = "http://" + str(self.base_ip).rsplit(".", maxsplit=1)[0] + "."
            for i in range(255):
                cam_url = str(self.base_ip) + str(i) + str(self.st_port)
                print("Checking for ", cam_url)
                if self.open_url(ur=cam_url):
                    if cam_url in exists_url:
                        print(cam_url, "already there")
                        pass
                    else:
                        print("Adding ", cam_url, "to Database")
                        self.s_data.query = "INSERT INTO cam_url (cam_url,task_date,task_time,status)" \
                                            "VALUES('" + str(cam_url) + "','" + str(self.s_time.now_date) + "','" \
                                            + str(self.s_time.now_time) + "','active');"
                        self.s_data.insert_or_update_or_delete_with_status()
                else:
                    pass
            if str(exists_url[0]).lower().__contains__('empty'):
                pass
            else:
                for i in range(len(exists_url)):
                    if self.open_url(ur=exists_url[i]):
                        pass
                    else:
                        print("Deleting",exists_url[i]," from the database")
                        self.s_data.query = "DELETE from cam_url where cam_url='"+str(exists_url[i])+"'"
                        self.s_data.create_insert_update_or_delete()
        except Exception as e:
            print(e)
        finally:
            self.s_data.set_date_system(process_name="update_cam_url")


    def open_url(self, ur):
        try:
            x = urllib.request.urlopen(url=ur, timeout=2)
            response = x.read()
            if response == b'':
                self.result = False
            else:
                self.result = True
        except Exception:
            self.result = False
        finally:
            return self.result

    def get_cam_url(self):
        try:
            self.s_data.query = "Select cam_url from cam_url order by count DESC"
            base_ip = self.s_data.select_from_table()
            if base_ip[0] == 'Empty':
                self.cam_url.append(False)
            else:
                for item in base_ip:
                    for _ in item:
                        self.cam_url.append(_)
        except Exception as e:
            print(e)
            self.cam_url.append(False)
        finally:
            return self.cam_url


if __name__ == '__main__':
    LookForCameraUrl().update_cam_url()