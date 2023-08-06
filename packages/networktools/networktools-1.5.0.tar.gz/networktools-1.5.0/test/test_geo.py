import unittest
import random
from rich import print
import copy
from datetime import datetime, timedelta
from networktools.geo import (
    DataItem,
    DataPoint,
    NEUData,
    TimeData, 
    GeoData)


class TestStrFunctions(unittest.TestCase):
    def test_datapoint(self):
        a = 1.
        b = .2
        val_min = a - b  
        val_max = a + b
        data = {
            "value":a,
            "error":b,
            "min":val_min,
            "max":val_max
        }
        dp = DataPoint(a,b)
        dp_dict = dp.dict()
        epsilon = 1e-10
        assert all([v-epsilon<=dp_dict[k]<=v+epsilon for k,v in data.items()]), "DataPoint not valid"


    def test_datapoint_sum(self):
        a = 1.
        b = .2
        c = 9.
        d = .045
        dp = DataPoint(a,b)
        dp2 = DataPoint(c,d)
        dp += dp2
        aw = a + c
        ew = b + d
        eps = 1e-10
        assert all([aw - eps<= dp.value <= aw + eps,
                    ew-eps<=dp.error<=ew+eps]),  "DataPoint adding failure"
        


    def test_neu(self):
        E = DataPoint(1,.45)
        N = DataPoint(2,.11)
        U = DataPoint(3.5,.2)
        neu = NEUData(N,E,U)
        assert (neu.neu) == (N,E,U), "No es NEU"
        

    def test_neu_add(self):
        E = DataPoint(1,.45)
        N = DataPoint(2,.11)
        U = DataPoint(3.5,.2)
        (tN1,tE1,tU1) = (copy.deepcopy(N),copy.deepcopy(E),copy.deepcopy(U),)
        neu1 = NEUData(N,E,U)
        E = DataPoint(4,.25)
        N = DataPoint(5,.17)
        U = DataPoint(1,.01)
        neu2 = NEUData(N,E,U)
        (tN2,tE2,tU2) = (copy.deepcopy(N),copy.deepcopy(E),copy.deepcopy(U),)

        neu1 += neu2
        tN1 +=  tN2
        tE1 +=  tE2
        tU1 +=  tU2

        assert (neu1.neu) == (tN1,tE1,tU1), "NEU class can't add"


    def test_timedata(self):
        rec = datetime.utcnow()
        delta = .1        
        td = TimeData(rec, delta)
        assert td.info == (rec, delta), "TimeData cotiene mismos valores"


    def test_timedata_add(self):
        rec = datetime.utcnow()
        delta = .1        
        td1 = TimeData(rec, delta)
        rec = datetime.utcnow() + timedelta(seconds=-60)
        delta = .5        
        td2 = TimeData(rec, delta)
        td1 += td2
        assert td2.recv <= td1.recv, "TimeData cotiene mismos valores"


    def test_geodata(self):
        rec = datetime.utcnow()
        delta = .1        
        td = TimeData(rec, delta)
        E = DataPoint(1,.45)
        N = DataPoint(2,.11)
        U = DataPoint(3.5,.2)
        neu = NEUData(N,E,U)
        gd = GeoData(
            "test", 
            "TEST", 
            datetime.timestamp(),
            datetime.utcnow(), 
            neu, 
            td)

if __name__ == "__main__":
     unittest.main()
