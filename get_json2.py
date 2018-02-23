import json,time,datetime,itertools,sys,re,sqlite3,hashlib,requests
from plotly.graph_objs import *
from timezone2 import timezone
import pandas as pd

#for web log in common access log file and combine access log file
COMBINED_LOGLINE_PAT = re.compile(
    r'(?P<origin>\d+\.\d+\.\d+\.\d+|[a-zA-Z0-9\.\-]+) (?P<identd>-|\w*) (?P<auth>-|\w*) '
    + r'\[(?P<ts>(?P<date>[^\[\]:]+):(?P<time>\d+:\d+:\d+)) (?P<tz>[\-\+]?\d\d\d\d)\] '
    + r'"(?P<method>\w+) (?P<path>[\S]+) (?P<protocol>[^"]+)" (?P<status>\d\d\d) (?P<bytes>-|\d+)'
    + r'( (?P<referrer>"[^"]*")( (?P<client>"[^"]*")( (?P<cookie>"[^"]*"))?)?)?\s*\Z')

locate = []
class make_json():
    def __init__(self,filename):
        self.append_file(self,filename)


#check md 5 in database if have reject
# and do plot_graph function in main file
    def append_file(self,filename):
        hasher = hashlib.md5()
        f = open(filename,'rb')
#
# check md 5 just read only hasher.update !!!
#
        for chunk in iter (lambda :f.read(4096),b""):
            hasher.update(chunk)
        read = hasher.hexdigest()
#
# open data base
#
        connection = sqlite3.connect('data_check2.db')
        cur = connection.cursor()
        cur.execute("SELECT * FROM table_contents")
        for x in cur.fetchall():
            if read in x:
                self.filename = x[0]
#always export filename for doing export_map and plot_graph!!
                return self.filename
        self.get_json(self,filename,read)
#after that plotmap
        self.filename = filename
        print(self.filename)
        return self.filename


    def get_json(self,filename,read):
 #       self.filename = filename
        file = open(filename,'r')
        in_file = file.readlines()
        jsonfile = open('{}.json'.format(filename), 'w')
        set_ip = set()
        entries = []
#enumarate when use it export a len of input
#is slice seperate like 111 to 1 1 1
#sys.maxsize is maximum of in_file
        for count, line in enumerate(itertools.islice(in_file, 0, sys.maxsize)):
            match_info = re.findall(COMBINED_LOGLINE_PAT,line)
            try:
                entry = {}
                #timestamp = self.parse_apache_date(self,match_info[0][3], match_info[0][6])
                #timestamp_str = timestamp.isoformat()
                entry['id'] = match_info[0][0] + ':' + timestamp_str + ':' + str(count)
                entry['label'] = entry['id']
                entry['origin'] = match_info[0][0]
                entry['timestamp'] = timestamp_str
                entry['path'] = match_info[0][8]
                entry['method'] = match_info[0][7]
                entry['protocol'] = match_info[0][9]
                entry['status'] = match_info[0][10]
                if match_info[0][11] != '-':
                    entry['bytes'] = match_info[0][11]
                if match_info[0][12] != '"-"':
                    entry['referrer'] = match_info[0][12]
                entry['location'] = ''
                entry['client'] = match_info[0][13]
                set_ip.add(entry['origin'])
                entries.append(entry)
            except:
                pass
        json_data_log = self.json_in_file(self,entries,set_ip,filename,read)
        jsonfile.write(json_data_log)
#
# render json for one time use set ip into
#
 # check ip table
    def json_in_file(self,entries,set_ip,filename,read):
        list_set=set()
        locate=[]
        for i in set_ip:
            locate = self.check_location_ip(self,i,locate)
        for index_origin in range(len(entries)):
            for index in range(len(locate)):
                if (entries[index_origin]['origin'])==(locate[index]['ip']):
                    entries[index_origin]['location'] = locate[index]['location']

#
#write json
#
        connection = sqlite3.connect('data_check2.db')
        cur = connection.cursor()
        cur.execute("insert into table_contents values(?,?)",(filename,read))
        connection.commit()
        cur.close()
        connection.close()
        json_data_log = json.dumps(entries,indent=4)
        return json_data_log

#        return self.filename

#convert string in standard platform datetime
    def parse_apache_date(self,date_str, tz_str):
        tt = time.strptime(date_str, "%d/%b/%Y:%H:%M:%S")
        tt = tt[:6] + (0, timezone(tz_str))
        return datetime.datetime(*tt)

    def check_location_ip(self,ip,locate):
        entry = {}
        connection = sqlite3.connect('data_check2.db')
        cur = connection.cursor()
        try:
            cur.execute("SELECT * FROM check_location where ip=?",(ip,))
            list_do = []
            for i in cur.fetchone():
                list_do.append(i)
            entry['location'] = {'latitude':list_do[3],'longitude':list_do[2], 'country_name':list_do[0],'city':list_do[1]}
            entry['ip'] = ip
            locate.append(entry)
        except:
            try:
                ipdb = requests.get("http://www.freegeoip.net/json/{}".format(ip))
                ipdb_load = json.loads(ipdb.text)
                entry = {}
                entry['ip'] = ip
                latitude = ipdb_load['latitude']
                longitude = ipdb_load['longitude']
                country = ipdb_load['country_name']
                city = ipdb_load['city']
                entry['location'] = {'latitude':latitude,'longitude':longitude, 'country_name':country,'city':city}
                locate.append(entry)
                cur.execute("insert into check_location values(?,?,?,?,?)",(country,city,longitude,latitude,ip))
                connection.commit()

        # use for service get domain that 404 error
            except:
               pass
        return locate


#make_json.append_file(make_json,filename='C:/Users/Lenovo M7/Desktop/test2/access_log.processed.2.2')
