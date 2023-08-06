"""
Geographic functions to calculate different values, among this the
change of cooridnate projections
Some special functions for geometric and geodesic use

"""
from math import sin, cos
import math
import sys
import os
import asyncio
import dataclasses
import time 
import signal
import time
import operator
from functools import reduce
from pathlib import Path
from enum import IntEnum, auto
from datetime import datetime
from dataclasses import dataclass as std_dataclass, asdict
from typing import Dict, Any, List, Tuple, Callable, Union
from typing import Tuple, Dict, Union, Optional
from pydantic.dataclasses import dataclass
from pydantic import ValidationError, validator
from dacite import from_dict
import numpy as np
import numpy.typing as npt



Double = Union[float, np.float64]
Matrix = npt.NDArray[np.float64]

def excentricity(a_0: float, b_0: float) -> float:
    """
    Excentricity given 'a' and 'b'
    """
    assert a_0 >= b_0, "a must be a superior value over b"
    aux = b_0/a_0
    return math.sqrt(1. - aux**2)


ECUATORIAL: float = 6378.137e3
POLAR: float = 6356.75231424e3
E: float = excentricity(ECUATORIAL, POLAR)
F: float = (ECUATORIAL-POLAR)/ECUATORIAL
E_2: float = E**2
DG2RD: float = math.pi/180
RD2DG: float = 180/math.pi


def rad2deg(rlat: float, rlon: float) -> Tuple[float, float]:
    """
    Converts radians to degree
    """
    dlat = math.degrees(rlat)
    dlon = math.degrees(rlon)
    return (dlat, dlon)


def deg2rad(dlat: float, dlon: float) -> Tuple[float, float]:
    """
    Convert lat-lon def to radians
    """
    rlat = math.radians(dlat)
    rlon = math.radians(dlon)
    return (rlat, rlon)


def radius(latitude: float) -> Tuple[float, float, float]:
    """
    Given the latitude returns the radio
    """
    sin_lat = math.sin(latitude)
    dex = math.pow(E, 2)
    fact_n = ECUATORIAL/math.sqrt(1-dex*sin_lat**2)
    fact_m = ECUATORIAL*(1-dex)/math.sqrt((1-dex*(sin_lat**2)) ** 3)
    result_radius = math.sqrt(fact_n*fact_m)
    return result_radius, fact_n, fact_m



def sph_rotation_matrix(lat: float, lon: float) -> Matrix:
    """
    Given lat and longitude returns the spherical rotation matrix
    """
    phi = lat  # rads
    lamb = lon  # rads
    rho_ = [cos(phi)*cos(lamb), cos(phi)*sin(lamb), sin(phi)]
    phi_ = [-sin(phi)*cos(lamb), -sin(phi)*cos(phi), cos(phi)]
    lamb_ = [-sin(lamb), cos(lamb), 0]
    spherical_radius = np.array([lamb_, phi_, rho_])
    return spherical_radius


def llh2ecef(lat: float, lon: float, elev: float) -> Tuple[float,
                                                           float,
                                                           float]:
    """
    Transform lon, lat, height to ecef x y z
    """
    # Source: https://www.mathworks.com/help/aeroblks/llatoecefposition.html
    lambda_s = math.atan(math.pow(1-F, 2)*math.tan(lat))
    rs = ECUATORIAL/math.sqrt(1+((1/(1-F)**2)-1) * math.sin(lambda_s) ** 2)
    x = (rs+elev)*math.cos(lambda_s)*math.cos(lon)
    y = (rs*math.cos(lambda_s)+elev*math.cos(lat)) * math.sin(lon)
    z = rs*math.sin(lambda_s)+elev*math.sin(lon)
    return x, y, z


def ecef2llh(
        x: float,
        y: float,
        z: float) -> Tuple[float, float, float]:
    """
    Transform x, y, z to latitude, longitude, height
    """
    # ECEF coordinates to (longitude, latitude, ellipsoidal_height)
    aux = math.sqrt(x*x + y*y)
    alpha = aux/ECUATORIAL
    beta = z/aux
    mu = beta
    aux1 = beta - mu*(1 - E_2/(alpha*math.sqrt(1 + mu*mu*(1.0 - E_2))))
    while abs(aux1) > 1.0e-12:
        mu2 = mu*mu
        aux2 = math.sqrt(1 + mu2*(1.0 - E_2))
        aux1 = beta - mu*(1 - E_2/(alpha*aux2))
        mu += aux1/(1 - E_2/(alpha*aux2*aux2*aux2))
    mu2 = mu*mu
    lon, lat = RD2DG*math.atan2(y, x) % 360, RD2DG*math.atan(mu)
    if lon > 180:
        lon -= 360
    return (lon,
            lat,
            math.sqrt(1 + mu2)*(aux - ECUATORIAL/math.sqrt(1 + mu2*(1 - E_2))))


