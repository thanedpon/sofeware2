import json
import pandas
import matplotlib.pyplot as plt
import numpy
from mpl_toolkits.basemap import Basemap
import re
class plot_only():
    def __init__(self,start,stop,filename):
        self.plot_graph(self,start,stop,filename)


    def plot_graph(self,start,stop,filename):
        file =  open("{}.json".format(filename),"r")
        data = file.read()
        document = json.loads(data)
        Table_data = []
#
#create new json for pandas dataframe just only for use
#
        for result in document:
            Table = {}
            Table['ip'] = result['origin']
            normal = re.compile(r'(?P<origin>\d+\-\d+\-\d+)')
            date = re.findall(normal,result['timestamp'])
            Table['date'] = date[0]
            Table['latitude'] = result['location']['latitude']
            Table['longitude'] = result['location']['longitude']
            Table['count'] = '1'
            Table_data.append(Table)
        data = json.dumps(Table_data)
        df = pandas.read_json(data,orient='records')
        df['date'] = pandas.to_datetime(df['date'])
        df.index = df['date']
        del df['date']
        if start == stop:
            df1 = df[start]
        else:
            df1 = df[start:stop]
#tobe pandas series
        df2 = df1[df1['count'] == 1].groupby(['ip','latitude','longitude']).agg({'count': numpy.sum})
#create new dataframe for sort value
        df3 = pandas.DataFrame({'times':df2['count'].values,'ip':df2['count'].index})
        df3.sort_values(by='times',inplace=True,ascending=False)
        #print(df3)
        self.cal_cylate_top_ten(self,filename,df3)
        print(df3)
#
#get top ten
#
    def cal_cylate_top_ten(self,filename,df3):
        filename=filename
        label = []
        log = []
        lat = []
        size = []
        for i in df3['ip']:
            label.append(i[0])
            log.append(i[1])
            lat.append(i[2])
        for i in df3['times']:
            size.append(i)
        if len(label) > 10:
            del(label[10:])
            del(size[10:])

        self.graph_gui(self,filename,label,size)
        self.export_map(self,lat,log,filename)
        print(label)
#
#draw graph
#
    def graph_gui(self,filename,label,size):
        labels = label
        sizes = size
        colors = ['tomato', 'darksalmon', 'rosybrown', 'lightcoral','indianred','darkred','lightpink','coral','hotpink','mistyrose']
        patches,text = plt.pie(sizes,colors=colors, shadow=True,startangle=140)
        plt.legend(patches, labels,bbox_to_anchor=(0.85,1.025),loc="upper left")
        plt.axis('equal')
#        plt.show()
        plt.savefig('{}.png'.format(filename),bbox_inches='tight',dpi=95)
        plt.close()

    def export_map(self,lat,log,filename):


        m = Basemap(projection='robin',lat_0=0,lon_0=-100,resolution='l',area_thresh=1000.0)
        m.drawcoastlines(linewidth=0.1)
#        m.drawcounties(linewidth=0.1)
        m.drawstates(linewidth=0.1)
        m.fillcontinents(color='#50a2a7',lake_color='#FFFFFF')
        m.drawmapboundary(fill_color='#FFFFFF')
        m.drawmapboundary()

        for i in range(len(lat)):
            lat,lon = lat,log
            x,y = m(lat,lon)
            m.plot(x,y,'.',color='#444444')
#        plt.show()
        plt.savefig('{}_map.png'.format(filename))
        plt.close()
#plot_only.plot_graph(plot_only,'','','C:/Users/Lenovo M7/Desktop/test2/access_log.processed.2')

