import numpy as np
import pandas as pd
import re

class data():
  def doitnow(self,filename):
      pass
  # Seperate type
  def getdf(self,filename):
        self.dataset = pd.read_excel('{}'.format(filename))
        key = self.dataset.keys()
        getstart = []
        date = []
        catagories = []
        values = []
        for i in key:
            gettype = {}
            a = self.dataset[i]
            gettype['colums'] = i
            types = np.dtype(a)
            gettype['type'] = types
            getstart.append(gettype)

        for i in getstart:
            if i['type'] == 'object':
                catagories.append(i['colums'])
            if i['type'] == 'float64' or i['type'] == 'int64':
                values.append(i['colums'])
            if i['type'] == 'datetime64[ns]':
                date.append(i['colums'])
        return date,catagories,values,key
  #
  def getinfo(self,indexx,indexy,mdata):
        plotlist = []
        dimentioncol = []
        valcol = []
        forcol = 0
        for i in indexx:
            plotlist.append(i)
            dimentioncol.append(forcol)
            forcol += 1
        for i in indexy:
            plotlist.append(i)
            valcol.append(forcol)
            forcol += 1

        df = mdata.iloc[:,plotlist].values
        df = pd.DataFrame(df)
        df = df.groupby(dimentioncol)[valcol].sum()
        #print(df)
        inform = df.to_dict()
        for i in inform:
             for a in inform[i]:
                self.getdataform  = inform[i]
        b = sorted(self.getdataform.items(), key=lambda x: x[0])
        return b

  #  Range date
  def selectdate(self,xy,formatdmy):
      listselect = []
      for indexxy in xy:
          indexxy = str(indexxy)
          normal = re.compile(r'(?P<date>\d+\-\d+\-\d+)')
          indexxy = re.findall(normal,indexxy)
          indexxy = str(indexxy[0])
          indexxy = indexxy.split('-')
          listselect.append(indexxy)
      if formatdmy == 'years':
          slice = 0
          forpd = self.selectlayer2(listselect,slice,xy)
      elif formatdmy == 'dates':
          slice = 2
          forpd = self.selectlayer2(listselect,slice,xy)
      elif formatdmy == 'months':
          slice = 1
          forpd = self.selectlayer2(listselect,slice,xy)

      data = pd.DataFrame(forpd)
      data = data.groupby(['selected']).agg({'count': np.sum})
      inform = data.to_dict()
      for i in inform:
         for a in inform[i]:
            xy = inform[i]
      b = sorted(xy.items(), key=lambda x: x[0])
      return b

  # Interested list
  def selectlayer2(self,listselect,slice,xy):
      listselect2 = []
      slices = 0
      for i in range(len(xy)):
              newxy = {}
              year = str(listselect[slices][slice])
              newxy['selected'] = year
              newxy['count'] = xy[slices][1]
              slices += 1
              listselect2.append(newxy)
      return listselect2