def ecef2neu(P0: Tuple[float, float],
             dx: float,
             dy: float,
             dz: float) -> Dict[str, float]:
    lat0 = P0[0]
    lon0 = P0[1]
    sin_lat0 = math.sin(lat0)
    sin_lon0 = math.sin(lon0)
    cos_lat0 = math.cos(lat0)
    cos_lon0 = math.cos(lon0)
    nt = -sin_lat0*cos_lon0*dx-sin_lat0 * \
        sin_lon0*dy+cos_lat0*dz  # [m]
    et = -sin_lon0*dx+cos_lon0*dy  # [m]
    ut = cos_lat0*cos_lon0*dx+cos_lat0 * \
        sin_lon0*dy+sin_lat0*dz  # [m]
    return dict(N=nt, E=et, U=ut)


def get_from_ecef(ECEF_DATA: Dict[str, Dict[str,float]]
                  ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    x = None
    y = None
    z = None
    try:
        ecef = ECEF_DATA['ECEF']
        if 'X' in ecef:
            x = ecef['X']
            y = ecef['Y']
            z = ecef['Z']
        elif 'X_POS' in ecef:
            x = ecef['X_POS']
            y = ecef['Y_POS']
            z = ecef['Z_POS']
    except Exception as ex:
        print("get from ecef execption %s" % ex)
        raise ex
    return x, y, z


def get_vcv_matrix(VCV: Dict[str, float]) -> Matrix:
    xx = VCV['VCV_XX']
    yy = VCV['VCV_YY']
    zz = VCV['VCV_ZZ']
    xy = VCV['VCV_XY']
    xz = VCV['VCV_XZ']
    yz = VCV['VCV_YZ']
    cov_xyz = np.array([[xx, xy, xz],
                        [xy, yy, yz],
                        [xz, yz, zz]])
    return cov_xyz


def rotate_vcv(R: Matrix, VCV: Matrix) -> Matrix:
    return R.dot(VCV.dot(R.T))


def vcv2dict(C: Matrix) -> Dict[str, float]:
    return {'EE': C[0][0],
            'EN': C[0][1],
            'EU': C[0][2],
            'NN': C[1][1],
            'NU': C[1][2],
            'UU': C[2][2], }


def all_in_one_vcv(R: Matrix, POSITION_VCV: Dict[str, float]) -> Dict[str, float]:
    vcv = get_vcv_matrix(POSITION_VCV)
    C = rotate_vcv(R, vcv)
    vcv_dict = vcv2dict(C)
    return vcv_dict

# @Poncho: Fco del campo::::>




def trig(alpha: Double) -> Tuple[Double, Double]:
    r"""Cosine and sine of an angle.

    :param alpha: angle :math:`\alpha` in radians.
    :return: :math:`\cos\alpha, \, \sin\alpha`
    """
    if isinstance(alpha, float):
        return math.cos(alpha), math.sin(alpha)
    else:
        return np.cos(alpha), np.sin(alpha)


def ecef2enu_rot(lon: float, lat: float) -> Matrix:
    r"""
    Rotation matrix from ECEF to local coordinates.

    Rotation matrix from Earth-centered earth-fixed Coordinates to
    (east, north, up). As input, uses longitude and latitude of the point
    where the transformation wants to be applied.

    .. math::
        R_{ecef2enu}(\lambda, \varphi) = \begin{bmatrix}
        -\sin\lambda & \cos\lambda & 0 \\
        -\sin\varphi\cos\lambda & -\sin\varphi\sin\lambda & \cos\varphi \\
        \cos\varphi\cos\lambda & \cos\varphi\sin\lambda & \sin\varphi
        \end{bmatrix}

        \vec{r}_{enu} = R_{ecef2enu}(\lambda, \varphi) \vec{r}_{ecef}

    :param lon: longitude in degrees :math:`\lambda`.
    :param lat: latitude in degrees :math:`\varphi`
    :type lon: float
    :type lat: float
    :return: rotation matrix :math:`R_{ecef2enu}(\varphi, \lambda)`.
    :rtype: numpy.ndarray [3][3]
    """
    cos_lon, sin_lon = trig(lon*DG2RD)
    cos_lat, sin_lat = trig(lat*DG2RD)
    return ecef2enu_rot_tr(cos_lon, sin_lon, cos_lat, sin_lat)


def ecef2enu_rot_tr(
        cos_lon: Double,
        sin_lon: Double,
        cos_lat: Double,
        sin_lat: Double) -> Matrix:
    r"""
    Rotation matrix from ECEF to local coordinates.

    Rotation matrix from Earth-centered earth-fixed Coordinates to
    (east, north, up). As input, uses trigonometric functions of longitude and
    latitude of the point where the transformation wants to be applied.

    .. math::
        R_{ecef2enu}(\lambda, \varphi) = \begin{bmatrix}
        -\sin\lambda & \cos\lambda & 0 \\
        -\sin\varphi\cos\lambda & -\sin\varphi\sin\lambda & \cos\varphi \\
        \cos\varphi\cos\lambda & \cos\varphi\sin\lambda & \sin\varphi
        \end{bmatrix}

        \vec{r}_{enu} = R_{ecef2enu}(\lambda, \varphi) \vec{r}_{ecef}

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :param cos_lat: cosine of latitude :math:`\cos\varphi`.
    :param sin_lat: sine of latitude :math:`\sin\varphi`.
    :type cos_lon: float
    :type sin_lon: float
    :type cos_lat: float
    :type sin_lat: float
    :return: rotation matrix :math:`R_{ecef2enu}(\varphi, \lambda)`.
    :rtype: numpy.ndarray [3][3]
    """
    e_, n_, v_ = enu_tr(cos_lon, sin_lon, cos_lat, sin_lat)
    return np.append([e_, n_], [v_], axis=0)


def east_north_up(lon: Double, lat: Double) -> Tuple[Matrix, Matrix, Matrix]:
    r"""East, north and vertical directions in ECEF coordinates.

    :param lon: longitude :math:`\lambda` in degrees.
    :param lat: latitude :math:`\varphi` in degrees.
    :type lon: float
    :type lat: float
    :return: unit east :math:`\hat{e}`, north :math:`\hat{n}` and up
        :math:`\hat{z}` directions. See :py:mod:`east_st`, :py:mod:`north_st`
        and :py:mod:`up_st` functions.
    :rtype: numpy.ndarray [3]
    """
    return enu_tr(*(trig(DG2RD*lon) + trig(DG2RD*lat)))


def enu_tr(cos_lon: Double,
           sin_lon: Double,
           cos_lat: Double,
           sin_lat: Double) -> Tuple[Matrix, Matrix, Matrix]:
    r"""East, north and up directions in ECEF coordinates.

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :param cos_lat: cosine of latitude :math:`\cos\varphi`.
    :param sin_lat: sine of latitude :math:`\sin\varphi`.
    :type cos_lon: float
    :type sin_lon: float
    :type cos_lat: float
    :type sin_lat: float
    :return: unit east :math:`\hat{e}`, north :math:`\hat{n}` and up
        :math:`\hat{z}` directions. See :py:mod:`east_`, :py:mod:`north_` and
        :py:mod:`up_` functions.
    :rtype: numpy.ndarray [3]
    """
    return (east_tr(cos_lon, sin_lon),
            north_tr(cos_lon, sin_lon, cos_lat, sin_lat),
            up_tr(cos_lon, sin_lon, cos_lat, sin_lat))


def east_tr(cos_lon: Double, sin_lon: Double) -> Matrix:
    r"""East direction in ECEF coordinates.

    .. math::
        \hat{e} = \begin{bmatrix} -\sin\lambda \\ \cos\lambda \\ 0
        \end{bmatrix}

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :type cos_lon: float
    :type sin_lon: float
    :return: unit east direction :math:`\hat{e}`.
    :rtype: numpy.ndarray [3]
    """
    return np.array([-sin_lon, cos_lon, 0.0])


def north_tr(
        cos_lon: Double,
        sin_lon: Double,
        cos_lat: Double,
        sin_lat: Double) -> Matrix:
    r"""North direction in ECEF coordinates.

    .. math::
        \hat{n} = \begin{bmatrix}
        -\sin\varphi\cos\lambda \\ -\sin\varphi\sin\lambda \\ \cos\varphi
        \end{bmatrix}

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :param cos_lat: cosine of latitude :math:`\cos\varphi`.
    :param sin_lat: sine of latitude :math:`\sin\varphi`.
    :type cos_lon: float
    :type sin_lon: float
    :type cos_lat: float
    :type sin_lat: float
    :return: unit north direction :math:`\hat{n}`.
    :rtype: numpy.ndarray [3]
    """
    return np.array([-sin_lat*cos_lon, -sin_lat*sin_lon, cos_lat])


def up_tr(
        cos_lon: Double,
        sin_lon: Double,
        cos_lat: Double,
        sin_lat: Double) -> Matrix:
    r"""Upwards vertical direction in ECEF coordinates.

    .. math::
        \hat{z} = \begin{bmatrix}
        \cos\varphi\cos\lambda \\ \cos\varphi\sin\lambda \\ \sin\varphi
        \end{bmatrix}

    :param cos_lon: cosine of longitude :math:`\cos\lambda`.
    :param sin_lon: sine of longitude :math:`\sin\lambda`.
    :param cos_lat: cosine of latitude :math:`\cos\varphi`.
    :param sin_lat: sine of latitude :math:`\sin\varphi`.
    :type cos_lon: float
    :type sin_lon: float
    :type cos_lat: float
    :type sin_lat: float
    :return: unit up direction :math:`\hat{z}`.
    :rtype: numpy.ndarray [3]
    """
    return np.array([cos_lat*cos_lon, cos_lat*sin_lon, sin_lat])


from typing import Protocol
from abc import abstractmethod

class DataItem(Protocol):
    """
    Al data type that has time mark must implements get_datetime
    """
    @abstractmethod
    def get_datetime(self) -> datetime:
        pass



@dataclass
class DataPoint:
    value: float
    error: float 

    def __add__(self, other) -> 'DataPoint':
        v = self.value + other.value
        e = self.error + other.error
        return DataPoint(v,e)

    def __truediv__(self,n:float) -> 'DataPoint':
        try:
            v = self.value / n
            e = self.error / n
            return DataPoint(v,e)
        except ZeroDivisionError as e:
            raise e

    def dict(self):
        data = asdict(self)
        data.update({"min":self.min, "max":self.max})
        return data

    @property
    def min(self):
        return self.value-self.error

    @property
    def max(self):
        return self.value+self.error


@dataclass
class NEUData:
    N: DataPoint
    E: DataPoint
    U: DataPoint

    def __add__(self, other) -> 'NEUData':
        N = self.N + other.N
        E = self.E + other.E
        U = self.U + other.U
        return NEUData(N,E,U)

    def __truediv__(self, n:float) -> 'NEUData':
        try:
            N = self.N / n
            E = self.E / n
            U = self.U / n
            return NEUData(N,E,U)
        except ZeroDivisionError as e:
            raise e


    @property
    def neu(self):
        return (self.N, self.E, self.U)

    def dict(self):
        return asdict(self)

        

@dataclass
class TimeData:
    recv: datetime 
    delta: float

    def dict(self):
        return asdict(self)

    def __add__(self, other):
        recv = max(self.recv, other.recv)
        delta = self.delta + other.delta
        return TimeData(recv, delta)

    def __truediv__(self, n:float):
        try:
            recv = self.recv
            delta = self.delta / n 
            return TimeData(recv, delta)
        except ZeroDivisionError as e:
            raise e

    @property
    def info(self):
        return (self.recv, self.delta)



BASIC = Union[str, int, datetime, float]
GEODATA_TYPES = Union[BASIC, Dict[str,BASIC]]

@dataclass
class GeoData(DataItem):
    source: str
    station: str
    timestamp: int
    dt_gen: datetime
    data: NEUData
    time: TimeData

    @property
    def N(self):
        return self.data.N

    @property
    def E(self):
        return self.data.E

    @property
    def U(self):
        return self.data.U


    def __add__(self, other) -> 'GeoData':
        if self.station ==  other.station:
            timestamp = max(self.timestamp, other.timestamp)
            dt_gen = max(self.dt_gen, other.dt_gen)
            if self.source != other.source:
                self.source += f":{other.source}"
            data = self.data + other.data
            time = self.time + other.time
        return GeoData(
            self.source,
            self.station,
            timestamp,
            dt_gen,
            data,
            time)


    def __truediv__(self, n:float) -> 'GeoData':
        try:
            timestamp = self.timestamp
            dt_gen = self.dt_gen
            time = self.time / n
            data = self.data / n
            return GeoData(
                self.source,
                self.station,
                timestamp,
                dt_gen,
                data,
                time)
        except ZeroDivisionError as e:
            raise e


    def dict(self) -> Dict[str, GEODATA_TYPES]:
        return asdict(self)


    def get_datetime(self) -> datetime:
        """
        Must follow  a protocol
        """
        return self.dt_gen


