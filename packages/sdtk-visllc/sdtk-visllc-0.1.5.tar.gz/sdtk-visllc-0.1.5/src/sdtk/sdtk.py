#    Copyright (C) 2019 Vis LLC - All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
#
#    Simple Data Toolkit (SDTK) - Source code can be found on SourceForge.net
#

import sys

import math as python_lib_Math
import math as Math
import inspect as python_lib_Inspect
import sys as python_lib_Sys
import builtins as python_lib_Builtins
import functools as python_lib_Functools
import json as python_lib_Json
import os as python_lib_Os
import re as python_lib_Re
import subprocess as python_lib_Subprocess
import time as python_lib_Time
import traceback as python_lib_Traceback
from datetime import datetime as python_lib_datetime_Datetime
from datetime import timezone as python_lib_datetime_Timezone
from io import BufferedReader as python_lib_io_BufferedReader
from io import BufferedWriter as python_lib_io_BufferedWriter
from io import StringIO as python_lib_io_StringIO
from io import TextIOWrapper as python_lib_io_TextIOWrapper
from subprocess import Popen as python_lib_subprocess_Popen


class _hx_AnonObject:
    _hx_disable_getattr = False
    def __init__(self, fields):
        self.__dict__ = fields
    def __repr__(self):
        return repr(self.__dict__)
    def __contains__(self, item):
        return item in self.__dict__
    def __getitem__(self, item):
        return self.__dict__[item]
    def __getattr__(self, name):
        if (self._hx_disable_getattr):
            raise AttributeError('field does not exist')
        else:
            return None
    def _hx_hasattr(self,field):
        self._hx_disable_getattr = True
        try:
            getattr(self, field)
            self._hx_disable_getattr = False
            return True
        except AttributeError:
            self._hx_disable_getattr = False
            return False



class Enum:
    _hx_class_name = "Enum"
    __slots__ = ("tag", "index", "params")
    _hx_fields = ["tag", "index", "params"]
    _hx_methods = ["__str__"]

    def __init__(self,tag,index,params):
        self.tag = tag
        self.index = index
        self.params = params

    def __str__(self):
        if (self.params is None):
            return self.tag
        else:
            return self.tag + '(' + (', '.join(str(v) for v in self.params)) + ')'

Enum._hx_class = Enum


class Class: pass


class Date:
    _hx_class_name = "Date"
    __slots__ = ("date", "dateUTC")
    _hx_fields = ["date", "dateUTC"]
    _hx_methods = ["toString"]
    _hx_statics = ["now", "fromTime", "makeLocal", "fromString"]

    def __init__(self,year,month,day,hour,_hx_min,sec):
        self.dateUTC = None
        if (year < python_lib_datetime_Datetime.min.year):
            year = python_lib_datetime_Datetime.min.year
        if (day == 0):
            day = 1
        self.date = Date.makeLocal(python_lib_datetime_Datetime(year,(month + 1),day,hour,_hx_min,sec,0))
        self.dateUTC = self.date.astimezone(python_lib_datetime_Timezone.utc)

    def toString(self):
        return self.date.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def now():
        d = Date(2000,0,1,0,0,0)
        d.date = Date.makeLocal(python_lib_datetime_Datetime.now())
        d.dateUTC = d.date.astimezone(python_lib_datetime_Timezone.utc)
        return d

    @staticmethod
    def fromTime(t):
        d = Date(2000,0,1,0,0,0)
        d.date = Date.makeLocal(python_lib_datetime_Datetime.fromtimestamp((t / 1000.0)))
        d.dateUTC = d.date.astimezone(python_lib_datetime_Timezone.utc)
        return d

    @staticmethod
    def makeLocal(date):
        try:
            return date.astimezone()
        except BaseException as _g:
            None
            tzinfo = python_lib_datetime_Datetime.now(python_lib_datetime_Timezone.utc).astimezone().tzinfo
            return date.replace(**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'tzinfo': tzinfo})))

    @staticmethod
    def fromString(s):
        _g = len(s)
        if (_g == 8):
            k = s.split(":")
            return Date.fromTime((((Std.parseInt((k[0] if 0 < len(k) else None)) * 3600000.) + ((Std.parseInt((k[1] if 1 < len(k) else None)) * 60000.))) + ((Std.parseInt((k[2] if 2 < len(k) else None)) * 1000.))))
        elif (_g == 10):
            k = s.split("-")
            return Date(Std.parseInt((k[0] if 0 < len(k) else None)),(Std.parseInt((k[1] if 1 < len(k) else None)) - 1),Std.parseInt((k[2] if 2 < len(k) else None)),0,0,0)
        elif (_g == 19):
            k = s.split(" ")
            _this = (k[0] if 0 < len(k) else None)
            y = _this.split("-")
            _this = (k[1] if 1 < len(k) else None)
            t = _this.split(":")
            return Date(Std.parseInt((y[0] if 0 < len(y) else None)),(Std.parseInt((y[1] if 1 < len(y) else None)) - 1),Std.parseInt((y[2] if 2 < len(y) else None)),Std.parseInt((t[0] if 0 < len(t) else None)),Std.parseInt((t[1] if 1 < len(t) else None)),Std.parseInt((t[2] if 2 < len(t) else None)))
        else:
            raise haxe_Exception.thrown(("Invalid date format : " + ("null" if s is None else s)))

Date._hx_class = Date


class DateTools:
    _hx_class_name = "DateTools"
    __slots__ = ()
    _hx_statics = ["DAY_SHORT_NAMES", "DAY_NAMES", "MONTH_SHORT_NAMES", "MONTH_NAMES", "__format_get", "__format", "format"]

    @staticmethod
    def _hx___format_get(d,e):
        e1 = e
        if (e1 == "%"):
            return "%"
        elif (e1 == "A"):
            return python_internal_ArrayImpl._get(DateTools.DAY_NAMES, HxOverrides.mod(d.date.isoweekday(), 7))
        elif (e1 == "B"):
            return python_internal_ArrayImpl._get(DateTools.MONTH_NAMES, (d.date.month - 1))
        elif (e1 == "C"):
            x = (d.date.year / 100)
            tmp = None
            try:
                tmp = int(x)
            except BaseException as _g:
                None
                tmp = None
            return StringTools.lpad(Std.string(tmp),"0",2)
        elif (e1 == "D"):
            return DateTools._hx___format(d,"%m/%d/%y")
        elif (e1 == "F"):
            return DateTools._hx___format(d,"%Y-%m-%d")
        elif ((e1 == "l") or ((e1 == "I"))):
            hour = HxOverrides.mod(d.date.hour, 12)
            return StringTools.lpad(Std.string((12 if ((hour == 0)) else hour)),("0" if ((e == "I")) else " "),2)
        elif (e1 == "M"):
            return StringTools.lpad(Std.string(d.date.minute),"0",2)
        elif (e1 == "R"):
            return DateTools._hx___format(d,"%H:%M")
        elif (e1 == "S"):
            return StringTools.lpad(Std.string(d.date.second),"0",2)
        elif (e1 == "T"):
            return DateTools._hx___format(d,"%H:%M:%S")
        elif (e1 == "Y"):
            return Std.string(d.date.year)
        elif (e1 == "a"):
            return python_internal_ArrayImpl._get(DateTools.DAY_SHORT_NAMES, HxOverrides.mod(d.date.isoweekday(), 7))
        elif ((e1 == "h") or ((e1 == "b"))):
            return python_internal_ArrayImpl._get(DateTools.MONTH_SHORT_NAMES, (d.date.month - 1))
        elif (e1 == "d"):
            return StringTools.lpad(Std.string(d.date.day),"0",2)
        elif (e1 == "e"):
            return Std.string(d.date.day)
        elif ((e1 == "k") or ((e1 == "H"))):
            return StringTools.lpad(Std.string(d.date.hour),("0" if ((e == "H")) else " "),2)
        elif (e1 == "m"):
            return StringTools.lpad(Std.string(((d.date.month - 1) + 1)),"0",2)
        elif (e1 == "n"):
            return "\n"
        elif (e1 == "p"):
            if (d.date.hour > 11):
                return "PM"
            else:
                return "AM"
        elif (e1 == "r"):
            return DateTools._hx___format(d,"%I:%M:%S %p")
        elif (e1 == "s"):
            x = ((d.date.timestamp() * 1000) / 1000)
            tmp = None
            try:
                tmp = int(x)
            except BaseException as _g:
                None
                tmp = None
            return Std.string(tmp)
        elif (e1 == "t"):
            return "\t"
        elif (e1 == "u"):
            t = HxOverrides.mod(d.date.isoweekday(), 7)
            if (t == 0):
                return "7"
            else:
                return Std.string(t)
        elif (e1 == "w"):
            return Std.string(HxOverrides.mod(d.date.isoweekday(), 7))
        elif (e1 == "y"):
            return StringTools.lpad(Std.string(HxOverrides.mod(d.date.year, 100)),"0",2)
        else:
            raise haxe_exceptions_NotImplementedException((("Date.format %" + ("null" if e is None else e)) + "- not implemented yet."),None,_hx_AnonObject({'fileName': "DateTools.hx", 'lineNumber': 101, 'className': "DateTools", 'methodName': "__format_get"}))

    @staticmethod
    def _hx___format(d,f):
        r_b = python_lib_io_StringIO()
        p = 0
        while True:
            np = (f.find("%") if ((p is None)) else HxString.indexOfImpl(f,"%",p))
            if (np < 0):
                break
            _hx_len = (np - p)
            r_b.write((HxString.substr(f,p,None) if ((_hx_len is None)) else HxString.substr(f,p,_hx_len)))
            r_b.write(Std.string(DateTools._hx___format_get(d,HxString.substr(f,(np + 1),1))))
            p = (np + 2)
        _hx_len = (len(f) - p)
        r_b.write((HxString.substr(f,p,None) if ((_hx_len is None)) else HxString.substr(f,p,_hx_len)))
        return r_b.getvalue()

    @staticmethod
    def format(d,f):
        return DateTools._hx___format(d,f)
DateTools._hx_class = DateTools


class EReg:
    _hx_class_name = "EReg"
    __slots__ = ("pattern", "matchObj", "_hx_global")
    _hx_fields = ["pattern", "matchObj", "global"]

    def __init__(self,r,opt):
        self.matchObj = None
        self._hx_global = False
        options = 0
        _g = 0
        _g1 = len(opt)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            c = (-1 if ((i >= len(opt))) else ord(opt[i]))
            if (c == 109):
                options = (options | python_lib_Re.M)
            if (c == 105):
                options = (options | python_lib_Re.I)
            if (c == 115):
                options = (options | python_lib_Re.S)
            if (c == 117):
                options = (options | python_lib_Re.U)
            if (c == 103):
                self._hx_global = True
        self.pattern = python_lib_Re.compile(r,options)

EReg._hx_class = EReg


class Reflect:
    _hx_class_name = "Reflect"
    __slots__ = ()
    _hx_statics = ["field", "setField", "isFunction"]

    @staticmethod
    def field(o,field):
        return python_Boot.field(o,field)

    @staticmethod
    def setField(o,field,value):
        setattr(o,(("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field)),value)

    @staticmethod
    def isFunction(f):
        if (not ((python_lib_Inspect.isfunction(f) or python_lib_Inspect.ismethod(f)))):
            return python_Boot.hasField(f,"func_code")
        else:
            return True
Reflect._hx_class = Reflect


class Std:
    _hx_class_name = "Std"
    __slots__ = ()
    _hx_statics = ["is", "isOfType", "string", "parseInt", "shortenPossibleNumber", "parseFloat"]

    @staticmethod
    def _hx_is(v,t):
        return Std.isOfType(v,t)

    @staticmethod
    def isOfType(v,t):
        if ((v is None) and ((t is None))):
            return False
        if (t is None):
            return False
        if ((type(t) == type) and (t == Dynamic)):
            return (v is not None)
        isBool = isinstance(v,bool)
        if (((type(t) == type) and (t == Bool)) and isBool):
            return True
        if ((((not isBool) and (not ((type(t) == type) and (t == Bool)))) and ((type(t) == type) and (t == Int))) and isinstance(v,int)):
            return True
        vIsFloat = isinstance(v,float)
        tmp = None
        tmp1 = None
        if (((not isBool) and vIsFloat) and ((type(t) == type) and (t == Int))):
            f = v
            tmp1 = (((f != Math.POSITIVE_INFINITY) and ((f != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(f)))
        else:
            tmp1 = False
        if tmp1:
            tmp1 = None
            try:
                tmp1 = int(v)
            except BaseException as _g:
                None
                tmp1 = None
            tmp = (v == tmp1)
        else:
            tmp = False
        if ((tmp and ((v <= 2147483647))) and ((v >= -2147483648))):
            return True
        if (((not isBool) and ((type(t) == type) and (t == Float))) and isinstance(v,(float, int))):
            return True
        if ((type(t) == type) and (t == str)):
            return isinstance(v,str)
        isEnumType = ((type(t) == type) and (t == Enum))
        if ((isEnumType and python_lib_Inspect.isclass(v)) and hasattr(v,"_hx_constructs")):
            return True
        if isEnumType:
            return False
        isClassType = ((type(t) == type) and (t == Class))
        if ((((isClassType and (not isinstance(v,Enum))) and python_lib_Inspect.isclass(v)) and hasattr(v,"_hx_class_name")) and (not hasattr(v,"_hx_constructs"))):
            return True
        if isClassType:
            return False
        tmp = None
        try:
            tmp = isinstance(v,t)
        except BaseException as _g:
            None
            tmp = False
        if tmp:
            return True
        if python_lib_Inspect.isclass(t):
            cls = t
            loop = None
            def _hx_local_1(intf):
                f = (intf._hx_interfaces if (hasattr(intf,"_hx_interfaces")) else [])
                if (f is not None):
                    _g = 0
                    while (_g < len(f)):
                        i = (f[_g] if _g >= 0 and _g < len(f) else None)
                        _g = (_g + 1)
                        if (i == cls):
                            return True
                        else:
                            l = loop(i)
                            if l:
                                return True
                    return False
                else:
                    return False
            loop = _hx_local_1
            currentClass = v.__class__
            result = False
            while (currentClass is not None):
                if loop(currentClass):
                    result = True
                    break
                currentClass = python_Boot.getSuperClass(currentClass)
            return result
        else:
            return False

    @staticmethod
    def string(s):
        return python_Boot.toString1(s,"")

    @staticmethod
    def parseInt(x):
        if (x is None):
            return None
        try:
            return int(x)
        except BaseException as _g:
            None
            base = 10
            _hx_len = len(x)
            foundCount = 0
            sign = 0
            firstDigitIndex = 0
            lastDigitIndex = -1
            previous = 0
            _g = 0
            _g1 = _hx_len
            while (_g < _g1):
                i = _g
                _g = (_g + 1)
                c = (-1 if ((i >= len(x))) else ord(x[i]))
                if (((c > 8) and ((c < 14))) or ((c == 32))):
                    if (foundCount > 0):
                        return None
                    continue
                else:
                    c1 = c
                    if (c1 == 43):
                        if (foundCount == 0):
                            sign = 1
                        elif (not (((48 <= c) and ((c <= 57))))):
                            if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                                break
                    elif (c1 == 45):
                        if (foundCount == 0):
                            sign = -1
                        elif (not (((48 <= c) and ((c <= 57))))):
                            if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                                break
                    elif (c1 == 48):
                        if (not (((foundCount == 0) or (((foundCount == 1) and ((sign != 0))))))):
                            if (not (((48 <= c) and ((c <= 57))))):
                                if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                                    break
                    elif ((c1 == 120) or ((c1 == 88))):
                        if ((previous == 48) and ((((foundCount == 1) and ((sign == 0))) or (((foundCount == 2) and ((sign != 0))))))):
                            base = 16
                        elif (not (((48 <= c) and ((c <= 57))))):
                            if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                                break
                    elif (not (((48 <= c) and ((c <= 57))))):
                        if (not (((base == 16) and ((((97 <= c) and ((c <= 122))) or (((65 <= c) and ((c <= 90))))))))):
                            break
                if (((foundCount == 0) and ((sign == 0))) or (((foundCount == 1) and ((sign != 0))))):
                    firstDigitIndex = i
                foundCount = (foundCount + 1)
                lastDigitIndex = i
                previous = c
            if (firstDigitIndex <= lastDigitIndex):
                digits = HxString.substring(x,firstDigitIndex,(lastDigitIndex + 1))
                try:
                    return (((-1 if ((sign == -1)) else 1)) * int(digits,base))
                except BaseException as _g:
                    return None
            return None

    @staticmethod
    def shortenPossibleNumber(x):
        r = ""
        _g = 0
        _g1 = len(x)
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            c = ("" if (((i < 0) or ((i >= len(x))))) else x[i])
            _g2 = HxString.charCodeAt(c,0)
            if (_g2 is None):
                break
            else:
                _g3 = _g2
                if (((((((((((_g3 == 57) or ((_g3 == 56))) or ((_g3 == 55))) or ((_g3 == 54))) or ((_g3 == 53))) or ((_g3 == 52))) or ((_g3 == 51))) or ((_g3 == 50))) or ((_g3 == 49))) or ((_g3 == 48))) or ((_g3 == 46))):
                    r = (("null" if r is None else r) + ("null" if c is None else c))
                else:
                    break
        return r

    @staticmethod
    def parseFloat(x):
        try:
            return float(x)
        except BaseException as _g:
            None
            if (x is not None):
                r1 = Std.shortenPossibleNumber(x)
                if (r1 != x):
                    return Std.parseFloat(r1)
            return Math.NaN
Std._hx_class = Std


class Float: pass


class Int: pass


class Bool: pass


class Dynamic: pass


class StringBuf:
    _hx_class_name = "StringBuf"
    __slots__ = ("b",)
    _hx_fields = ["b"]
    _hx_methods = ["get_length", "toString"]

    def __init__(self):
        self.b = python_lib_io_StringIO()

    def get_length(self):
        pos = self.b.tell()
        self.b.seek(0,2)
        _hx_len = self.b.tell()
        self.b.seek(pos,0)
        return _hx_len

    def toString(self):
        return self.b.getvalue()

StringBuf._hx_class = StringBuf


class StringTools:
    _hx_class_name = "StringTools"
    __slots__ = ()
    _hx_statics = ["isSpace", "ltrim", "rtrim", "trim", "lpad", "replace"]

    @staticmethod
    def isSpace(s,pos):
        if (((len(s) == 0) or ((pos < 0))) or ((pos >= len(s)))):
            return False
        c = HxString.charCodeAt(s,pos)
        if (not (((c > 8) and ((c < 14))))):
            return (c == 32)
        else:
            return True

    @staticmethod
    def ltrim(s):
        l = len(s)
        r = 0
        while ((r < l) and StringTools.isSpace(s,r)):
            r = (r + 1)
        if (r > 0):
            return HxString.substr(s,r,(l - r))
        else:
            return s

    @staticmethod
    def rtrim(s):
        l = len(s)
        r = 0
        while ((r < l) and StringTools.isSpace(s,((l - r) - 1))):
            r = (r + 1)
        if (r > 0):
            return HxString.substr(s,0,(l - r))
        else:
            return s

    @staticmethod
    def trim(s):
        return StringTools.ltrim(StringTools.rtrim(s))

    @staticmethod
    def lpad(s,c,l):
        if (len(c) <= 0):
            return s
        buf = StringBuf()
        l = (l - len(s))
        while (buf.get_length() < l):
            s1 = Std.string(c)
            buf.b.write(s1)
        s1 = Std.string(s)
        buf.b.write(s1)
        return buf.b.getvalue()

    @staticmethod
    def replace(s,sub,by):
        _this = (list(s) if ((sub == "")) else s.split(sub))
        return by.join([python_Boot.toString1(x1,'') for x1 in _this])
StringTools._hx_class = StringTools


class Sys:
    _hx_class_name = "Sys"
    __slots__ = ()
    _hx_statics = ["environ", "get_environ", "args", "environment", "systemName"]
    environ = None

    @staticmethod
    def get_environ():
        _g = Sys.environ
        if (_g is None):
            environ = haxe_ds_StringMap()
            env = python_lib_Os.environ
            key = python_HaxeIterator(iter(env.keys()))
            while key.hasNext():
                key1 = key.next()
                value = env.get(key1,None)
                environ.h[key1] = value
            def _hx_local_1():
                def _hx_local_0():
                    Sys.environ = environ
                    return Sys.environ
                return _hx_local_0()
            return _hx_local_1()
        else:
            env = _g
            return env

    @staticmethod
    def args():
        argv = python_lib_Sys.argv
        return argv[1:None]

    @staticmethod
    def environment():
        return Sys.get_environ()

    @staticmethod
    def systemName():
        _g = python_lib_Sys.platform
        x = _g
        if x.startswith("linux"):
            return "Linux"
        else:
            _g1 = _g
            _hx_local_0 = len(_g1)
            if (_hx_local_0 == 5):
                if (_g1 == "win32"):
                    return "Windows"
                else:
                    raise haxe_Exception.thrown("not supported platform")
            elif (_hx_local_0 == 6):
                if (_g1 == "cygwin"):
                    return "Windows"
                elif (_g1 == "darwin"):
                    return "Mac"
                else:
                    raise haxe_Exception.thrown("not supported platform")
            else:
                raise haxe_Exception.thrown("not supported platform")
Sys._hx_class = Sys

class ValueType(Enum):
    __slots__ = ()
    _hx_class_name = "ValueType"
    _hx_constructs = ["TNull", "TInt", "TFloat", "TBool", "TObject", "TFunction", "TClass", "TEnum", "TUnknown"]

    @staticmethod
    def TClass(c):
        return ValueType("TClass", 6, (c,))

    @staticmethod
    def TEnum(e):
        return ValueType("TEnum", 7, (e,))
ValueType.TNull = ValueType("TNull", 0, ())
ValueType.TInt = ValueType("TInt", 1, ())
ValueType.TFloat = ValueType("TFloat", 2, ())
ValueType.TBool = ValueType("TBool", 3, ())
ValueType.TObject = ValueType("TObject", 4, ())
ValueType.TFunction = ValueType("TFunction", 5, ())
ValueType.TUnknown = ValueType("TUnknown", 8, ())
ValueType._hx_class = ValueType


class Type:
    _hx_class_name = "Type"
    __slots__ = ()
    _hx_statics = ["getClass", "getClassName", "typeof"]

    @staticmethod
    def getClass(o):
        if (o is None):
            return None
        o1 = o
        if ((o1 is not None) and ((HxOverrides.eq(o1,str) or python_lib_Inspect.isclass(o1)))):
            return None
        if isinstance(o,_hx_AnonObject):
            return None
        if hasattr(o,"_hx_class"):
            return o._hx_class
        if hasattr(o,"__class__"):
            return o.__class__
        else:
            return None

    @staticmethod
    def getClassName(c):
        if hasattr(c,"_hx_class_name"):
            return c._hx_class_name
        else:
            if (c == list):
                return "Array"
            if (c == Math):
                return "Math"
            if (c == str):
                return "String"
            try:
                return c.__name__
            except BaseException as _g:
                None
                return None

    @staticmethod
    def typeof(v):
        if (v is None):
            return ValueType.TNull
        elif isinstance(v,bool):
            return ValueType.TBool
        elif isinstance(v,int):
            return ValueType.TInt
        elif isinstance(v,float):
            return ValueType.TFloat
        elif isinstance(v,str):
            return ValueType.TClass(str)
        elif isinstance(v,list):
            return ValueType.TClass(list)
        elif (isinstance(v,_hx_AnonObject) or python_lib_Inspect.isclass(v)):
            return ValueType.TObject
        elif isinstance(v,Enum):
            return ValueType.TEnum(v.__class__)
        elif (isinstance(v,type) or hasattr(v,"_hx_class")):
            return ValueType.TClass(v.__class__)
        elif callable(v):
            return ValueType.TFunction
        else:
            return ValueType.TUnknown
Type._hx_class = Type


class com_sdtk_calendar_CalendarInviteFormat:
    pass


class com_sdtk_calendar_AbstractCalendarInviteFormat:

    def __init__(self,sDateTimeFormat,sStartOfFile,sEndOfFile,sUID,sCreated,sStart,sEnd,sSummary,sSeparator,sLineEnd,iLimit):
        self.sDateTimeFormat = sDateTimeFormat
        self._startOfFile = sStartOfFile
        self._endOfFile = sEndOfFile
        self._uid = sUID
        self._created = sCreated
        self._start = sStart
        self._end = sEnd
        self._summary = sSummary
        self._separator = sSeparator
        self._lineEnd = sLineEnd
        self._limit = iLimit

    def convertDateTime(self,dDateTime):
        return DateTools.format(dDateTime,self.sDateTimeFormat)

    def toDateTime(self,sValue):
        try:
            return Date(Std.parseInt(HxString.substring(sValue,0,4)),Std.parseInt(HxString.substr(sValue,4,2)),Std.parseInt(HxString.substr(sValue,6,2)),Std.parseInt(HxString.substr(sValue,9,2)),Std.parseInt(HxString.substr(sValue,11,2)),Std.parseInt(HxString.substr(sValue,13,2)))
        except BaseException as _g:
            None
            return None

    def convert(self,ciInvite,wWriter):
        wWriter.start()
        if (self._startOfFile is not None):
            wWriter.write(self._startOfFile)
        if ((self._uid is not None) and ((ciInvite.uid is not None))):
            wWriter.write(self._uid)
            wWriter.write(self._separator)
            wWriter.write(ciInvite.uid)
            wWriter.write(self._lineEnd)
        if ((self._created is not None) and ((ciInvite.created is not None))):
            wWriter.write(self._created)
            wWriter.write(self._separator)
            wWriter.write(self.convertDateTime(ciInvite.created))
            wWriter.write(self._lineEnd)
        if ((self._start is not None) and ((ciInvite.start is not None))):
            wWriter.write(self._start)
            wWriter.write(self._separator)
            wWriter.write(self.convertDateTime(ciInvite.start))
            wWriter.write(self._lineEnd)
        if ((self._end is not None) and ((ciInvite.end is not None))):
            wWriter.write(self._end)
            wWriter.write(self._separator)
            wWriter.write(self.convertDateTime(ciInvite.end))
            wWriter.write(self._lineEnd)
        if ((self._summary is not None) and ((ciInvite.summary is not None))):
            wWriter.write(self._summary)
            wWriter.write(self._separator)
            wWriter.write(ciInvite.summary)
            wWriter.write(self._lineEnd)
        if (self._endOfFile is not None):
            wWriter.write(self._endOfFile)
        wWriter.dispose()

    def convertToString(self,ciInvite):
        wWriter = com_sdtk_std_StringWriter(None)
        self.convert(ciInvite,wWriter)
        return wWriter.toString()

    def read(self,rReader):
        ciInvite = com_sdtk_calendar_CalendarInvite()
        sbBuffer = StringBuf()
        sCurrentLabel = ""
        rReader.start()
        while rReader.hasNext():
            c = rReader.next()
            if (c == self._lineEnd):
                if (sbBuffer.get_length() > 0):
                    sValue = sbBuffer.b.getvalue()
                    if (sCurrentLabel == self._uid):
                        ciInvite.uid = sValue
                    elif (sCurrentLabel == self._created):
                        ciInvite.created = self.toDateTime(sValue)
                    elif (sCurrentLabel == self._start):
                        ciInvite.start = self.toDateTime(sValue)
                    elif (sCurrentLabel == self._end):
                        ciInvite.end = self.toDateTime(sValue)
                    elif (sCurrentLabel == self._summary):
                        ciInvite.summary = sValue
                    sbBuffer = StringBuf()
            elif (c == self._separator):
                sLabel = sbBuffer.b.getvalue()
                sbBuffer = StringBuf()
            elif (sbBuffer.get_length() < self._limit):
                s = Std.string(c)
                sbBuffer.b.write(s)
        return ciInvite


class com_sdtk_calendar_CalendarInvite:

    def __init__(self):
        self.uid = None
        self.summary = None
        self.end = None
        self.start = None
        self.created = None


class com_sdtk_calendar_ConsoleFormat(com_sdtk_calendar_AbstractCalendarInviteFormat):

    def __init__(self):
        super().__init__("%y-%m-%d T%H%M%SZ",None,None,"UID","Created","Start","End","Summary",": ","\n",1024)


class com_sdtk_calendar_Create:

    @staticmethod
    def main():
        pParameters = com_sdtk_calendar_Parameters()
        if pParameters.getNothing():
            cifOutputFormat = com_sdtk_calendar_ICS.instance
            cifOutputFormat.convert(pParameters.getInvite(),com_sdtk_std_StdoutWriter())
        elif pParameters.getInvalid():
            return
        elif ((pParameters.getInput() is not None) and ((pParameters.getOutput() is not None))):
            cifInputFormat = com_sdtk_calendar_ICS.instance
            cifOutputFormat = com_sdtk_calendar_ICS.instance
            ciInvite = cifInputFormat.read(com_sdtk_std_FileReader(pParameters.getInput()))
            cifOutputFormat.convert(ciInvite,com_sdtk_std_FileWriter(pParameters.getOutput(),False))
        elif (pParameters.getInput() is not None):
            cifInputFormat = com_sdtk_calendar_ICS.instance
            ciInvite = cifInputFormat.read(com_sdtk_std_FileReader(pParameters.getInput()))
            cifOutputFormat = com_sdtk_calendar_ConsoleFormat.instance
            cifOutputFormat.convert(ciInvite,com_sdtk_std_StdoutWriter())
        else:
            cifOutputFormat = com_sdtk_calendar_ICS.instance
            cifOutputFormat.convert(pParameters.getInvite(),com_sdtk_std_FileWriter(pParameters.getOutput(),False))


class com_sdtk_calendar_ICS(com_sdtk_calendar_AbstractCalendarInviteFormat):

    def __init__(self):
        super().__init__("%y%m%dT%H%M%SZ","BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//hacksw/handcal//NONSGML v1.0//EN\nBEGIN:VEVENT\n","END:VEVENT\nEND:VCALENDAR","UID","DTSTAMP","DTSTART","DTEND","SUMMARY",":","\n",1024)


class com_sdtk_std_Parameters:

    def __init__(self):
        self._arguments = None
        self.getArguments()

    def getArguments(self):
        self._arguments = Sys.args()

    def getParameter(self,i):
        try:
            return (self._arguments[i] if i >= 0 and i < len(self._arguments) else None)
        except BaseException as _g:
            None
            return None


class com_sdtk_calendar_Parameters(com_sdtk_std_Parameters):

    def __init__(self):
        self._invalid = None
        self._nothing = None
        self._output = None
        self._input = None
        self._format = None
        self._invite = None
        super().__init__()
        ciInvite = com_sdtk_calendar_CalendarInvite()
        iDates = 0
        iText = 0
        sFiles = list()
        regexp = EReg("[.]ics$","i")
        i = 0
        sParameter = None
        while True:
            sParameter = self.getParameter(i)
            if (sParameter is not None):
                dDate = None
                try:
                    dDate = Date.fromString(sParameter)
                    tmp = None
                    if (not dDate.toString().startswith("NaN")):
                        _hx_str = ("" + Std.string(dDate.date.year))
                        startIndex = None
                        tmp = (((sParameter.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sParameter,_hx_str,startIndex))) < 0)
                    else:
                        tmp = True
                    if tmp:
                        dDate = None
                except BaseException as _g:
                    None
                if (dDate is not None):
                    iDates1 = iDates
                    if (iDates1 == 0):
                        ciInvite.start = dDate
                        self._invite = ciInvite
                    elif (iDates1 == 1):
                        ciInvite.end = dDate
                        self._invite = ciInvite
                    else:
                        pass
                    iDates = (iDates + 1)
                else:
                    regexp.matchObj = python_lib_Re.search(regexp.pattern,sParameter)
                    if (regexp.matchObj is not None):
                        sFiles.append(sParameter)
                    else:
                        if (iText == 0):
                            ciInvite.summary = sParameter
                            self._invite = ciInvite
                        iText = (iText + 1)
            i = (i + 1)
            if (not ((sParameter is not None))):
                break
        if (((len(sFiles) == 0) and ((iText > 0))) and ((iDates > 0))):
            self._nothing = True
            self._invalid = False
        elif (((len(sFiles) == 1) and ((iText > 0))) and ((iDates > 0))):
            self._output = (sFiles[0] if 0 < len(sFiles) else None)
            self._nothing = False
            self._invalid = False
        elif (((len(sFiles) == 1) and ((iText == 0))) and ((iDates == 0))):
            self._input = (sFiles[0] if 0 < len(sFiles) else None)
            self._nothing = False
            self._invalid = False
        elif (len(sFiles) == 2):
            self._input = (sFiles[0] if 0 < len(sFiles) else None)
            self._output = (sFiles[1] if 1 < len(sFiles) else None)
            self._nothing = False
            self._invalid = False
        else:
            self._invalid = True
            self._nothing = False

    def getInvite(self):
        return self._invite

    def getOutput(self):
        return self._output

    def getInput(self):
        return self._input

    def getNothing(self):
        return self._nothing

    def getInvalid(self):
        return self._invalid


class com_sdtk_calendar_TableFormat:

    def __init__(self):
        self.sDateTimeFormat = None

    def convertDateTime(self,dDateTime):
        return DateTools.format(dDateTime,self.sDateTimeFormat)

    def toDateTime(self,sValue):
        try:
            return Date(Std.parseInt(HxString.substring(sValue,0,4)),Std.parseInt(HxString.substr(sValue,4,2)),Std.parseInt(HxString.substr(sValue,6,2)),Std.parseInt(HxString.substr(sValue,9,2)),Std.parseInt(HxString.substr(sValue,11,2)),Std.parseInt(HxString.substr(sValue,13,2)))
        except BaseException as _g:
            None
            return None

    def convert(self,ciInvite,wWriter):
        pass

    def convertToString(self,ciInvite):
        return ""

    def read(self,rReader):
        ciInvite = com_sdtk_calendar_CalendarInvite()
        return ciInvite


class com_sdtk_graphs_GrapherInterface:
    pass


class com_sdtk_graphs_Grapher:

    def __init__(self,options):
        self._lastI = None
        self._lastX = None
        self._convertedData = None
        self._originY = None
        self._originX = None
        self._changed = None
        self._coordinates = None
        self._locationsX = None
        self._locationsY = None
        self._tileHeight = None
        self._tileWidth = None
        fo = options.toMap()
        width = fo.h.get("tileWidth",None)
        height = fo.h.get("tileHeight",None)
        shiftX = fo.h.get("shiftX",None)
        shiftY = fo.h.get("shiftY",None)
        self._plotFunction = fo.h.get("plotFunction",None)
        self._plotType = fo.h.get("plotType",None)
        if (shiftX is None):
            shiftX = 0
        if (shiftY is None):
            shiftY = 0
        self._shiftX = shiftX
        self._shiftY = shiftY
        self._reader = fo.h.get("reader",None)
        self._dataX = fo.h.get("dataX",None)
        self._dataY = fo.h.get("dataY",None)
        self._dataByIndex = fo.h.get("dataByIndex",None)
        self._fillGap = False
        if ((self._plotFunction is None) and ((self._reader is not None))):
            self._plotFunction = self.plotForData

    def updateLocations(self):
        self._convertedData = com_sdtk_graphs_Grapher._updateData(self._convertedData,self._reader,self._plotType,self._dataByIndex,self._dataX,self._dataY)
        results = com_sdtk_graphs_Grapher._updateLocations(self._originX,self._originY,1,1,self._tileWidth,self._tileHeight,self._shiftX,self._shiftY,self._plotFunction,self._plotType,self._locationsX,self._locationsY,self._coordinates,self._convertedData)
        self._changed = results._changed
        self._locationsX = results._locationsX
        self._locationsY = results._locationsY
        self._coordinates = results._coordinates

    def exportOptions(self):
        return com_sdtk_graphs_GraphExportTypeOptions(self)

    def export(self,options,callback = None):
        return com_sdtk_graphs_Grapher._export(None,options,callback,self._originX,self._originY,1,1,self._tileWidth,self._tileHeight,self._shiftX,self._shiftY,self._plotType,self._locationsX,self._locationsY,self._coordinates,self._convertedData)

    def plotForData(self,x):
        return com_sdtk_graphs_Grapher._plotForData(x,self._convertedData)

    @staticmethod
    def create(options):
        return com_sdtk_graphs_Grapher(options)

    @staticmethod
    def options():
        return com_sdtk_graphs_GrapherOptions()

    @staticmethod
    def _updateData(convertedData,reader,plotType,dataByIndex,dataX,dataY):
        if ((reader is not None) and ((convertedData is None))):
            if dataByIndex:
                convertedData = com_sdtk_graphs_Grapher.convertDataForPlotByColumnIndex(reader,plotType,dataX,dataY)
            else:
                convertedData = com_sdtk_graphs_Grapher.convertDataForPlotByColumnName(reader,plotType,dataX,dataY)
        return convertedData

    @staticmethod
    def _updateLocations(originX,originY,rectWidth,rectHeight,tileWidth,tileHeight,shiftX,shiftY,plotFunction,plotType,_locationsX,_locationsY,_coordinates,convertedData):
        results = com_sdtk_graphs_GrapherUpdateLocationsResults()
        start = -1
        end = -1
        increment = -1
        size = None
        plotType1 = plotType
        if (plotType1 == 1):
            start = (originY - shiftY)
            end = (start + tileHeight)
            increment = (1 / rectHeight)
        elif (plotType1 == 2):
            start = (originX - shiftX)
            end = (start + tileWidth)
            increment = (1 / rectWidth)
        else:
            pass
        if (convertedData is None):
            size = Math.floor(((((end - start)) / increment) + 0.5))
        else:
            size = len(convertedData)
            increment = 1
        locationsY = list()
        l = len(locationsY)
        if (l < size):
            idx = (size - 1)
            v = None
            l1 = len(locationsY)
            while (l1 < idx):
                locationsY.append(None)
                l1 = (l1 + 1)
            if (l1 == idx):
                locationsY.append(v)
            else:
                locationsY[idx] = v
        elif (l > size):
            pos = size
            _hx_len = (l - size)
            if (pos < 0):
                pos = (len(locationsY) + pos)
            if (pos < 0):
                pos = 0
            res = locationsY[pos:(pos + _hx_len)]
            del locationsY[pos:(pos + _hx_len)]
        locationsX = list()
        l = len(locationsX)
        if (l < size):
            idx = (size - 1)
            v = None
            l1 = len(locationsX)
            while (l1 < idx):
                locationsX.append(None)
                l1 = (l1 + 1)
            if (l1 == idx):
                locationsX.append(v)
            else:
                locationsX[idx] = v
        elif (l > size):
            pos = size
            _hx_len = (l - size)
            if (pos < 0):
                pos = (len(locationsX) + pos)
            if (pos < 0):
                pos = 0
            res = locationsX[pos:(pos + _hx_len)]
            del locationsX[pos:(pos + _hx_len)]
        coordinates = list()
        l = len(coordinates)
        if (l < size):
            idx = (size - 1)
            v = None
            l1 = len(coordinates)
            while (l1 < idx):
                coordinates.append(None)
                l1 = (l1 + 1)
            if (l1 == idx):
                coordinates.append(v)
            else:
                coordinates[idx] = v
        elif (l > size):
            pos = size
            _hx_len = (l - size)
            if (pos < 0):
                pos = (len(coordinates) + pos)
            if (pos < 0):
                pos = 0
            res = coordinates[pos:(pos + _hx_len)]
            del coordinates[pos:(pos + _hx_len)]
        locationUse = None
        locationResult = None
        locationCompare = None
        shiftUse = -1
        shiftResult = -1
        getCoordinates = None
        plotType1 = plotType
        if (plotType1 == 1):
            locationUse = locationsY
            locationResult = locationsX
            locationCompare = _locationsX
            shiftUse = shiftY
            shiftResult = shiftX
            def _hx_local_3(y,x):
                return ((("" + Std.string(x)) + ",") + Std.string(y))
            getCoordinates = _hx_local_3
        elif (plotType1 == 2):
            locationUse = locationsX
            locationResult = locationsY
            locationCompare = _locationsY
            shiftUse = shiftX
            shiftResult = shiftY
            def _hx_local_4(x,y):
                return ((("" + Std.string(x)) + ",") + Std.string(y))
            getCoordinates = _hx_local_4
        else:
            pass
        changed = (_locationsX is None)
        i = start
        j = 0
        while (j < size):
            result = plotFunction(i)
            python_internal_ArrayImpl._set(locationUse, j, (i + shiftUse))
            python_internal_ArrayImpl._set(locationResult, j, (result + shiftResult))
            if (convertedData is None):
                python_internal_ArrayImpl._set(coordinates, j, getCoordinates(i,result))
            else:
                python_internal_ArrayImpl._set(coordinates, j, ((Std.string(python_internal_ArrayImpl._get((convertedData[j] if j >= 0 and j < len(convertedData) else None), 0)) + " - ") + Std.string(python_internal_ArrayImpl._get((convertedData[j] if j >= 0 and j < len(convertedData) else None), 1))))
            if ((not changed) and (((locationCompare[j] if j >= 0 and j < len(locationCompare) else None) != (locationResult[j] if j >= 0 and j < len(locationResult) else None)))):
                changed = True
            i = (i + increment)
            j = (j + 1)
        results._changed = changed
        if changed:
            results._locationsX = locationsX
            results._locationsY = locationsY
            results._coordinates = coordinates
        else:
            results._locationsX = _locationsX
            results._locationsY = _locationsY
            results._coordinates = _coordinates
        return results

    @staticmethod
    def _export(exporter,options,callback = None,originX = None,originY = None,rectWidth = None,rectHeight = None,tileWidth = None,tileHeight = None,shiftX = None,shiftY = None,plotType = None,locationsX = None,locationsY = None,coordinates = None,convertedData = None):
        width = None
        height = None
        if (options is not None):
            fo = options.toMap()
            exporter = fo.h.get("type",None)
            width = fo.h.get("width",None)
            height = fo.h.get("height",None)
        sb = exporter.getTarget()
        if (width is None):
            width = Math.floor(((tileWidth * rectWidth) + 0.5))
        if (height is None):
            height = Math.floor(((tileHeight * rectHeight) + 0.5))
        start = -1
        end = -1
        increment = -1
        scale = -1
        plotType1 = plotType
        if (plotType1 == 1):
            start = originY
            end = (start + tileHeight)
            increment = (1 / rectHeight)
            scale = (height / ((tileHeight * rectHeight)))
        elif (plotType1 == 2):
            start = originX
            end = (start + tileWidth)
            increment = (1 / rectWidth)
            scale = (width / ((tileWidth * rectWidth)))
        else:
            pass
        size = None
        if (convertedData is None):
            size = Math.floor(((((end - start)) / increment) + 0.5))
        else:
            size = len(convertedData)
        exporter.start(sb,width,height)
        j = 1
        multiX = (rectWidth * scale)
        multiY = (rectHeight * scale)
        prevX = Math.floor(((python_internal_ArrayImpl._get(locationsX, (j - 1)) * multiX) + 0.5))
        prevY = Math.floor(((python_internal_ArrayImpl._get(locationsY, (j - 1)) * multiY) + 0.5))
        while (j < size):
            newX = Math.floor((((locationsX[j] if j >= 0 and j < len(locationsX) else None) * multiX) + 0.5))
            newY = Math.floor((((locationsY[j] if j >= 0 and j < len(locationsY) else None) * multiY) + 0.5))
            exporter.drawLine(sb,prevX,prevY,newX,newY)
            prevX = newX
            prevY = newY
            j = (j + 1)
        startX = originX
        startY = originY
        endX = (startX + tileWidth)
        endY = (startY + tileHeight)
        tickHeight = (rectHeight / 10)
        tickWidth = (rectWidth / 10)
        i = startX
        j = 0
        while (j < tileWidth):
            exporter.drawLine(sb,(((j + startX)) * rectWidth),((-tickHeight / 2) + ((((originY + shiftY)) * rectHeight))),(((j + startX)) * rectWidth),((tickHeight / 2) + ((((originY + shiftY)) * rectHeight))))
            if ((convertedData is not None) and ((plotType == 2))):
                exporter.setCaption(sb,python_internal_ArrayImpl._get((convertedData[j] if j >= 0 and j < len(convertedData) else None), 0))
            else:
                exporter.setCaption(sb,Std.string((j - shiftX)))
            j = (j + 1)
        j = 0
        while (j < tileHeight):
            exporter.drawLine(sb,((-tickWidth / 2) + ((((originX + shiftX)) * rectWidth))),(((j + startY)) * rectHeight),((tickWidth / 2) + ((((originX + shiftX)) * rectWidth))),(((j + startY)) * rectHeight))
            if ((convertedData is not None) and ((plotType == 1))):
                exporter.setCaption(sb,python_internal_ArrayImpl._get((convertedData[j] if j >= 0 and j < len(convertedData) else None), 1))
            else:
                exporter.setCaption(sb,Std.string((j - shiftY)))
            j = (j + 1)
        exporter.drawLine(sb,(startX * rectWidth),(((originY + shiftY)) * rectHeight),(endX * rectWidth),(((originY + shiftY)) * rectHeight))
        exporter.drawLine(sb,(((originX + shiftX)) * rectWidth),(startY * rectHeight),(((originX + shiftX)) * rectWidth),(endY * rectHeight))
        s = exporter.end(sb)
        if (callback is not None):
            callback(s)
            return None
        else:
            return s

    @staticmethod
    def convertData(columns,r):
        awWriter = com_sdtk_table_Array2DWriter.writeToExpandableArray(None)
        arr = awWriter.getArray()
        com_sdtk_table_Converter.convertWithOptions(r,None,awWriter,com_sdtk_table_Formats.ARRAY(),None,columns,None,None,columns,False,False,None,None)
        return arr

    @staticmethod
    def convertDataForPlotByColumnName(r,plotType,x,y):
        columns = list()
        plotType1 = plotType
        if (plotType1 == 1):
            columns.append(y)
            columns.append(x)
        elif (plotType1 == 2):
            columns.append(x)
            columns.append(y)
        else:
            raise haxe_Exception.thrown("Invalid direction")
        return com_sdtk_graphs_Grapher.convertData(columns,r)

    @staticmethod
    def convertDataForPlotByColumnIndex(r,plotType,x,y):
        columns = list()
        plotType1 = plotType
        if (plotType1 == 1):
            columns.append(y)
            columns.append(x)
        elif (plotType1 == 2):
            columns.append(x)
            columns.append(y)
        else:
            raise haxe_Exception.thrown("Invalid direction")
        return com_sdtk_graphs_Grapher.convertData(columns,r)

    @staticmethod
    def _plotForData(x,convertedData):
        return python_internal_ArrayImpl._get(python_internal_ArrayImpl._get(convertedData, x), 1)


class com_sdtk_graphs_GrapherUpdateLocationsResults:

    def __init__(self):
        self._coordinates = None
        self._locationsY = None
        self._locationsX = None
        self._changed = None


class com_sdtk_graphs_GraphExportTypeOptions:

    def __init__(self,view):
        self._values = haxe_ds_StringMap()
        self._view = view

    def html(self):
        return self.setType(com_sdtk_graphs_GrapherHTMLExporter.getInstance())

    def svg(self):
        return self.setType(com_sdtk_graphs_GrapherSVGExporter.getInstance())

    def tex(self):
        return self.setType(com_sdtk_graphs_GrapherTEXExporter.getInstance())

    def setType(self,t):
        self._values.h["type"] = t
        return com_sdtk_graphs_GraphExportTypeOptionsFinish(self._view,self._values)


class com_sdtk_graphs_GraphExportTypeOptionsFinish:

    def __init__(self,view,values):
        self._view = view
        self._values = values

    def width(self,width):
        self._values.h["width"] = width
        return self

    def height(self,height):
        self._values.h["height"] = height
        return self

    def toMap(self):
        return self._values

    def execute(self,callback = None):
        return self._view.export(self,callback)


class com_sdtk_graphs_GrapherExporter:
    pass


class com_sdtk_graphs_GrapherHTMLExporter:

    def __init__(self):
        pass

    def getTarget(self):
        return StringBuf()

    def start(self,sb,width,height):
        sb.b.write("<html><head><style>.line-segment { transform: rotate(calc(var(--angle) * 1deg)); transform-origin: left bottom; bottom: calc(var(--y1) * 1px); left: calc(var(--x1) * 1px); height: 1px; position: absolute; background-color: black; width: calc(var(--length) * 1px); }</style></head><body><div style=\"width:")
        s = Std.string(width)
        sb.b.write(s)
        sb.b.write("px; height: ")
        s = Std.string(height)
        sb.b.write(s)
        sb.b.write("px;\">")

    def setCaption(self,sb,caption):
        pass

    def end(self,sb):
        sb.b.write("</div></body></html>")
        return sb.b.getvalue()

    def drawLine(self,sb,x1,y1,x2,y2):
        angle = ((-Math.atan2((y2 - y1),(x2 - x1)) / Math.PI) * 180)
        v = ((((x2 - x1)) * ((x2 - x1))) + ((((y2 - y1)) * ((y2 - y1)))))
        length = (Math.NaN if ((v < 0)) else python_lib_Math.sqrt(v))
        sb.b.write("<div ")
        sb.b.write("class=\"line-segment\" ")
        sb.b.write("style=\"--x1: ")
        s = Std.string(x1)
        sb.b.write(s)
        sb.b.write("; --y1: ")
        s = Std.string(y1)
        sb.b.write(s)
        sb.b.write("; --x2: ")
        s = Std.string(x2)
        sb.b.write(s)
        sb.b.write("; --y2: ")
        s = Std.string(y2)
        sb.b.write(s)
        sb.b.write("; --angle: ")
        s = Std.string(angle)
        sb.b.write(s)
        sb.b.write("; --length: ")
        s = Std.string(length)
        sb.b.write(s)
        sb.b.write("; \"> </div>\n")

    @staticmethod
    def getInstance():
        return com_sdtk_graphs_GrapherHTMLExporter._instance


class com_sdtk_graphs_GrapherSVGExporter:

    def __init__(self):
        pass

    def getTarget(self):
        return StringBuf()

    def start(self,sb,width,height):
        sb.b.write("<svg viewBox=\"0 0 ")
        s = Std.string(width)
        sb.b.write(s)
        sb.b.write(" ")
        s = Std.string(height)
        sb.b.write(s)
        sb.b.write("\" transform=\"scale(1,-1)\" xmlns=\"http://www.w3.org/2000/svg\">")

    def setCaption(self,sb,caption):
        pass

    def end(self,sb):
        sb.b.write("</svg>")
        return sb.b.getvalue()

    def drawLine(self,sb,x1,y1,x2,y2):
        sb.b.write("<line x1=\"")
        s = Std.string(x1)
        sb.b.write(s)
        sb.b.write("\" y1=\"")
        s = Std.string(y1)
        sb.b.write(s)
        sb.b.write("\" x2=\"")
        s = Std.string(x2)
        sb.b.write(s)
        sb.b.write("\" y2=\"")
        s = Std.string(y2)
        sb.b.write(s)
        sb.b.write("\" stroke=\"black\" />\n")

    @staticmethod
    def getInstance():
        return com_sdtk_graphs_GrapherSVGExporter._instance


class com_sdtk_graphs_GrapherTEXExporter:

    def __init__(self):
        pass

    def getTarget(self):
        return StringBuf()

    def start(self,sb,width,height):
        pageHeight = 254
        pageWidth = 190.5
        adjustHeight = (pageHeight / height)
        adjustWidth = (pageWidth / width)
        sb.b.write("\\documentclass{article}\n")
        sb.b.write("\\setlength{\\unitlength}{")
        s = Std.string((adjustHeight if ((adjustHeight < adjustWidth)) else adjustWidth))
        sb.b.write(s)
        sb.b.write("mm}\n")
        sb.b.write("\\begin{document}\n")
        sb.b.write("\\begin{picture}(")
        s = Std.string(width)
        sb.b.write(s)
        sb.b.write(",")
        s = Std.string(height)
        sb.b.write(s)
        sb.b.write(")\n")

    def setCaption(self,sb,caption):
        pass

    def end(self,sb):
        sb.b.write("\\end{picture}\n")
        sb.b.write("\\end{document}\n")
        return sb.b.getvalue()

    def drawLine(self,sb,x1,y1,x2,y2):
        sb.b.write("\\qbezier(")
        s = Std.string(x1)
        sb.b.write(s)
        sb.b.write(",")
        s = Std.string(y1)
        sb.b.write(s)
        sb.b.write(")(")
        s = Std.string((((x1 + x2)) / 2))
        sb.b.write(s)
        sb.b.write(",")
        s = Std.string((((y1 + y2)) / 2))
        sb.b.write(s)
        sb.b.write(")(")
        s = Std.string(x2)
        sb.b.write(s)
        sb.b.write(",")
        s = Std.string(y2)
        sb.b.write(s)
        sb.b.write(")\n")

    @staticmethod
    def getInstance():
        return com_sdtk_graphs_GrapherTEXExporter._instance


class com_sdtk_graphs_GrapherOptions:

    def __init__(self):
        self._values = haxe_ds_StringMap()

    def plotFunctionForX(self,f):
        return com_sdtk_graphs_GrapherOptions._plotFunctionForX(com_sdtk_graphs_GrapherOptions.setOnceI,self,f)

    def plotFunctionForY(self,f):
        return com_sdtk_graphs_GrapherOptions._plotFunctionForY(com_sdtk_graphs_GrapherOptions.setOnceI,self,f)

    def plotDataByColumnNameForY(self,r,x,y):
        return com_sdtk_graphs_GrapherOptions._plotDataByColumnNameForY(com_sdtk_graphs_GrapherOptions.setOnceI,self,r,x,y)

    def plotDataByColumnNameForX(self,r,x,y):
        return com_sdtk_graphs_GrapherOptions._plotDataByColumnNameForX(com_sdtk_graphs_GrapherOptions.setOnceI,self,r,x,y)

    def plotDataByColumnIndexForY(self,r,x,y):
        return com_sdtk_graphs_GrapherOptions._plotDataByColumnIndexForY(com_sdtk_graphs_GrapherOptions.setOnceI,self,r,x,y)

    def plotDataByColumnIndexForX(self,r,x,y):
        return com_sdtk_graphs_GrapherOptions._plotDataByColumnIndexForX(com_sdtk_graphs_GrapherOptions.setOnceI,self,r,x,y)

    def positiveOnlyY(self):
        return com_sdtk_graphs_GrapherOptions._positiveOnlyY(com_sdtk_graphs_GrapherOptions.setOnceI,self)

    def negativeOnlyY(self):
        return com_sdtk_graphs_GrapherOptions._negativeOnlyY(com_sdtk_graphs_GrapherOptions.setOnceI,self)

    def positiveAndNegativeY(self):
        return com_sdtk_graphs_GrapherOptions._positiveAndNegativeY(com_sdtk_graphs_GrapherOptions.setOnceI,self)

    def positiveOnlyX(self):
        return com_sdtk_graphs_GrapherOptions._positiveOnlyX(com_sdtk_graphs_GrapherOptions.setOnceI,self)

    def negativeOnlyX(self):
        return com_sdtk_graphs_GrapherOptions._negativeOnlyX(com_sdtk_graphs_GrapherOptions.setOnceI,self)

    def positiveAndNegativeX(self):
        return com_sdtk_graphs_GrapherOptions._positiveAndNegativeX(com_sdtk_graphs_GrapherOptions.setOnceI,self)

    def setOnce(self,key,value):
        if (self._values.h.get(key,None) is None):
            self._values.h[key] = value
            return value
        else:
            raise haxe_Exception.thrown("Can only set once.")

    def toMap(self):
        return self._values

    def execute(self):
        return com_sdtk_graphs_Grapher.create(self)

    @staticmethod
    def _plotFunctionForX(setOnce,options,f):
        setOnce(options,"plotFunction",f)
        return setOnce(options,"plotType",1)

    @staticmethod
    def _plotFunctionForY(setOnce,options,f):
        setOnce(options,"plotFunction",f)
        return setOnce(options,"plotType",2)

    @staticmethod
    def _plotDataByColumnNameForY(setOnce,options,r,x,y):
        setOnce(options,"plotType",2)
        setOnce(options,"reader",r)
        setOnce(options,"dataX",x)
        setOnce(options,"dataY",y)
        return setOnce(options,"dataByIndex",False)

    @staticmethod
    def _plotDataByColumnNameForX(setOnce,options,r,x,y):
        setOnce(options,"plotType",1)
        setOnce(options,"reader",r)
        setOnce(options,"dataX",x)
        setOnce(options,"dataY",y)
        return setOnce(options,"dataByIndex",False)

    @staticmethod
    def _plotDataByColumnIndexForY(setOnce,options,r,x,y):
        setOnce(options,"plotType",2)
        setOnce(options,"reader",r)
        setOnce(options,"dataX",x)
        setOnce(options,"dataY",y)
        return setOnce(options,"dataByIndex",True)

    @staticmethod
    def _plotDataByColumnIndexForX(setOnce,options,r,x,y):
        setOnce(options,"plotType",1)
        setOnce(options,"reader",r)
        setOnce(options,"dataX",x)
        setOnce(options,"dataY",y)
        return setOnce(options,"dataByIndex",True)

    @staticmethod
    def _positiveOnlyY(setOnce,options):
        return setOnce(options,"centerOfY",1)

    @staticmethod
    def _negativeOnlyY(setOnce,options):
        return setOnce(options,"centerOfY",-1)

    @staticmethod
    def _positiveAndNegativeY(setOnce,options):
        return setOnce(options,"centerOfY",0)

    @staticmethod
    def _positiveOnlyX(setOnce,options):
        return setOnce(options,"centerOfX",1)

    @staticmethod
    def _negativeOnlyX(setOnce,options):
        return setOnce(options,"centerOfX",-1)

    @staticmethod
    def _positiveAndNegativeX(setOnce,options):
        return setOnce(options,"centerOfX",0)

    @staticmethod
    def setOnceI(o,key,value):
        o2 = o
        o2.setOnce(key,value)
        return o


class com_sdtk_log_Parameters(com_sdtk_std_Parameters):

    def __init__(self):
        self._outputControlId = None
        self._file = None
        self._processParams = None
        self._process = None
        self._exclude = None
        self._include = None
        self._inputMode = 0
        self._outputMode = 0
        super().__init__()
        i = 0
        sParameter = None
        while True:
            sParameter = self.getParameter(i)
            if (sParameter is not None):
                if (self._process is not None):
                    _this = self._processParams
                    _this.append(sParameter)
                else:
                    _g = sParameter.upper()
                    _hx_local_0 = len(_g)
                    if (_hx_local_0 == 11):
                        if (_g == "EVENTLOGGER"):
                            self._outputMode = 1
                        elif (_g == "EVENTVIEWER"):
                            self._outputMode = 1
                        else:
                            startIndex = None
                            iPeriod = (sParameter.find(".") if ((startIndex is None)) else HxString.indexOfImpl(sParameter,".",startIndex))
                            startIndex1 = None
                            iHash = (sParameter.find("#") if ((startIndex1 is None)) else HxString.indexOfImpl(sParameter,"#",startIndex1))
                            if ((iPeriod == 0) or ((iHash == 0))):
                                self._outputControlId = sParameter
                                self._outputMode = 3
                            elif (iPeriod < 0):
                                self._process = sParameter
                                self._inputMode = 1
                            else:
                                self._file = sParameter
                                self._inputMode = 0
                    elif (_hx_local_0 == 9):
                        if (_g == "EVENTLOGS"):
                            self._outputMode = 1
                        else:
                            startIndex = None
                            iPeriod = (sParameter.find(".") if ((startIndex is None)) else HxString.indexOfImpl(sParameter,".",startIndex))
                            startIndex1 = None
                            iHash = (sParameter.find("#") if ((startIndex1 is None)) else HxString.indexOfImpl(sParameter,"#",startIndex1))
                            if ((iPeriod == 0) or ((iHash == 0))):
                                self._outputControlId = sParameter
                                self._outputMode = 3
                            elif (iPeriod < 0):
                                self._process = sParameter
                                self._inputMode = 1
                            else:
                                self._file = sParameter
                                self._inputMode = 0
                    elif (_hx_local_0 == 5):
                        if (_g == "ALERT"):
                            self._outputMode = 2
                        elif (_g == "POPUP"):
                            self._outputMode = 2
                        elif (_g == "EVENT"):
                            self._outputMode = 1
                        else:
                            startIndex = None
                            iPeriod = (sParameter.find(".") if ((startIndex is None)) else HxString.indexOfImpl(sParameter,".",startIndex))
                            startIndex1 = None
                            iHash = (sParameter.find("#") if ((startIndex1 is None)) else HxString.indexOfImpl(sParameter,"#",startIndex1))
                            if ((iPeriod == 0) or ((iHash == 0))):
                                self._outputControlId = sParameter
                                self._outputMode = 3
                            elif (iPeriod < 0):
                                self._process = sParameter
                                self._inputMode = 1
                            else:
                                self._file = sParameter
                                self._inputMode = 0
                    elif (_hx_local_0 == 3):
                        if (_g == "POP"):
                            self._outputMode = 2
                        else:
                            startIndex = None
                            iPeriod = (sParameter.find(".") if ((startIndex is None)) else HxString.indexOfImpl(sParameter,".",startIndex))
                            startIndex1 = None
                            iHash = (sParameter.find("#") if ((startIndex1 is None)) else HxString.indexOfImpl(sParameter,"#",startIndex1))
                            if ((iPeriod == 0) or ((iHash == 0))):
                                self._outputControlId = sParameter
                                self._outputMode = 3
                            elif (iPeriod < 0):
                                self._process = sParameter
                                self._inputMode = 1
                            else:
                                self._file = sParameter
                                self._inputMode = 0
                    elif (_hx_local_0 == 7):
                        if (_g == "CONTROL"):
                            i = (i + 1)
                            self._outputControlId = self.getParameter(i)
                            self._outputMode = 3
                        elif (_g == "EXCLUDE"):
                            i = (i + 1)
                            self._exclude = self.getParameter(i)
                        elif (_g == "INCLUDE"):
                            i = (i + 1)
                            self._include = self.getParameter(i)
                        elif (_g == "VERSION"):
                            _hx_str = Std.string(("Version " + HxOverrides.stringOrNull(com_sdtk_std_Version.get())))
                            python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
                        else:
                            startIndex = None
                            iPeriod = (sParameter.find(".") if ((startIndex is None)) else HxString.indexOfImpl(sParameter,".",startIndex))
                            startIndex1 = None
                            iHash = (sParameter.find("#") if ((startIndex1 is None)) else HxString.indexOfImpl(sParameter,"#",startIndex1))
                            if ((iPeriod == 0) or ((iHash == 0))):
                                self._outputControlId = sParameter
                                self._outputMode = 3
                            elif (iPeriod < 0):
                                self._process = sParameter
                                self._inputMode = 1
                            else:
                                self._file = sParameter
                                self._inputMode = 0
                    elif (_hx_local_0 == 8):
                        if (_g == "EVENTLOG"):
                            self._outputMode = 1
                        else:
                            startIndex = None
                            iPeriod = (sParameter.find(".") if ((startIndex is None)) else HxString.indexOfImpl(sParameter,".",startIndex))
                            startIndex1 = None
                            iHash = (sParameter.find("#") if ((startIndex1 is None)) else HxString.indexOfImpl(sParameter,"#",startIndex1))
                            if ((iPeriod == 0) or ((iHash == 0))):
                                self._outputControlId = sParameter
                                self._outputMode = 3
                            elif (iPeriod < 0):
                                self._process = sParameter
                                self._inputMode = 1
                            else:
                                self._file = sParameter
                                self._inputMode = 0
                    elif (_hx_local_0 == 6):
                        if (_g == "ALERTS"):
                            self._outputMode = 2
                        elif (_g == "EVENTS"):
                            self._outputMode = 1
                        else:
                            startIndex = None
                            iPeriod = (sParameter.find(".") if ((startIndex is None)) else HxString.indexOfImpl(sParameter,".",startIndex))
                            startIndex1 = None
                            iHash = (sParameter.find("#") if ((startIndex1 is None)) else HxString.indexOfImpl(sParameter,"#",startIndex1))
                            if ((iPeriod == 0) or ((iHash == 0))):
                                self._outputControlId = sParameter
                                self._outputMode = 3
                            elif (iPeriod < 0):
                                self._process = sParameter
                                self._inputMode = 1
                            else:
                                self._file = sParameter
                                self._inputMode = 0
                    else:
                        startIndex = None
                        iPeriod = (sParameter.find(".") if ((startIndex is None)) else HxString.indexOfImpl(sParameter,".",startIndex))
                        startIndex1 = None
                        iHash = (sParameter.find("#") if ((startIndex1 is None)) else HxString.indexOfImpl(sParameter,"#",startIndex1))
                        if ((iPeriod == 0) or ((iHash == 0))):
                            self._outputControlId = sParameter
                            self._outputMode = 3
                        elif (iPeriod < 0):
                            self._process = sParameter
                            self._inputMode = 1
                        else:
                            self._file = sParameter
                            self._inputMode = 0
            i = (i + 1)
            if (sParameter is None):
                break

    def getOutputMode(self):
        return self._outputMode

    def getInputMode(self):
        return self._inputMode

    def getFileParam(self):
        return self._file

    def getProcessParams(self):
        return self._processParams

    def getProcessParam(self):
        return self._process

    def getControlParam(self):
        return self._outputControlId

    def getInclude(self):
        return self._include

    def getExclude(self):
        return self._exclude


class com_sdtk_std_DataIterable:
    pass


class com_sdtk_std_DataIterator:
    pass


class com_sdtk_std_Disposable:
    pass


class com_sdtk_std_Reader:

    def __init__(self):
        pass

    def start(self):
        pass

    def rawIndex(self):
        return -1

    def jumpTo(self,index):
        pass

    def hasNext(self):
        return False

    def next(self):
        return None

    def peek(self):
        return None

    def dispose(self):
        pass

    def iterator(self):
        return self

    def switchToLineReader(self):
        return com_sdtk_std_WholeLineReader(self)

    def unwrapOne(self):
        return self

    def unwrapAll(self):
        return self

    def reset(self):
        pass


class com_sdtk_log_ProcessReader(com_sdtk_std_Reader):

    def __init__(self,sCommand,sParameters):
        self._process = None
        super().__init__()
        self._process = sys_io_Process(sCommand,sParameters)

    def get(self):
        return self._process.stdout.readLine()

    def end(self):
        try:
            self._process.close()
        except BaseException as _g:
            None


class com_sdtk_std_Flushable:
    pass


class com_sdtk_std_Writer:

    def __init__(self):
        pass

    def start(self):
        pass

    def dispose(self):
        pass

    def flush(self):
        pass

    def write(self,_hx_str):
        pass

    def switchToLineWriter(self):
        return com_sdtk_std_WholeLineWriter(self)

    def unwrapOne(self):
        return self

    def unwrapAll(self):
        return self


class com_sdtk_log_TSFileWriter(com_sdtk_std_Writer):

    def __init__(self,sLocation):
        self._path = None
        self._location = None
        super().__init__()
        self._location = sLocation
        sSeparator = ""
        tmp = ("" if ((self._location is None)) else self._location)
        v = (self.getTimeStamp() * 1000.0)
        self._path = ((("null" if tmp is None else tmp) + ("null" if sSeparator is None else sSeparator)) + Std.string(((v if (((v == Math.POSITIVE_INFINITY) or ((v == Math.NEGATIVE_INFINITY)))) else (Math.NaN if (python_lib_Math.isnan(v)) else Math.floor(v))))))
        self._path = haxe_io_Path(self._path).toString()

    def getTimeStamp(self):
        return python_lib_Time.time()

    def write(self,sLine):
        try:
            out = sys_io_File.append(self._path,False)
            try:
                out.writeString(sLine)
                out.writeString("\n")
            except BaseException as _g:
                None
            out.close()
        except BaseException as _g:
            None


class com_sdtk_log_TimeStampWriter(com_sdtk_std_Writer):

    def __init__(self,sWrapped,sDateFormat,sEntryFormat,bIndicateStartAndEnd):
        self._indicateStartEnd = None
        self._entryFormat = None
        self._dateFormat = None
        self._wrapped = None
        super().__init__()
        self._wrapped = sWrapped
        self._dateFormat = ("%Y-%m-%d_%H:%M:%S" if ((sDateFormat is None)) else sDateFormat)
        self._entryFormat = ("%timestamp% - %entry%" if ((sEntryFormat is None)) else sEntryFormat)
        _this = self._entryFormat
        startIndex = None
        if (((_this.find("%timestamp%") if ((startIndex is None)) else HxString.indexOfImpl(_this,"%timestamp%",startIndex))) < 0):
            self._entryFormat = ("%timestamp%" + HxOverrides.stringOrNull(self._entryFormat))
        _this = self._entryFormat
        startIndex = None
        if (((_this.find("%entry%") if ((startIndex is None)) else HxString.indexOfImpl(_this,"%entry%",startIndex))) < 0):
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0._entryFormat
            _hx_local_0._entryFormat = (("null" if _hx_local_1 is None else _hx_local_1) + "%entry%")
            _hx_local_0._entryFormat
        self._indicateStartEnd = bIndicateStartAndEnd
        if self._indicateStartEnd:
            self.write("Started")

    def write(self,sLine):
        self._wrapped.write(StringTools.replace(StringTools.replace(self._entryFormat,"%timestamp%",DateTools.format(Date.now(),self._dateFormat)),"%entry%",sLine))

    def dispose(self):
        if self._indicateStartEnd:
            self.write("Ended")
        self._wrapped.dispose()


class com_sdtk_log_Transfer:

    def __init__(self):
        pass

    def transfer(self,reader,writer):
        sLine = reader.next()
        while (sLine is not None):
            writer.write(sLine)
            sLine = reader.next()
        reader.dispose()
        writer.dispose()

    @staticmethod
    def defaultTransfer(sLocation,pParameters):
        rReader = None
        wWriter = None
        _g = pParameters.getOutputMode()
        if (_g == 0):
            wWriter = com_sdtk_log_TSFileWriter(sLocation)
        elif (_g == 1):
            wWriter = com_sdtk_std_SysLogWriter()
        elif (_g == 2):
            wWriter = com_sdtk_std_PopUpWriter()
        elif (_g == 3):
            wWriter = com_sdtk_std_ControlWriter(pParameters.getControlParam())
        else:
            pass
        wWriter = wWriter.switchToLineWriter()
        _g = pParameters.getInputMode()
        if (_g == 0):
            rReader = com_sdtk_std_StdinReader()
        elif (_g == 1):
            rReader = com_sdtk_log_ProcessReader(pParameters.getProcessParam(),pParameters.getProcessParams())
        else:
            pass
        rReader = rReader.switchToLineReader()
        if ((pParameters.getInclude() is not None) or ((pParameters.getExclude() is not None))):
            frReader = com_sdtk_std_FilterReader(rReader)
            rReader = frReader
            if (pParameters.getInclude() is not None):
                frReader.addFilter(com_sdtk_std_Filter.parse(pParameters.getInclude(),False))
            if (pParameters.getExclude() is not None):
                frReader.addFilter(com_sdtk_std_Filter.parse(pParameters.getExclude(),True))
        com_sdtk_log_Transfer().transfer(rReader,wWriter)

    @staticmethod
    def main():
        pParameters = com_sdtk_log_Parameters()
        sLocation = None
        try:
            sLocation = pParameters.getFileParam()
        except BaseException as _g:
            None
        if (sLocation is None):
            sLocation = "~/Log"
        bWindows = False
        _this = Sys.systemName()
        startIndex = None
        bWindows = (((_this.find("Windows") if ((startIndex is None)) else HxString.indexOfImpl(_this,"Windows",startIndex))) >= 0)
        if bWindows:
            sLocation = StringTools.replace(StringTools.replace(sLocation,"/","\\"),"~","%userprofile%")
            env = Sys.environment()
            v = env.keys()
            while v.hasNext():
                v1 = v.next()
                val = env.h.get(v1,None)
                sLocation = StringTools.replace(sLocation,(("%" + HxOverrides.stringOrNull(v1.lower())) + "%"),val)
                sLocation = StringTools.replace(sLocation,(("%" + HxOverrides.stringOrNull(v1.upper())) + "%"),val)
        com_sdtk_log_Transfer.defaultTransfer(sLocation,pParameters)


class com_sdtk_std_Calc:

    @staticmethod
    def average(reader):
        total = 0
        count = 0
        readerI = reader.iterator()
        while readerI.hasNext():
            total = (total + readerI.next())
            count = (count + 1)
        return (total / count)

    @staticmethod
    def standardDeviation(reader,avg = None):
        if (avg is None):
            avg = com_sdtk_std_Calc.average(reader)
        total = 0
        count = 0
        reader2 = reader.iterator()
        while reader2.hasNext():
            value = reader2.next()
            total = (total + ((((value - avg)) * ((value - avg)))))
            count = (count + 1)
        v = (total / count)
        if (v < 0):
            return Math.NaN
        else:
            return python_lib_Math.sqrt(v)

    @staticmethod
    def correlation(readerI,readerJ,avgI = None,avgJ = None,sdI = None,sdJ = None):
        if (avgI is None):
            avgI = com_sdtk_std_Calc.average(readerI)
        if (avgJ is None):
            avgJ = com_sdtk_std_Calc.average(readerJ)
        if (sdI is None):
            sdI = com_sdtk_std_Calc.standardDeviation(readerI,avgI)
        if (sdJ is None):
            sdJ = com_sdtk_std_Calc.standardDeviation(readerJ,avgJ)
        count = 0
        total = 0
        readerI2 = readerI.iterator()
        readerJ2 = readerJ.iterator()
        while readerI2.hasNext():
            i = readerI2.next()
            j = readerJ2.next()
            total = (total + ((i * j)))
            count = (count + 1)
        return (((total - (((count * avgI) * avgJ)))) / (((((count - 1)) * sdI) * sdJ)))

    @staticmethod
    def regressionSlope(readerI,readerJ,avgI = None,avgJ = None,sdI = None,sdJ = None,correlationIJ = None):
        if ((avgI is None) and (((correlationIJ is None) or ((sdI is None))))):
            avgI = com_sdtk_std_Calc.average(readerI)
        if ((avgJ is None) and (((correlationIJ is None) or ((sdJ is None))))):
            avgJ = com_sdtk_std_Calc.average(readerJ)
        if (sdI is None):
            sdI = com_sdtk_std_Calc.standardDeviation(readerI,avgI)
        if (sdJ is None):
            sdJ = com_sdtk_std_Calc.standardDeviation(readerJ,avgJ)
        if (correlationIJ is None):
            correlationIJ = com_sdtk_std_Calc.correlation(readerI,readerJ,avgI,avgJ,sdI,sdJ)
        return ((correlationIJ * sdJ) / sdI)

    @staticmethod
    def regressionIntercept(readerI,readerJ,avgI = None,avgJ = None,sdI = None,sdJ = None,correlationIJ = None,slope = None):
        if (avgI is None):
            avgI = com_sdtk_std_Calc.average(readerI)
        if (avgJ is None):
            avgJ = com_sdtk_std_Calc.average(readerJ)
        if (slope is None):
            slope = com_sdtk_std_Calc.regressionSlope(readerI,readerJ,avgI,avgJ,sdI,sdJ,correlationIJ)
        return (avgJ - ((slope * avgI)))


class com_sdtk_std_StringReader(com_sdtk_std_Reader):

    def __init__(self,sValue):
        self._method = None
        self._dropping = -1
        self._index = 0
        self._value = None
        self._next = None
        super().__init__()
        self._value = sValue
        self._next = ""
        self._method = com_sdtk_std_StringReaderEachChar.instance
        self.moveToNext()

    def reset(self):
        self._index = 0
        self._next = ""
        self.moveToNext()

    def rawIndex(self):
        return self._index

    def jumpTo(self,index):
        self._index = index

    def setString(self,sValue):
        self._value = sValue

    def moveToNext(self):
        try:
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0._index
            _hx_local_0._index = (_hx_local_1 + len(self._next))
            _hx_local_0._index
            self._next = None
            if ((self._dropping > 0) and ((self._index >= self._dropping))):
                self._value = HxString.substr(self._value,self._index,None)
                self._index = 0
            self._next = self._method.moveToNext(self._index,self._value)
            if ((self._next is not None) and ((len(self._next) <= 0))):
                self._next = None
        except BaseException as _g:
            None
        if (self._next is None):
            self.dispose()

    def hasNext(self):
        return (self._next is not None)

    def next(self):
        sValue = self._next
        if (sValue is not None):
            self.moveToNext()
        return sValue

    def peek(self):
        return self._next

    def dispose(self):
        if (self._value is not None):
            self._value = None
            self._next = None
            self._index = -1

    def iterator(self):
        return self

    def switchToLineReader(self):
        self._method = com_sdtk_std_StringReaderEachLine.instance
        return self

    def unwrapOne(self):
        self._method = com_sdtk_std_StringReaderEachChar.instance
        return self

    def unwrapAll(self):
        self._method = com_sdtk_std_StringReaderEachChar.instance
        return self

    def switchToDroppingCharacters(self,chars = None):
        if (chars is None):
            chars = 10000
        self._dropping = chars
        return self


class com_sdtk_std_ControlReader(com_sdtk_std_StringReader):

    def __init__(self,sControl,bPlainText):
        self._id = None
        self._control = None
        super().__init__(com_sdtk_std_ControlReader.getValue(sControl,bPlainText))
        self._control = com_sdtk_std_ControlReader.getControl(sControl)
        self._id = sControl

    def dispose(self):
        super().dispose()
        self._control = None

    @staticmethod
    def getControl(sControl):
        return None

    @staticmethod
    def getValue(sControl,bPlainText):
        cControl = com_sdtk_std_ControlReader.getControl(sControl)
        sValue = None
        return sValue


class com_sdtk_std_ControlWriter(com_sdtk_std_Writer):

    def __init__(self,sControl):
        self._id = None
        self._control = None
        super().__init__()
        self._id = sControl

    def send(self,sLine):
        try:
            pass
        except BaseException as _g:
            None
            return

    def dispose(self):
        self._control = None


class com_sdtk_std_FileReader(com_sdtk_std_Reader):

    def __init__(self,sName):
        self._currentRawIndex = None
        self._nextRawIndex = None
        self._path = None
        self._in = None
        self._next = None
        super().__init__()
        self._path = sName
        self.reset()

    def reset(self):
        self.open()
        self._nextRawIndex = 0

    def open(self):
        self._in = open(self._path, "r")

    def rawIndex(self):
        return self._currentRawIndex

    def jumpTo(self,index):
        if (index < self._nextRawIndex):
            self.reset()
        self._in.seek((index - self._nextRawIndex))
        self._nextRawIndex = index
        self.check()

    def start(self):
        self.check()

    def check(self):
        if (self._in is not None):
            try:
                self._next = self._in.read(1)
            except BaseException as _g:
                None
                self._next = None
                self.dispose()
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0._nextRawIndex
            _hx_local_0._nextRawIndex = (_hx_local_1 + 1)
            _hx_local_1
        else:
            self._next = None

    def hasNext(self):
        return (self._next is not None)

    def next(self):
        _current = self._next
        self.check()
        return _current

    def peek(self):
        return self._next

    def close(self):
        self._in.close()

    def dispose(self):
        if (self._path is not None):
            self._path = None
            self.close()
            self._in = None

    def convertToStringReader(self):
        s = ""
        if (self._next is not None):
            s = (("null" if s is None else s) + HxOverrides.stringOrNull(self._next))
        s = (("null" if s is None else s) + Std.string(self._in.read()))
        sr = com_sdtk_std_StringReader(s)
        self.dispose()
        return sr


class com_sdtk_std_FileWriter(com_sdtk_std_Writer):

    def __init__(self,sName,bAppend):
        self._path = None
        self._out = None
        super().__init__()
        self._path = sName
        if (not bAppend):
            self.open(False)

    def open(self,bAppend):
        self._out = open(self._path, ("a" if bAppend else "w"))

    def close(self):
        self._out.close()
        self._out = None

    def writeI(self,_hx_str):
        try:
            self._out.write(_hx_str)
        except BaseException as _g:
            None

    def write(self,_hx_str):
        if (self._out is None):
            self.open(True)
            self.writeI(_hx_str)
            self.close()
        else:
            self.writeI(_hx_str)

    def dispose(self):
        if (self._path is not None):
            self._path = None
            if (self._out is not None):
                self.close()
                self._out = None

    def convertToStringWriter(self):
        sw = com_sdtk_std_StringWriter(None)
        sw.endWith(self)
        return sw


class com_sdtk_std_Filter:

    def __init__(self):
        pass

    def filter(self,sValue):
        return sValue

    def _hx_and(self,fFilter):
        cfAnd = com_sdtk_std_FilterCompositeAnd()
        cfAnd._hx_and(self)
        cfAnd._hx_and(fFilter)
        return cfAnd

    def _hx_or(self,fFilter):
        cfAnd = com_sdtk_std_FilterCompositeOr()
        cfAnd._hx_or(self)
        cfAnd._hx_or(fFilter)
        return cfAnd

    @staticmethod
    def parse(sValue,bBlock):
        if (sValue is None):
            return None
        elif bBlock:
            _g = ("" if ((0 >= len(sValue))) else sValue[0])
            if (_g == "#"):
                sValue = HxString.substring(sValue,1,None)
                startIndex = None
                if (((sValue.find("-") if ((startIndex is None)) else HxString.indexOfImpl(sValue,"-",startIndex))) > 0):
                    iRange = com_sdtk_std_Filter.parseRange(sValue)
                    return com_sdtk_std_FilterBlockCountingRange((iRange[0] if 0 < len(iRange) else None),(iRange[1] if 1 < len(iRange) else None))
                else:
                    startIndex = None
                    if (((sValue.find(",") if ((startIndex is None)) else HxString.indexOfImpl(sValue,",",startIndex))) > 0):
                        return com_sdtk_std_FilterBlockCountingList(com_sdtk_std_Filter.parseList(sValue))
                    else:
                        return com_sdtk_std_FilterBlockCountingSingle(Std.parseInt(StringTools.trim(sValue)))
            elif (_g == "/"):
                return com_sdtk_std_FilterBlockRegularExpression(sValue)
            elif (_g == "="):
                return com_sdtk_std_FilterBlockEqualString(HxString.substring(sValue,1,None))
            else:
                return com_sdtk_std_FilterBlockWithString(sValue)
        else:
            _g = ("" if ((0 >= len(sValue))) else sValue[0])
            if (_g == "#"):
                sValue = HxString.substring(sValue,1,None)
                startIndex = None
                if (((sValue.find("-") if ((startIndex is None)) else HxString.indexOfImpl(sValue,"-",startIndex))) > 0):
                    iRange = com_sdtk_std_Filter.parseRange(sValue)
                    return com_sdtk_std_FilterAllowCountingRange((iRange[0] if 0 < len(iRange) else None),(iRange[1] if 1 < len(iRange) else None))
                else:
                    startIndex = None
                    if (((sValue.find(",") if ((startIndex is None)) else HxString.indexOfImpl(sValue,",",startIndex))) > 0):
                        return com_sdtk_std_FilterAllowCountingList(com_sdtk_std_Filter.parseList(sValue))
                    else:
                        return com_sdtk_std_FilterAllowCountingSingle(Std.parseInt(StringTools.trim(sValue)))
            elif (_g == "/"):
                return com_sdtk_std_FilterAllowRegularExpression(sValue)
            elif (_g == "="):
                return com_sdtk_std_FilterAllowEqualString(HxString.substring(sValue,1,None))
            else:
                return com_sdtk_std_FilterAllowWithString(sValue)

    @staticmethod
    def parseList(sList):
        iList = list()
        _g = 0
        _g1 = sList.split(",")
        while (_g < len(_g1)):
            s = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            x = Std.parseInt(StringTools.trim(s))
            iList.append(x)
        return iList

    @staticmethod
    def parseRange(sRange):
        iRange = list()
        _g = 0
        _g1 = sRange.split("-")
        while (_g < len(_g1)):
            s = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            x = Std.parseInt(StringTools.trim(s))
            iRange.append(x)
        return iRange


class com_sdtk_std_FilterCounting(com_sdtk_std_Filter):

    def __init__(self):
        self._count = 0
        super().__init__()

    def filter(self,sValue):
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._count
        _hx_local_0._count = (_hx_local_1 + 1)
        _hx_local_1
        return None

    def getCount(self):
        return self._count


class com_sdtk_std_FilterAllowCountingList(com_sdtk_std_FilterCounting):

    def __init__(self,iSearchFor):
        self._searchFor = None
        super().__init__()
        self._searchFor = iSearchFor

    def filter(self,sValue):
        super().filter(sValue)
        if ((self._searchFor is not None) and ((len(self._searchFor) > 0))):
            if (python_internal_ArrayImpl.indexOf(self._searchFor,self.getCount(),None) >= 0):
                return sValue
            else:
                return None
        else:
            return None


class com_sdtk_std_FilterAllowCountingRange(com_sdtk_std_FilterCounting):

    def __init__(self,iSearchForStart,iSearchForEnd):
        self._searchForEnd = None
        self._searchForStart = None
        super().__init__()
        self._searchForStart = iSearchForStart
        self._searchForEnd = iSearchForEnd

    def filter(self,sValue):
        super().filter(sValue)
        if ((self._searchForStart > 0) and ((self._searchForEnd > 0))):
            if ((self.getCount() >= self._searchForStart) and ((self.getCount() <= self._searchForEnd))):
                return sValue
            else:
                return None
        else:
            return None


class com_sdtk_std_FilterAllowCountingSingle(com_sdtk_std_FilterCounting):

    def __init__(self,iSearchFor):
        self._searchFor = None
        super().__init__()
        self._searchFor = iSearchFor

    def filter(self,sValue):
        super().filter(sValue)
        if (self._searchFor > 0):
            if (self.getCount() == self._searchFor):
                return sValue
            else:
                return None
        else:
            return None


class com_sdtk_std_FilterAllowEqualString(com_sdtk_std_Filter):

    def __init__(self,sSearchFor):
        self._searchFor = None
        super().__init__()
        self._searchFor = sSearchFor

    def filter(self,sValue):
        if (sValue is not None):
            if (sValue == self._searchFor):
                return sValue
            else:
                return None
        else:
            return None


class com_sdtk_std_FilterAllowRegularExpression(com_sdtk_std_Filter):

    def __init__(self,sSearchFor):
        self._searchFor = None
        super().__init__()
        sSearchFor = HxString.substr(sSearchFor,1,None)
        startIndex = None
        i = None
        if (startIndex is None):
            i = sSearchFor.rfind("/", 0, len(sSearchFor))
        else:
            i1 = sSearchFor.rfind("/", 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len("/"))) if ((i1 == -1)) else (i1 + 1))
            check = sSearchFor.find("/", startLeft, len(sSearchFor))
            i = (check if (((check > i1) and ((check <= startIndex)))) else i1)
        self._searchFor = EReg(HxString.substring(sSearchFor,0,i),HxString.substring(sSearchFor,(i + 1),None))

    def filter(self,sValue):
        if (sValue is not None):
            _this = self._searchFor
            _this.matchObj = python_lib_Re.search(_this.pattern,sValue)
            if (_this.matchObj is not None):
                return sValue
            else:
                return None
        else:
            return None


class com_sdtk_std_FilterAllowWithString(com_sdtk_std_Filter):

    def __init__(self,sSearchFor):
        self._searchFor = None
        super().__init__()
        self._searchFor = sSearchFor

    def filter(self,sValue):
        if (sValue is not None):
            _hx_str = self._searchFor
            startIndex = None
            if (((sValue.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sValue,_hx_str,startIndex))) >= 0):
                return sValue
            else:
                return None
        else:
            return None


class com_sdtk_std_FilterBlockCountingList(com_sdtk_std_FilterCounting):

    def __init__(self,iSearchFor):
        self._searchFor = None
        super().__init__()
        self._searchFor = iSearchFor

    def filter(self,sValue):
        super().filter(sValue)
        if ((self._searchFor is not None) and ((len(self._searchFor) > 0))):
            if (python_internal_ArrayImpl.indexOf(self._searchFor,self.getCount(),None) >= 0):
                return None
            else:
                return sValue
        else:
            return None


class com_sdtk_std_FilterBlockCountingRange(com_sdtk_std_FilterCounting):

    def __init__(self,iSearchForStart,iSearchForEnd):
        self._searchForEnd = None
        self._searchForStart = None
        super().__init__()
        self._searchForStart = iSearchForStart
        self._searchForEnd = iSearchForEnd

    def filter(self,sValue):
        super().filter(sValue)
        if ((self._searchForStart > 0) and ((self._searchForEnd > 0))):
            if ((self.getCount() >= self._searchForStart) and ((self.getCount() <= self._searchForEnd))):
                return None
            else:
                return sValue
        else:
            return None


class com_sdtk_std_FilterBlockCountingSingle(com_sdtk_std_FilterCounting):

    def __init__(self,iSearchFor):
        self._searchFor = None
        super().__init__()
        self._searchFor = iSearchFor

    def filter(self,sValue):
        super().filter(sValue)
        if (self._searchFor > 0):
            if (self.getCount() == self._searchFor):
                return None
            else:
                return sValue
        else:
            return None


class com_sdtk_std_FilterBlockEqualString(com_sdtk_std_Filter):

    def __init__(self,sSearchFor):
        self._searchFor = None
        super().__init__()
        self._searchFor = sSearchFor

    def filter(self,sValue):
        if (sValue is not None):
            if (sValue == self._searchFor):
                return None
            else:
                return sValue
        else:
            return None


class com_sdtk_std_FilterBlockRegularExpression(com_sdtk_std_Filter):

    def __init__(self,sSearchFor):
        self._searchFor = None
        super().__init__()
        sSearchFor = HxString.substr(sSearchFor,1,None)
        startIndex = None
        i = None
        if (startIndex is None):
            i = sSearchFor.rfind("/", 0, len(sSearchFor))
        else:
            i1 = sSearchFor.rfind("/", 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len("/"))) if ((i1 == -1)) else (i1 + 1))
            check = sSearchFor.find("/", startLeft, len(sSearchFor))
            i = (check if (((check > i1) and ((check <= startIndex)))) else i1)
        self._searchFor = EReg(HxString.substring(sSearchFor,0,i),HxString.substring(sSearchFor,(i + 1),None))

    def filter(self,sValue):
        if (sValue is not None):
            _this = self._searchFor
            _this.matchObj = python_lib_Re.search(_this.pattern,sValue)
            if (_this.matchObj is not None):
                return None
            else:
                return sValue
        else:
            return None


class com_sdtk_std_FilterBlockWithString(com_sdtk_std_Filter):

    def __init__(self,sSearchFor):
        self._searchFor = None
        super().__init__()
        self._searchFor = sSearchFor

    def filter(self,sValue):
        if (sValue is not None):
            _hx_str = self._searchFor
            startIndex = None
            if (((sValue.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sValue,_hx_str,startIndex))) >= 0):
                return None
            else:
                return sValue
        else:
            return None


class com_sdtk_std_FilterCompositeAnd(com_sdtk_std_Filter):

    def __init__(self):
        self._list = list()
        super().__init__()

    def filter(self,sValue):
        if (sValue is None):
            return None
        _g = 0
        _g1 = self._list
        while (_g < len(_g1)):
            fFilter = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            sValue = fFilter.filter(sValue)
            if (sValue is None):
                return None
        return sValue

    def _hx_and(self,fFilter):
        _this = self._list
        _this.append(fFilter)
        return self


class com_sdtk_std_FilterCompositeOr(com_sdtk_std_Filter):

    def __init__(self):
        self._list = list()
        super().__init__()

    def filter(self,sValue):
        if (sValue is None):
            return None
        _g = 0
        _g1 = self._list
        while (_g < len(_g1)):
            fFilter = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            if (fFilter.filter(sValue) is not None):
                return sValue
        return None

    def _hx_or(self,fFilter):
        _this = self._list
        _this.append(fFilter)
        return self


class com_sdtk_std_FilterReader(com_sdtk_std_Reader):

    def __init__(self,rReader):
        self._currentRawIndex = None
        self._current = None
        self._filter = None
        self._reader = None
        super().__init__()
        self._reader = rReader

    def rawIndex(self):
        return self._currentRawIndex

    def jumpTo(self,index):
        self._reader.jumpTo(index)
        self._current = None
        self.check()

    def addFilter(self,fFilter):
        if (self._filter is None):
            self._filter = list()
        _this = self._filter
        _this.append(fFilter)

    def check(self):
        if (self._current is None):
            if (self._filter is None):
                self._current = self._reader.next()
            else:
                while (self._current is None):
                    iNext = self._reader.rawIndex()
                    sNext = self._reader.next()
                    if (sNext is None):
                        break
                    _g = 0
                    _g1 = self._filter
                    while (_g < len(_g1)):
                        fFilter = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                        _g = (_g + 1)
                        sNext = fFilter.filter(sNext)
                    if (sNext is not None):
                        self._current = sNext
                        self._currentRawIndex = iNext

    def hasNext(self):
        self.check()
        return (self._current is not None)

    def next(self):
        self.check()
        sCurrent = self._current
        self._current = None
        return sCurrent

    def peek(self):
        self.check()
        return self._current

    def dispose(self):
        if (self._reader is not None):
            self._reader.dispose()
            self._reader = None
            self._current = None
            self._filter = None

    def switchToLineReader(self):
        self._reader = self._reader.switchToLineReader()
        return self

    def unwrapOne(self):
        return self._reader

    def unwrapAll(self):
        return self._reader.unwrapAll()

    def reset(self):
        self._reader.reset()
        self._current = None


class com_sdtk_std_FilterWriter(com_sdtk_std_Writer):

    def __init__(self,wWriter):
        self._filter = None
        self._writer = None
        super().__init__()
        self._writer = wWriter

    def addFilter(self,fFilter):
        if (self._filter is None):
            self._filter = list()
        _this = self._filter
        _this.append(fFilter)

    def write(self,_hx_str):
        if (self._filter is None):
            self._writer.write(_hx_str)
        else:
            sWrite = _hx_str
            _g = 0
            _g1 = self._filter
            while (_g < len(_g1)):
                fFilter = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                sWrite = fFilter.filter(sWrite)
            if (sWrite is not None):
                self._writer.write(sWrite)

    def switchToLineWriter(self):
        self._writer = self._writer.switchToLineWriter()
        return self

    def unwrapOne(self):
        return self._writer

    def unwrapAll(self):
        return self._writer.unwrapAll()

    def flush(self):
        self._writer.flush()

    def dispose(self):
        if (self._writer is not None):
            self._writer.dispose()
            self._writer = None
            self._filter = None


class com_sdtk_std_AbstractReader(com_sdtk_std_Reader):
    _hx_class_name = "com.sdtk.std.AbstractReader"
    __slots__ = ("_next", "_reader", "_mode", "_nextRawIndex", "_rawIndex")
    _hx_fields = ["_next", "_reader", "_mode", "_nextRawIndex", "_rawIndex"]
    _hx_methods = ["reset", "rawIndex", "jumpTo", "start", "moveToNext", "next", "peek", "dispose", "unwrapOne", "unwrapAll", "switchToLineReader", "hasNext"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = com_sdtk_std_Reader


    def __init__(self,iReader):
        self._rawIndex = None
        self._nextRawIndex = None
        self._reader = None
        self._mode = 0
        self._next = None
        super().__init__()
        self._reader = iReader
        self._next = ""

    def reset(self):
        self._nextRawIndex = 0

    def rawIndex(self):
        return self._rawIndex

    def jumpTo(self,index):
        if (index < self._nextRawIndex):
            self.reset()
        self._reader.readString((index - self._nextRawIndex))
        self._nextRawIndex = index

    def start(self):
        self.moveToNext()

    def moveToNext(self):
        try:
            _g = self._mode
            if (_g == 0):
                self._next = self._reader.readString(1)
            elif (_g == 1):
                self._next = self._reader.readLine()
            else:
                pass
        except BaseException as _g:
            None
            self.dispose()

    def next(self):
        sValue = self._next
        if (sValue is not None):
            self.moveToNext()
        return sValue

    def peek(self):
        return self._next

    def dispose(self):
        if (self._reader is not None):
            self._reader.close()
            self._reader = None
            self._next = None

    def unwrapOne(self):
        self._mode = 0
        return self

    def unwrapAll(self):
        self._mode = 0
        return self

    def switchToLineReader(self):
        self._mode = 1
        return self

    def hasNext(self):
        return (self._next is not None)

com_sdtk_std_AbstractReader._hx_class = com_sdtk_std_AbstractReader


class com_sdtk_std_AbstractWriter(com_sdtk_std_Writer):
    _hx_class_name = "com.sdtk.std.AbstractWriter"
    __slots__ = ("_writer",)
    _hx_fields = ["_writer"]
    _hx_methods = ["dispose", "flush", "write"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = com_sdtk_std_Writer


    def __init__(self,oWriter):
        self._writer = None
        super().__init__()
        self._writer = oWriter

    def dispose(self):
        if (self._writer is not None):
            self._writer.close()
            self._writer = None

    def flush(self):
        self._writer.flush()

    def write(self,_hx_str):
        self._writer.writeString(_hx_str)

com_sdtk_std_AbstractWriter._hx_class = com_sdtk_std_AbstractWriter


class com_sdtk_std_ParametersReader(com_sdtk_std_Reader):

    def __init__(self,pParameters):
        self._parameters = None
        self._index = 0
        self._next = None
        super().__init__()
        if (pParameters is None):
            pParameters = com_sdtk_std_Parameters()
        self._parameters = pParameters
        self._next = ""
        self.moveToNext()

    def reset(self):
        self._index = 0
        self._next = ""

    def rawIndex(self):
        return self._index

    def jumpTo(self,index):
        self._index = index

    def moveToNext(self):
        try:
            self._next = None
            self._next = self._parameters.getParameter(self._index)
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0._index
            _hx_local_0._index = (_hx_local_1 + 1)
            _hx_local_1
        except BaseException as _g:
            None
        if (self._next is None):
            self.dispose()

    def hasNext(self):
        return (self._next is not None)

    def next(self):
        sValue = self._next
        if (sValue is not None):
            self.moveToNext()
        return sValue

    def peek(self):
        return self._next

    def dispose(self):
        if (self._parameters is not None):
            self._parameters = None
            self._next = None
            self._index = -1

    def iterator(self):
        return self


class com_sdtk_std_PopUpWriter(com_sdtk_std_Writer):

    def __init__(self):
        super().__init__()

    def write(self,sLine):
        try:
            pass
        except BaseException as _g:
            None
            return


class com_sdtk_std_ReaderAsync:
    pass


class com_sdtk_std_ReaderAsyncAbstract:

    def __init__(self):
        self._handlers = list()

    def readTo(self,rhHandler):
        _this = self._handlers
        _this.append(rhHandler)
        return self

    def read(self,sValue):
        _g = 0
        _g1 = self._handlers
        while (_g < len(_g1)):
            rhHandler = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            rhHandler.read(sValue)

    def start(self):
        return self

    def dispose(self):
        self._handlers = None


class com_sdtk_std_ReaderHandler:
    pass


class com_sdtk_std_StdinReader(com_sdtk_std_FileReader):

    def __init__(self):
        super().__init__(None)

    def open(self):
        self._in = sys.stdin

    def close(self):
        pass


class com_sdtk_std_StdoutWriter(com_sdtk_std_FileWriter):

    def __init__(self):
        super().__init__(None,False)

    def open(self,bAppend):
        self._out = sys.stdout

    def close(self):
        self._out = self._out.flush()


class com_sdtk_std_StringReaderMethod:
    pass


class com_sdtk_std_StringReaderEachChar:

    def __init__(self):
        pass

    def moveToNext(self,index,value):
        return HxString.substr(value,index,1)


class com_sdtk_std_StringReaderEachLine:

    def __init__(self):
        pass

    def moveToNext(self,index,value):
        j = (value.find("\n") if ((index is None)) else HxString.indexOfImpl(value,"\n",index))
        if (j < 0):
            j = len(value)
        return HxString.substr(value,index,(j - index))


class com_sdtk_std_StringWriter(com_sdtk_std_Writer):

    def __init__(self,reuse):
        self._dropping = -1
        self._end = None
        self._writer = None
        self._buffer = None
        super().__init__()
        if (reuse is None):
            self._buffer = StringBuf()
        else:
            self._buffer = reuse

    def endWith(self,writer):
        self._writer = writer

    def dispose(self):
        if (self._buffer is not None):
            self._end = self._buffer.b.getvalue()
        if (self._writer is not None):
            self._writer.write(self._end)
            self._writer.dispose()
            self._writer = None
        self._buffer = None

    def toString(self):
        if (self._buffer is not None):
            return self._buffer.b.getvalue()
        else:
            return self._end

    def write(self,_hx_str):
        _this = self._buffer
        s = Std.string(_hx_str)
        _this.b.write(s)
        if ((self._dropping > 0) and ((self._buffer.get_length() > self._dropping))):
            self._writer.write(self._buffer.b.getvalue())
            self._buffer = StringBuf()

    def switchToDroppingCharacters(self,chars = None):
        if (chars is None):
            chars = 10000
        self._dropping = chars
        return self


class com_sdtk_std_UsesCompletionHandler:
    pass


class com_sdtk_std_WriterAsync:
    pass


class com_sdtk_std_StringWriterAsync:

    def __init__(self):
        self._buffer = StringBuf()

    def done(self,iBytes,oAttachment):
        pass

    def write(self,sData,whHandler):
        _this = self._buffer
        s = Std.string(sData)
        _this.b.write(s)
        whHandler.done()
        return self

    def toString(self):
        return self._buffer.b.getvalue()

    def dispose(self):
        self._buffer = None


class com_sdtk_std_SysLogWriter(com_sdtk_std_Writer):

    def __init__(self):
        super().__init__()

    def write(self,sLine):
        try:
            sLineUpper = sLine.upper()
            iLevel = 0
            startIndex = None
            if (((sLineUpper.find("WARN") if ((startIndex is None)) else HxString.indexOfImpl(sLineUpper,"WARN",startIndex))) >= 0):
                iLevel = 1
            startIndex = None
            if (((sLineUpper.find("ERR") if ((startIndex is None)) else HxString.indexOfImpl(sLineUpper,"ERR",startIndex))) >= 0):
                iLevel = 2
        except BaseException as _g:
            None
            return

    def dispose(self):
        super().dispose()


class com_sdtk_std_Version:

    @staticmethod
    def get():
        return com_sdtk_std_Version._code


class com_sdtk_std_WholeLineReader(com_sdtk_std_Reader):

    def __init__(self,rReader):
        self._reader = None
        self._currentRawIndex = None
        self._current = None
        self._list = None
        self._buffer = StringBuf()
        self._empty = True
        super().__init__()
        self._reader = rReader

    def reset(self):
        self._reader.reset()

    def rawIndex(self):
        return self._currentRawIndex

    def jumpTo(self,index):
        self._current = None
        self._reader.jumpTo(index)
        self.check()

    def check(self):
        if (self._current is None):
            if ((self._list is not None) and ((len(self._list) > 0))):
                _this = self._list
                self._current = (None if ((len(_this) == 0)) else _this.pop(0))
            elif (self._empty and ((self._reader.hasNext() == False))):
                return
            else:
                try:
                    self._currentRawIndex = self._reader.rawIndex()
                    while True:
                        s = self._reader.next()
                        if ((s is None) and (not self._empty)):
                            s = "\n"
                        if (s is not None):
                            _this = self._buffer
                            s1 = Std.string(s)
                            _this.b.write(s1)
                            self._empty = False
                        tmp = None
                        if (s is not None):
                            startIndex = None
                            tmp = (((s.find("\n") if ((startIndex is None)) else HxString.indexOfImpl(s,"\n",startIndex))) >= 0)
                        else:
                            tmp = True
                        if tmp:
                            sLines = s.split("\n")
                            _this1 = self._buffer
                            s2 = Std.string((sLines[0] if 0 < len(sLines) else None))
                            _this1.b.write(s2)
                            self._current = self._buffer.b.getvalue()
                            self._buffer = StringBuf()
                            if ((len(sLines) <= 1) or ((len(python_internal_ArrayImpl._get(sLines, (len(sLines) - 1))) == 0))):
                                self._empty = True
                            else:
                                _this2 = self._buffer
                                s3 = Std.string(python_internal_ArrayImpl._get(sLines, (len(sLines) - 1)))
                                _this2.b.write(s3)
                                inlarr_0 = (len(sLines) - 1)
                                self._empty = False
                            i = 1
                            while (i < ((len(sLines) - 1))):
                                _this3 = self._list
                                x = i
                                i = (i + 1)
                                x1 = (sLines[x] if x >= 0 and x < len(sLines) else None)
                                _this3.append(x1)
                            break
                except BaseException as _g:
                    None
                    self._current = None

    def hasNext(self):
        self.check()
        return (self._current is not None)

    def next(self):
        self.check()
        sCurrent = self._current
        self._current = None
        return sCurrent

    def peek(self):
        self.check()
        return self._current

    def dispose(self):
        if (self._reader is not None):
            self._reader.dispose()
            self._reader = None
            self._buffer = None
            self._current = None
            self._list = None

    def switchToLineReader(self):
        return self

    def unwrapOne(self):
        return self._reader

    def unwrapAll(self):
        return self._reader.unwrapAll()


class com_sdtk_std_WholeLineWriter(com_sdtk_std_Writer):

    def __init__(self,wWriter):
        self._writer = None
        self._buffer = StringBuf()
        self._empty = True
        super().__init__()
        self._writer = wWriter

    def write(self,_hx_str):
        startIndex = None
        tmp = None
        if (startIndex is None):
            tmp = _hx_str.rfind("\n", 0, len(_hx_str))
        else:
            i = _hx_str.rfind("\n", 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len("\n"))) if ((i == -1)) else (i + 1))
            check = _hx_str.find("\n", startLeft, len(_hx_str))
            tmp = (check if (((check > i) and ((check <= startIndex)))) else i)
        if (tmp < 0):
            _this = self._buffer
            s = Std.string(_hx_str)
            _this.b.write(s)
            self._empty = False
        else:
            sLines = _hx_str.split("\n")
            iLine = 1
            _g = 0
            while (_g < len(sLines)):
                sLine = (sLines[_g] if _g >= 0 and _g < len(sLines) else None)
                _g = (_g + 1)
                if (iLine == len(sLines)):
                    if (len(sLine) > 0):
                        _this = self._buffer
                        s = Std.string(sLine)
                        _this.b.write(s)
                elif self._empty:
                    self._writer.write(_hx_str)
                else:
                    _this1 = self._buffer
                    s1 = Std.string(sLine)
                    _this1.b.write(s1)
                    self._writer.write(self._buffer.b.getvalue())
                    self._buffer = StringBuf()
                    self._empty = True
                iLine = (iLine + 1)

    def switchToLineWriter(self):
        return self

    def unwrapOne(self):
        return self._writer

    def unwrapAll(self):
        return self._writer.unwrapAll()

    def flush(self):
        self._writer.flush()

    def dispose(self):
        if (self._writer is not None):
            self._writer.dispose()
            self._writer = None
            self._buffer = None


class com_sdtk_std_WriterHandler:
    pass


class com_sdtk_table_AbstractTableReader:

    def __init__(self,tdInfo,oElement):
        self._next = None
        self._info = tdInfo
        self._element = oElement
        self._accessor = None
        self.findNext()

    def elementCheck(self,oElement):
        return False

    def getValue(self,oElement):
        return None

    def findNext(self):
        pass

    def hasNext(self):
        return (self._next is not None)

    def peek(self):
        if (self._next is None):
            return None
        else:
            return self.getValue(self._next)

    def next(self):
        self._accessor = self._next
        self.findNext()
        if (self._accessor is None):
            return None
        else:
            return self.getValue(self._accessor)


class com_sdtk_table_DataTableRowWriter:

    def __init__(self):
        pass

    def write(self,data,name,index):
        pass

    def start(self):
        pass

    def dispose(self):
        pass


class com_sdtk_table_AbstractTableRowWriter(com_sdtk_table_DataTableRowWriter):

    def __init__(self,tdInfo,writer,sHeader):
        self._writer = None
        self._info = None
        self._header = None
        super().__init__()
        self.reuse(tdInfo,writer,sHeader)

    def reuse(self,tdInfo,writer,sHeader):
        self._info = tdInfo
        self._writer = writer
        self._header = sHeader

    def dispose(self):
        self._header = None
        self._info = None
        self._writer = None


class com_sdtk_table_ArrayInfo:

    def __init__(self,arr,start,end,entriesInRow,increment,rowIncrement):
        self._arr = arr
        self._start = start
        self._end = end
        self._entriesInRow = entriesInRow
        self._increment = increment
        self._rowIncrement = rowIncrement


class com_sdtk_table_Array2DInfo(com_sdtk_table_ArrayInfo):

    def __init__(self,arr,start,end,entriesInRow,increment,rowIncrement):
        super().__init__(arr,start,end,entriesInRow,increment,rowIncrement)


class com_sdtk_table_DataEntryReader:

    def __init__(self):
        self._nameIsIndex = None
        self._autoNamed = None
        self._value = None
        self._name = None
        self._started = False
        self._rawIndex = -1
        self._index = -1

    def incrementTo(self,name,value,rawIndex):
        self._rawIndex = rawIndex
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._index
        _hx_local_0._index = (_hx_local_1 + 1)
        _hx_local_1
        indexAsString = Std.string(self._index)
        self._value = value
        if (name is None):
            self._name = indexAsString
            self._autoNamed = True
            self._nameIsIndex = True
        else:
            self._name = name
            self._autoNamed = False
            self._nameIsIndex = (indexAsString == name)

    def hasNext(self):
        return False

    def next(self):
        return None

    def iterator(self):
        return self

    def name(self):
        return self._name

    def index(self):
        return self._index

    def rawIndex(self):
        return self._rawIndex

    def value(self):
        return self._value

    def isAutoNamed(self):
        return self._autoNamed

    def isNameIndex(self):
        return self._nameIsIndex

    def start(self):
        if (not self._started):
            self._started = True
            self.startI()

    def startI(self):
        pass

    def dispose(self):
        pass


class com_sdtk_table_DataTableReader(com_sdtk_table_DataEntryReader):

    def __init__(self):
        self._iteratorData = None
        self._alwaysString = False
        self.HEADER_ROW_INDEX = -1
        self.HEADER_ROW_NAME = None
        self.ROW_NAME_INDEX = -1
        self.ROW_NAME = "__name__"
        super().__init__()

    def writeRowNameHeader(self,writers,rowWriters,sName):
        bWritingRowNames = False
        if ((sName is not None) and ((len(sName) > 0))):
            i = 0
            writer = HxOverrides.iterator(writers)
            while writer.hasNext():
                writer1 = writer.next()
                if writer1.writeRowNameFirst():
                    (rowWriters[i] if i >= 0 and i < len(rowWriters) else None).write(self.ROW_NAME,self.ROW_NAME,self.ROW_NAME_INDEX)
                    bWritingRowNames = True
                i = (i + 1)
        return bWritingRowNames

    def writeRowName(self,writers,rowWriters,sName,bWritingRowNames):
        if bWritingRowNames:
            bWritingRowNames = False
            if ((sName is not None) and ((len(sName) > 0))):
                i = 0
                writer = HxOverrides.iterator(writers)
                while writer.hasNext():
                    writer1 = writer.next()
                    if writer1.writeRowNameFirst():
                        (rowWriters[i] if i >= 0 and i < len(rowWriters) else None).write(sName,self.ROW_NAME,self.ROW_NAME_INDEX)
                        bWritingRowNames = True
                    i = (i + 1)
        return bWritingRowNames

    def nextReuse(self,reader):
        return None

    def writeFirstRow(self,writers,rowWriters):
        bBufferFirstRow = False
        rowReader = self.next()
        rowReader.alwaysString(self._alwaysString)
        bWritingRowNames = ((not self.isAutoNamed()) and (not self.isNameIndex()))
        sName = self.name()
        iIndex = self.index()
        if self.headerRowNotIncluded():
            writer = HxOverrides.iterator(writers)
            while writer.hasNext():
                writer1 = writer.next()
                bBufferFirstRow = (bBufferFirstRow or writer1.writeHeaderFirst())
        if (not bBufferFirstRow):
            if (not self.headerRowNotIncluded()):
                i = 0
                iNulls = 0
                writer = HxOverrides.iterator(writers)
                while writer.hasNext():
                    writer1 = writer.next()
                    if (not writer1.writeHeaderFirst()):
                        tmp = i
                        i = (i + 1)
                        python_internal_ArrayImpl._set(rowWriters, tmp, com_sdtk_table_NullRowWriter.instance)
                        iNulls = (iNulls + 1)
                    else:
                        tmp1 = i
                        i = (i + 1)
                        python_internal_ArrayImpl._set(rowWriters, tmp1, writer1.writeStart(sName,iIndex))
                if (iNulls == i):
                    rowReader.convertTo(com_sdtk_table_NullRowWriter.instance)
                else:
                    bWritingRowNames = self.writeRowName(writers,rowWriters,sName,bWritingRowNames)
                    rowReader.convertToAll(rowWriters)
                i = 0
                _g = 0
                while (_g < len(rowWriters)):
                    rowWriter = (rowWriters[_g] if _g >= 0 and _g < len(rowWriters) else None)
                    _g = (_g + 1)
                    if (rowWriter is not None):
                        if (rowWriter == com_sdtk_table_NullRowWriter.instance):
                            python_internal_ArrayImpl._set(rowWriters, i, None)
                        else:
                            rowWriter.dispose()
                    i = (i + 1)
            else:
                i = 0
                writer = HxOverrides.iterator(writers)
                while writer.hasNext():
                    writer1 = writer.next()
                    tmp = i
                    i = (i + 1)
                    python_internal_ArrayImpl._set(rowWriters, tmp, writer1.writeStart(sName,iIndex))
                bWritingRowNames = self.writeRowName(writers,rowWriters,sName,bWritingRowNames)
                rowReader.convertToAll(rowWriters)
                _g = 0
                while (_g < len(rowWriters)):
                    rowWriter = (rowWriters[_g] if _g >= 0 and _g < len(rowWriters) else None)
                    _g = (_g + 1)
                    if (rowWriter is not None):
                        rowWriter.dispose()
        else:
            i = 0
            aData = list()
            aName = list()
            aIndex = list()
            writer = HxOverrides.iterator(writers)
            while writer.hasNext():
                writer1 = writer.next()
                if writer1.writeHeaderFirst():
                    tmp = i
                    i = (i + 1)
                    python_internal_ArrayImpl._set(rowWriters, tmp, writer1.writeStart(self.HEADER_ROW_NAME,self.HEADER_ROW_INDEX))
                else:
                    tmp1 = i
                    i = (i + 1)
                    python_internal_ArrayImpl._set(rowWriters, tmp1, None)
            rowReader.start()
            _g = 0
            while (_g < len(rowWriters)):
                rowWriter = (rowWriters[_g] if _g >= 0 and _g < len(rowWriters) else None)
                _g = (_g + 1)
                if (rowWriter is not None):
                    rowWriter.start()
            if bWritingRowNames:
                bWritingRowNames = self.writeRowNameHeader(writers,rowWriters,sName)
            while rowReader.hasNext():
                try:
                    data = rowReader.next()
                    sName1 = rowReader.name()
                    iIndex1 = rowReader.index()
                    _g = 0
                    while (_g < len(rowWriters)):
                        rowWriter = (rowWriters[_g] if _g >= 0 and _g < len(rowWriters) else None)
                        _g = (_g + 1)
                        if (rowWriter is not None):
                            rowWriter.write(sName1,sName1,iIndex1)
                    aData.append(data)
                    aName.append(sName1)
                    aIndex.append(iIndex1)
                except BaseException as _g1:
                    None
                    break
            rowReader.dispose()
            _g = 0
            while (_g < len(rowWriters)):
                rowWriter = (rowWriters[_g] if _g >= 0 and _g < len(rowWriters) else None)
                _g = (_g + 1)
                if (rowWriter is not None):
                    rowWriter.dispose()
            i = 0
            writer = HxOverrides.iterator(writers)
            while writer.hasNext():
                writer1 = writer.next()
                tmp = i
                i = (i + 1)
                python_internal_ArrayImpl._set(rowWriters, tmp, writer1.writeStart(sName,iIndex))
            _g = 0
            while (_g < len(rowWriters)):
                rowWriter = (rowWriters[_g] if _g >= 0 and _g < len(rowWriters) else None)
                _g = (_g + 1)
                rowWriter.start()
            bWritingRowNames = self.writeRowName(writers,rowWriters,sName,bWritingRowNames)
            i = 0
            _g = 0
            while (_g < len(aData)):
                o = (aData[_g] if _g >= 0 and _g < len(aData) else None)
                _g = (_g + 1)
                _g1 = 0
                while (_g1 < len(rowWriters)):
                    rowWriter = (rowWriters[_g1] if _g1 >= 0 and _g1 < len(rowWriters) else None)
                    _g1 = (_g1 + 1)
                    rowWriter.write(o,(aName[i] if i >= 0 and i < len(aName) else None),(aIndex[i] if i >= 0 and i < len(aIndex) else None))
                i = (i + 1)
            _g = 0
            while (_g < len(rowWriters)):
                rowWriter = (rowWriters[_g] if _g >= 0 and _g < len(rowWriters) else None)
                _g = (_g + 1)
                rowWriter.dispose()
        return bWritingRowNames

    def convertTo(self,writer):
        aSingle = list()
        aSingle.append(writer)
        self.convertToAll(aSingle)

    def convertToAll(self,writers):
        bWritingRowNames = True
        bFirst = True
        bCanWrite = True
        self.start()
        writer = HxOverrides.iterator(writers)
        while writer.hasNext():
            writer1 = writer.next()
            writer1.start()
        try:
            rowReader = None
            rowWriters = []
            writer = HxOverrides.iterator(writers)
            while writer.hasNext():
                writer1 = writer.next()
                rowWriters.append(None)
            while (self.hasNext() and bCanWrite):
                if bFirst:
                    bWritingRowNames = self.writeFirstRow(writers,rowWriters)
                    bFirst = False
                else:
                    rowReader = self.nextReuse(rowReader)
                    if (rowReader is None):
                        break
                    rowReader.alwaysString(self._alwaysString)
                    rowReader.start()
                    try:
                        i = 0
                        sName = self.name()
                        iIndex = self.index()
                        writer = HxOverrides.iterator(writers)
                        while writer.hasNext():
                            writer1 = writer.next()
                            python_internal_ArrayImpl._set(rowWriters, i, writer1.writeStartReuse(sName,iIndex,(rowWriters[i] if i >= 0 and i < len(rowWriters) else None)))
                            i = (i + 1)
                        bWritingRowNames = self.writeRowName(writers,rowWriters,sName,bWritingRowNames)
                        rowReader.convertToAll(rowWriters)
                    except BaseException as _g:
                        None
                bCanWrite = False
                writer2 = HxOverrides.iterator(writers)
                while writer2.hasNext():
                    writer3 = writer2.next()
                    bCanWrite = (bCanWrite or writer3.canWrite())
            _g = 0
            while (_g < len(rowWriters)):
                rowWriter = (rowWriters[_g] if _g >= 0 and _g < len(rowWriters) else None)
                _g = (_g + 1)
                if (rowWriter is not None):
                    rowWriter.dispose()
            if (rowReader is not None):
                rowReader.dispose()
        except BaseException as _g:
            None
        self.dispose()
        writer = HxOverrides.iterator(writers)
        while writer.hasNext():
            writer1 = writer.next()
            writer1.dispose()

    def headerRowNotIncluded(self):
        return True

    def oneRowPerFile(self):
        return False

    def alwaysString(self,value = None):
        if (value is None):
            return self._alwaysString
        else:
            self._alwaysString = value
            return self._alwaysString

    def reset(self):
        pass

    def moveTo(self,row):
        if (row < self._index):
            self.reset()
        while (self._index < row):
            pass

    def noHeaderIncluded(self,noHeader):
        pass

    def allowNoHeaderInclude(self):
        return False

    def indexer(self):
        _gthis = self
        if (self._iteratorData is None):
            self._iteratorData = com_sdtk_table_DataTableReaderSharedIterator(self)
        def _hx_local_1():
            def _hx_local_0():
                return _gthis._iteratorData._row
            return com_sdtk_table_DataTableReaderIterable(self._iteratorData,_hx_local_0)
        return _hx_local_1()

    def readColumnIndex(self,i):
        _gthis = self
        if (self._iteratorData is None):
            self._iteratorData = com_sdtk_table_DataTableReaderSharedIterator(self)
        def _hx_local_1():
            def _hx_local_0():
                return python_internal_ArrayImpl._get(_gthis._iteratorData._dataByIndex, i)
            return com_sdtk_table_DataTableReaderIterable(self._iteratorData,_hx_local_0)
        return _hx_local_1()

    def readColumnName(self,s):
        _gthis = self
        if (self._iteratorData is None):
            self._iteratorData = com_sdtk_table_DataTableReaderSharedIterator(self)
        def _hx_local_1():
            def _hx_local_0():
                return _gthis._iteratorData._dataByName.h.get(s,None)
            return com_sdtk_table_DataTableReaderIterable(self._iteratorData,_hx_local_0)
        return _hx_local_1()


class com_sdtk_table_Array2DReader(com_sdtk_table_DataTableReader):

    def __init__(self,info):
        self._info = None
        self._i = None
        super().__init__()
        self._info = info
        self._i = info._start

    def hasNext(self):
        return (self._i <= (((len(self._info._arr) - 1) if ((self._info._end < 0)) else self._info._end)))

    def nextReuse(self,rowReader):
        if (rowReader is None):
            rowReader = com_sdtk_table_ArrayRowReader.readWholeArray(python_internal_ArrayImpl._get(self._info._arr, self._i))
        else:
            rr = rowReader
            rr.reuse(python_internal_ArrayImpl._get(self._info._arr, self._i))
        self.incrementTo(None,rowReader,self._i)
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._i
        _hx_local_0._i = (_hx_local_1 + self._info._rowIncrement)
        _hx_local_0._i
        return rowReader

    def next(self):
        return self.nextReuse(None)

    def iterator(self):
        return com_sdtk_table_Array2DReader(self._info)

    def flip(self):
        return com_sdtk_table_Array2DWriter.reuse(self._info)

    def headerRowNotIncluded(self):
        return False

    def reset(self):
        self._i = self._info._start

    @staticmethod
    def readWholeArray(arr):
        return com_sdtk_table_Array2DReader(com_sdtk_table_Array2DInfo(arr,0,(len(arr) - 1),(len(arr) - 1),1,1))

    @staticmethod
    def readWholeArrayI(arr):
        return com_sdtk_table_Array2DReader(com_sdtk_table_Array2DInfo(arr,0,(len(arr) - 1),(len(arr) - 1),1,1))

    @staticmethod
    def reuse(info):
        return com_sdtk_table_Array2DReader(info)


class com_sdtk_table_DataTableWriter:

    def __init__(self):
        self._written = 0

    def start(self):
        pass

    def writeStart(self,name,index):
        return self.writeStartReuse(name,index,None)

    def writeStartReuse(self,name,index,rowWriter):
        if (not self.canWrite()):
            return None
        else:
            dtrwWriter = self.writeStartI(name,index,rowWriter)
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0._written
            _hx_local_0._written = (_hx_local_1 + 1)
            _hx_local_1
            return dtrwWriter

    def writeStartI(self,name,index,rowWriter):
        return None

    def writeHeaderFirst(self):
        return False

    def writeRowNameFirst(self):
        return False

    def oneRowPerFile(self):
        return False

    def canWrite(self):
        if (self._written > 0):
            return (not self.oneRowPerFile())
        else:
            return True

    def dispose(self):
        pass


class com_sdtk_table_Array2DWriter(com_sdtk_table_DataTableWriter):

    def __init__(self,info):
        self._info = None
        self._i = None
        super().__init__()
        self._info = info
        self._i = info._start

    def start(self):
        pass

    def writeStartI(self,name,index,rowWriter):
        arr = self._info._arr
        if ((self._info._end >= 0) and (((index + self._info._start) > self._info._end))):
            return None
        while (len(arr) <= self._i):
            x = list()
            arr.append(x)
        rowWriter1 = com_sdtk_table_ArrayRowWriter.writeToExpandableArrayReuse(python_internal_ArrayImpl._get(arr, self._i),rowWriter)
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._i
        _hx_local_0._i = (_hx_local_1 + self._info._rowIncrement)
        _hx_local_0._i
        return rowWriter1

    def flip(self):
        return com_sdtk_table_Array2DReader.reuse(self._info)

    def getArray(self):
        return self._info._arr

    def dispose(self):
        if (self._info is not None):
            self._info = None

    def writeHeaderFirst(self):
        return False

    def writeRowNameFirst(self):
        return True

    @staticmethod
    def writeToWholeArray(arr):
        return com_sdtk_table_Array2DWriter(com_sdtk_table_Array2DInfo(arr,0,(len(arr) - 1),(len(arr) - 1),1,1))

    @staticmethod
    def writeToExpandableArrayI(arr):
        if (arr is None):
            arr = list()
        return com_sdtk_table_Array2DWriter(com_sdtk_table_Array2DInfo(arr,0,-1,-1,1,1))

    @staticmethod
    def writeToExpandableArray(arr):
        if (arr is None):
            arr = list()
        return com_sdtk_table_Array2DWriter(com_sdtk_table_Array2DInfo(arr,0,-1,-1,1,1))

    @staticmethod
    def reuse(info):
        return com_sdtk_table_Array2DWriter(info)


class com_sdtk_table_ArrayReader(com_sdtk_table_DataTableReader):

    def __init__(self,info):
        self._info = None
        self._i = None
        super().__init__()
        self._info = info
        self._i = info._start

    def hasNext(self):
        return (self._i <= self._info._end)

    def nextReuse(self,rowReader):
        if (rowReader is None):
            rowReader = com_sdtk_table_ArrayRowReader.continueRead(self._info,self._i,((self._i + self._info._entriesInRow) - 1))
        else:
            rr = rowReader
            rr.reuse(python_internal_ArrayImpl._get(self._info._arr, self._i))
        self._value = rowReader
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._i
        _hx_local_0._i = (_hx_local_1 + self._info._rowIncrement)
        _hx_local_0._i
        return rowReader

    def next(self):
        return self.nextReuse(None)

    def iterator(self):
        return com_sdtk_table_ArrayReader(self._info)

    def reset(self):
        self._i = self._info._start

    @staticmethod
    def readSlicesOfArray(arr,start,end,entriesInRow,increment,rowIncrement):
        return com_sdtk_table_ArrayReader(com_sdtk_table_ArrayInfo(arr,start,end,entriesInRow,increment,rowIncrement))

    @staticmethod
    def readPartOfArray(arr,start,end,increment):
        return com_sdtk_table_ArrayReader(com_sdtk_table_ArrayInfo(arr,start,end,(len(arr) - 1),increment,1))

    @staticmethod
    def readWholeArray(arr):
        return com_sdtk_table_ArrayReader(com_sdtk_table_ArrayInfo(arr,0,(len(arr) - 1),(len(arr) - 1),1,0))


class com_sdtk_table_Stopwatch:

    def __init__(self):
        pass

    def start(self):
        pass

    def end(self):
        pass

    def toString(self):
        return None

    def isNull(self):
        return True

    @staticmethod
    def getStopwatch(name):
        watch = com_sdtk_table_Stopwatch._watches.h.get(name,None)
        if (watch is None):
            if com_sdtk_table_Stopwatch._defaultActual:
                watch = com_sdtk_table_StopwatchWrapper(com_sdtk_table_StopwatchActual(name))
            else:
                if (com_sdtk_table_Stopwatch._null is None):
                    com_sdtk_table_Stopwatch._null = com_sdtk_table_StopwatchNull()
                watch = com_sdtk_table_StopwatchWrapper(com_sdtk_table_Stopwatch._null)
            com_sdtk_table_Stopwatch._watches.h[name] = watch
        return watch

    @staticmethod
    def setDefaultActual(defaultActual):
        com_sdtk_table_Stopwatch._defaultActual = defaultActual
        if defaultActual:
            k = com_sdtk_table_Stopwatch._watches.keys()
            while k.hasNext():
                k1 = k.next()
                com_sdtk_table_Stopwatch.setActual(k1)

    @staticmethod
    def setActual(name):
        watch = com_sdtk_table_Stopwatch._watches.h.get(name,None)
        if (watch is None):
            watch = com_sdtk_table_StopwatchWrapper(com_sdtk_table_StopwatchActual(name))
            com_sdtk_table_Stopwatch._watches.h[name] = watch
        elif watch.isNull():
            wrapper = watch
            wrapper.set(com_sdtk_table_StopwatchActual(name))

    @staticmethod
    def printResults():
        buffer = ""
        k = com_sdtk_table_Stopwatch._watches.keys()
        while k.hasNext():
            k1 = k.next()
            watch = com_sdtk_table_Stopwatch._watches.h.get(k1,None)
            if (watch is not None):
                _hx_str = watch.toString()
                if (_hx_str is not None):
                    buffer = (("null" if buffer is None else buffer) + HxOverrides.stringOrNull(((("null" if _hx_str is None else _hx_str) + "\n"))))
        _hx_str = Std.string(buffer)
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))


class com_sdtk_table_StopwatchActual(com_sdtk_table_Stopwatch):
    _hx_class_name = "com.sdtk.table.StopwatchActual"
    __slots__ = ("_start", "_end", "_duration", "_invocations", "_name")
    _hx_fields = ["_start", "_end", "_duration", "_invocations", "_name"]
    _hx_methods = ["start", "end", "toString", "isNull"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = com_sdtk_table_Stopwatch


    def __init__(self,name):
        self._name = None
        self._end = None
        self._start = None
        self._invocations = 0
        self._duration = 0
        super().__init__()
        self._name = name

    def start(self):
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._invocations
        _hx_local_0._invocations = (_hx_local_1 + 1)
        _hx_local_1
        self._start = Date.now()

    def end(self):
        self._end = Date.now()
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._duration
        _hx_local_0._duration = (_hx_local_1 + Math.floor(((self._end.date.timestamp() * 1000) - ((self._start.date.timestamp() * 1000)))))
        _hx_local_0._duration

    def toString(self):
        if (self._invocations == 1):
            return (((("Duration for " + HxOverrides.stringOrNull(self._name)) + " was ") + Std.string(self._duration)) + "ms")
        else:
            return (((((("Total duration for " + HxOverrides.stringOrNull(self._name)) + " was ") + Std.string(self._duration)) + "ms and it was invoked ") + Std.string(self._invocations)) + " times.")

    def isNull(self):
        return False

com_sdtk_table_StopwatchActual._hx_class = com_sdtk_table_StopwatchActual


class com_sdtk_table_StopwatchWrapper(com_sdtk_table_Stopwatch):
    _hx_class_name = "com.sdtk.table.StopwatchWrapper"
    __slots__ = ("_watch",)
    _hx_fields = ["_watch"]
    _hx_methods = ["start", "end", "toString", "set", "isNull"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = com_sdtk_table_Stopwatch


    def __init__(self,watch):
        self._watch = None
        super().__init__()
        self._watch = watch

    def start(self):
        self._watch.start()

    def end(self):
        self._watch.end()

    def toString(self):
        return self._watch.toString()

    def set(self,watch):
        self._watch = watch

    def isNull(self):
        return self._watch.isNull()

com_sdtk_table_StopwatchWrapper._hx_class = com_sdtk_table_StopwatchWrapper


class com_sdtk_table_StopwatchNull(com_sdtk_table_Stopwatch):
    _hx_class_name = "com.sdtk.table.StopwatchNull"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = com_sdtk_table_Stopwatch


    def __init__(self):
        super().__init__()
com_sdtk_table_StopwatchNull._hx_class = com_sdtk_table_StopwatchNull


class com_sdtk_table_DataTableRowReader(com_sdtk_table_DataEntryReader):

    def __init__(self):
        self._alwaysString = False
        super().__init__()

    def convertTo(self,rowWriter):
        aSingle = list()
        aSingle.append(rowWriter)
        self.convertToAll(aSingle)

    def fromStringToType(self,_hx_str):
        com_sdtk_table_DataTableRowReader._watch.start()
        result = None
        if self._alwaysString:
            result = _hx_str
        else:
            isInt = True
            isHex = True
            isFloat = True
            foundPoint = False
            foundX = False
            i = 0
            _g = _hx_str.lower()
            _hx_local_0 = len(_g)
            if (_hx_local_0 == 5):
                if (_g == "false"):
                    result = False
                else:
                    while (i < len(_hx_str)):
                        _g = ("" if (((i < 0) or ((i >= len(_hx_str))))) else _hx_str[i])
                        if ((_g == ".") or ((_g == ","))):
                            if foundPoint:
                                isFloat = False
                                break
                            else:
                                foundPoint = True
                            isHex = False
                            isInt = False
                        elif ((((((((((_g == "9") or ((_g == "8"))) or ((_g == "7"))) or ((_g == "6"))) or ((_g == "5"))) or ((_g == "4"))) or ((_g == "3"))) or ((_g == "2"))) or ((_g == "1"))) or ((_g == "0"))):
                            pass
                        elif ((((((((((((_g == "f") or ((_g == "e"))) or ((_g == "d"))) or ((_g == "c"))) or ((_g == "b"))) or ((_g == "a"))) or ((_g == "F"))) or ((_g == "E"))) or ((_g == "D"))) or ((_g == "C"))) or ((_g == "B"))) or ((_g == "A"))):
                            isInt = False
                            isFloat = False
                        elif ((_g == "x") or ((_g == "X"))):
                            if foundX:
                                isHex = False
                                break
                            else:
                                foundX = True
                            isFloat = False
                            isInt = False
                        else:
                            isFloat = False
                            isHex = False
                            isInt = False
                            break
                        i = (i + 1)
                    if isFloat:
                        result = Std.parseFloat(_hx_str)
                    elif isHex:
                        if foundX:
                            result = Std.parseInt(_hx_str)
                        else:
                            result = Std.parseInt(("0x" + ("null" if _hx_str is None else _hx_str)))
                    elif isInt:
                        result = Std.parseInt(_hx_str)
                    else:
                        result = _hx_str
            elif (_hx_local_0 == 4):
                if (_g == "true"):
                    result = True
                else:
                    while (i < len(_hx_str)):
                        _g = ("" if (((i < 0) or ((i >= len(_hx_str))))) else _hx_str[i])
                        if ((_g == ".") or ((_g == ","))):
                            if foundPoint:
                                isFloat = False
                                break
                            else:
                                foundPoint = True
                            isHex = False
                            isInt = False
                        elif ((((((((((_g == "9") or ((_g == "8"))) or ((_g == "7"))) or ((_g == "6"))) or ((_g == "5"))) or ((_g == "4"))) or ((_g == "3"))) or ((_g == "2"))) or ((_g == "1"))) or ((_g == "0"))):
                            pass
                        elif ((((((((((((_g == "f") or ((_g == "e"))) or ((_g == "d"))) or ((_g == "c"))) or ((_g == "b"))) or ((_g == "a"))) or ((_g == "F"))) or ((_g == "E"))) or ((_g == "D"))) or ((_g == "C"))) or ((_g == "B"))) or ((_g == "A"))):
                            isInt = False
                            isFloat = False
                        elif ((_g == "x") or ((_g == "X"))):
                            if foundX:
                                isHex = False
                                break
                            else:
                                foundX = True
                            isFloat = False
                            isInt = False
                        else:
                            isFloat = False
                            isHex = False
                            isInt = False
                            break
                        i = (i + 1)
                    if isFloat:
                        result = Std.parseFloat(_hx_str)
                    elif isHex:
                        if foundX:
                            result = Std.parseInt(_hx_str)
                        else:
                            result = Std.parseInt(("0x" + ("null" if _hx_str is None else _hx_str)))
                    elif isInt:
                        result = Std.parseInt(_hx_str)
                    else:
                        result = _hx_str
            else:
                while (i < len(_hx_str)):
                    _g = ("" if (((i < 0) or ((i >= len(_hx_str))))) else _hx_str[i])
                    if ((_g == ".") or ((_g == ","))):
                        if foundPoint:
                            isFloat = False
                            break
                        else:
                            foundPoint = True
                        isHex = False
                        isInt = False
                    elif ((((((((((_g == "9") or ((_g == "8"))) or ((_g == "7"))) or ((_g == "6"))) or ((_g == "5"))) or ((_g == "4"))) or ((_g == "3"))) or ((_g == "2"))) or ((_g == "1"))) or ((_g == "0"))):
                        pass
                    elif ((((((((((((_g == "f") or ((_g == "e"))) or ((_g == "d"))) or ((_g == "c"))) or ((_g == "b"))) or ((_g == "a"))) or ((_g == "F"))) or ((_g == "E"))) or ((_g == "D"))) or ((_g == "C"))) or ((_g == "B"))) or ((_g == "A"))):
                        isInt = False
                        isFloat = False
                    elif ((_g == "x") or ((_g == "X"))):
                        if foundX:
                            isHex = False
                            break
                        else:
                            foundX = True
                        isFloat = False
                        isInt = False
                    else:
                        isFloat = False
                        isHex = False
                        isInt = False
                        break
                    i = (i + 1)
                if isFloat:
                    result = Std.parseFloat(_hx_str)
                elif isHex:
                    if foundX:
                        result = Std.parseInt(_hx_str)
                    else:
                        result = Std.parseInt(("0x" + ("null" if _hx_str is None else _hx_str)))
                elif isInt:
                    result = Std.parseInt(_hx_str)
                else:
                    result = _hx_str
        com_sdtk_table_DataTableRowReader._watch.end()
        return result

    def convertToAll(self,rowWriters):
        self.start()
        rowWriter = HxOverrides.iterator(rowWriters)
        while rowWriter.hasNext():
            rowWriter1 = rowWriter.next()
            rowWriter1.start()
        while self.hasNext():
            data = self.next()
            sName = self.name()
            iIndex = self.index()
            rowWriter = HxOverrides.iterator(rowWriters)
            while rowWriter.hasNext():
                rowWriter1 = rowWriter.next()
                if (rowWriter1 is not None):
                    rowWriter1.write(data,sName,iIndex)

    def alwaysString(self,value = None):
        if (value is None):
            return self._alwaysString
        else:
            self._alwaysString = value
            return self._alwaysString


class com_sdtk_table_ArrayRowReader(com_sdtk_table_DataTableRowReader):

    def __init__(self,info):
        self._info = None
        self._i = None
        super().__init__()
        self.reuse(info)

    def reuse(self,info):
        self._info = info
        self._i = info._start
        self._started = False
        self._index = -1
        self._rawIndex = -1
        self._started = False
        self._value = None

    def hasNext(self):
        return (self._i <= self._info._end)

    def next(self):
        self._name = Std.string(self._index)
        self._value = python_internal_ArrayImpl._get(self._info._arr, self._i)
        self.incrementTo(None,self._value,self._i)
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._i
        _hx_local_0._i = (_hx_local_1 + self._info._increment)
        _hx_local_0._i
        return self._value

    def iterator(self):
        return com_sdtk_table_ArrayRowReader(self._info)

    def reset(self):
        self._i = self._info._start

    def dispose(self):
        if (self._info is not None):
            self._info = None

    @staticmethod
    def continueRead(info,start,end):
        return com_sdtk_table_ArrayRowReader.continueReadReuse(info,start,end,None)

    @staticmethod
    def readPartOfArray(arr,start,end,increment):
        return com_sdtk_table_ArrayRowReader.readPartOfArrayReuse(arr,start,end,increment,None)

    @staticmethod
    def readWholeArray(arr):
        return com_sdtk_table_ArrayRowReader.readWholeArrayReuse(arr,None)

    @staticmethod
    def continueReadReuse(info,start,end,rowReader):
        info1 = com_sdtk_table_ArrayInfo(info._arr,start,end,info._entriesInRow,info._increment,info._rowIncrement)
        if (rowReader is None):
            rowReader = com_sdtk_table_ArrayRowReader(info1)
        else:
            rowReader.reuse(info1)
        return rowReader

    @staticmethod
    def readPartOfArrayReuse(arr,start,end,increment,rowReader):
        info = com_sdtk_table_ArrayInfo(arr,start,end,(len(arr) - 1),increment,1)
        if (rowReader is None):
            rowReader = com_sdtk_table_ArrayRowReader(info)
        else:
            rowReader.reuse(info)
        return rowReader

    @staticmethod
    def readWholeArrayReuse(arr,rowReader):
        info = com_sdtk_table_ArrayInfo(arr,0,(len(arr) - 1),(len(arr) - 1),1,0)
        if (rowReader is None):
            rowReader = com_sdtk_table_ArrayRowReader(info)
        else:
            rowReader.reuse(info)
        return rowReader


class com_sdtk_table_ArrayRowWriter(com_sdtk_table_DataTableRowWriter):

    def __init__(self,info):
        self._info = None
        self._i = None
        super().__init__()
        self.reuse(info)

    def reuse(self,info):
        self._info = info
        self._i = info._start

    def write(self,data,name,index):
        if (self._info is not None):
            if ((self._info._end >= 0) and (((index + self._info._start) > self._info._end))):
                return
            arr = self._info._arr
            while (len(arr) <= index):
                arr.append(None)
            python_internal_ArrayImpl._set(arr, index, data)

    def reset(self):
        self._i = self._info._start

    def dispose(self):
        if (self._info is not None):
            self._info = None

    @staticmethod
    def continueWrite(info,start,end):
        return com_sdtk_table_ArrayRowWriter.continueWriteReuse(info,start,end,None)

    @staticmethod
    def writeToPartOfArray(arr,start,end,increment):
        return com_sdtk_table_ArrayRowWriter.writeToPartOfArrayReuse(arr,start,end,increment,None)

    @staticmethod
    def writeToWholeArray(arr):
        return com_sdtk_table_ArrayRowWriter.writeToWholeArrayReuse(arr,None)

    @staticmethod
    def writeToExpandableArray(arr):
        return com_sdtk_table_ArrayRowWriter.writeToExpandableArrayReuse(arr,None)

    @staticmethod
    def continueWriteReuse(info,start,end,rowWriter):
        info1 = com_sdtk_table_ArrayInfo(info._arr,start,end,info._entriesInRow,info._increment,info._rowIncrement)
        if (rowWriter is None):
            rowWriter = com_sdtk_table_ArrayRowWriter(info1)
        else:
            rowWriter.reuse(info1)
        return rowWriter

    @staticmethod
    def writeToPartOfArrayReuse(arr,start,end,increment,rowWriter):
        info = com_sdtk_table_ArrayInfo(arr,start,end,(len(arr) - 1),increment,1)
        if (rowWriter is None):
            rowWriter = com_sdtk_table_ArrayRowWriter(info)
        else:
            rowWriter.reuse(info)
        return rowWriter

    @staticmethod
    def writeToWholeArrayReuse(arr,rowWriter):
        info = com_sdtk_table_ArrayInfo(arr,0,(len(arr) - 1),(len(arr) - 1),1,0)
        if (rowWriter is None):
            rowWriter = com_sdtk_table_ArrayRowWriter(info)
        else:
            rowWriter.reuse(info)
        return rowWriter

    @staticmethod
    def writeToExpandableArrayReuse(arr,rowWriter):
        info = com_sdtk_table_ArrayInfo(arr,0,-1,-1,1,0)
        if (rowWriter is None):
            rowWriter = com_sdtk_table_ArrayRowWriter(info)
        else:
            rowWriter.reuse(info)
        return rowWriter


class com_sdtk_table_ArrayWriter(com_sdtk_table_DataTableWriter):

    def __init__(self,info):
        self._info = None
        self._i = None
        super().__init__()
        self._info = info
        self._i = info._start

    def start(self):
        pass

    def writeStartI(self,name,index,rowWriter):
        if ((self._info._end >= 0) and (((index + self._info._start) > self._info._end))):
            return None
        rowWriter1 = com_sdtk_table_ArrayRowWriter.continueWriteReuse(self._info,self._i,((self._i + self._info._entriesInRow) - 1),rowWriter)
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._i
        _hx_local_0._i = (_hx_local_1 + self._info._rowIncrement)
        _hx_local_0._i
        return rowWriter1

    def dispose(self):
        if (self._info is not None):
            print(str(self._info._arr))
            self._info = None

    @staticmethod
    def writeToSlicesOfArray(arr,start,end,entriesInRow,increment,rowIncrement):
        return com_sdtk_table_ArrayWriter(com_sdtk_table_ArrayInfo(arr,start,end,entriesInRow,increment,rowIncrement))

    @staticmethod
    def writeToPartOfArray(arr,start,end,increment):
        return com_sdtk_table_ArrayWriter(com_sdtk_table_ArrayInfo(arr,start,end,(len(arr) - 1),increment,1))

    @staticmethod
    def writeToWholeArray(arr):
        return com_sdtk_table_ArrayWriter(com_sdtk_table_ArrayInfo(arr,0,(len(arr) - 1),(len(arr) - 1),1,0))

    @staticmethod
    def writeToExpandableArray(arr):
        return com_sdtk_table_ArrayWriter(com_sdtk_table_ArrayInfo(arr,0,-1,-1,1,0))


class com_sdtk_table_FileSystemHandler:
    pass


class com_sdtk_table_CMDDirHandler:

    def __init__(self):
        self._NAME = 2
        self._extension = "."
        self._tilde = "~"
        self._zero = "0"
        self._footerFreeSpace = " bytes free"
        self._total = "     Total Files Listed:"
        self._footerSize = "  bytes"
        self._footerDirs = " Dir(s)  "
        self._footerFiles = " File(s) "
        self._trueNameEnd = "]"
        self._trueNameStart = "["
        self._space = " "
        self._numberSeparator = ","
        self._dateIndicator = "/"
        self._timeIndicator = ":"
        self._driveIndicator = ":"
        self._startOfSection = " "
        self._endOfSection = "\n\n"
        self._endOfEntry = "\n"
        self._directorySeparator = "\\"
        self._noDirIndicator = "     "
        self._junctionIndicator2 = "    "
        self._junctionIndicator = "<JUNCTION>"
        self._dirIndicator2 = "         "
        self._dirIndicator = "<DIR>"
        self._dtSeparator = "    "
        self._timeSeparator = "  "
        self._secondEntry = " .."
        self._firstEntry = " ."
        self._directoryOf = " Directory of "
        self._serial = " Volume Serial Number is "
        self._is = " is "
        self._volumeInDrive = " Volume in drive "

    def convertFromDateTime(self,dDate):
        iHours = dDate.date.hour
        return ((((((((((Std.string(((dDate.date.month - 1) - 1)) + "/") + Std.string(dDate.date.day)) + "/") + Std.string(dDate.date.year)) + " ") + Std.string(((12 if (((iHours == 0) or ((iHours == 12)))) else HxOverrides.mod(iHours, 12))))) + ":") + Std.string(dDate.date.minute)) + " ") + HxOverrides.stringOrNull((("AM" if ((iHours < 12)) else "PM"))))

    def convertToDate(self,sDate):
        iMonth = Std.parseInt(HxString.substr(sDate,0,2))
        iDay = Std.parseInt(HxString.substr(sDate,2,2))
        iYear = Std.parseInt(HxString.substr(sDate,4,4))
        return Date(iYear,(iMonth - 1),iDay,0,0,0)

    def convertToTime(self,sTime):
        iHours = Std.parseInt(HxString.substr(sTime,0,2))
        if (HxString.substr(sTime,4,2).lower() == "pm"):
            if (iHours < 12):
                iHours = (iHours + 12)
        elif (iHours == 12):
            iHours = 0
        iMinutes = ((iHours * 60) + Std.parseInt(HxString.substr(sTime,2,2)))
        return ((iMinutes * 60) * 1000)

    def convertToSize(self,sSize):
        return Std.parseInt(StringTools.replace(StringTools.replace(sSize,self._numberSeparator,""),self._space,""))

    def convertFromSize(self,iSize,iOptions):
        if (iSize <= 0):
            return self._zero
        elif (iSize < 1000):
            return Std.string(iSize)
        elif (((iOptions & com_sdtk_table_CMDDirHandler.OPTION_COMMAS)) != 0):
            sParts = list()
            while (iSize > 0):
                iPart = HxOverrides.mod(iSize, 1000)
                iSize1 = None
                try:
                    iSize1 = int((iSize / 1000))
                except BaseException as _g:
                    None
                    iSize1 = None
                iSize = iSize1
                x = Std.string(iPart)
                sParts.append(x)
            sParts.reverse()
            return self._numberSeparator.join([python_Boot.toString1(x1,'') for x1 in sParts])
        else:
            return Std.string(iSize)

    def convertFromCount(self,iCount):
        return Std.string(iCount)

    def displayFooter(self,wWriter,diInfo,iOptions,tiTally):
        iCount = diInfo.getCount()
        iSize = diInfo.getSize()
        wWriter.write(self.convertFromCount(iCount))
        wWriter.write(self._footerFiles)
        wWriter.write(self.convertFromSize(iSize,iOptions))
        wWriter.write(self._footerSize)
        wWriter.write(self._endOfSection)
        tiTally.add(iCount,iSize)

    def write(self,wWriter,fiPrevious,fiCurrent,iOptions,tiTally):
        if (((iOptions & com_sdtk_table_CMDDirHandler.OPTION_BARE)) == com_sdtk_table_CMDDirHandler.OPTION_BARE):
            wWriter.write(fiCurrent.getName())
            wWriter.write(self._endOfEntry)
        elif (((iOptions & com_sdtk_table_CMDDirHandler.OPTION_FULL_PATH)) == com_sdtk_table_CMDDirHandler.OPTION_FULL_PATH):
            wWriter.write(fiCurrent.getFullPath())
            wWriter.write(self._endOfEntry)
        else:
            if (fiCurrent is None):
                self.displayFooter(wWriter,fiPrevious.getDirectoryInfo(),iOptions,tiTally)
                if (tiTally.getNumberOfEntries() > 1):
                    wWriter.write(self._total)
                    wWriter.write(self._endOfEntry)
                    wWriter.write(self.convertFromCount(tiTally.getFileCount()))
                    wWriter.write(self._footerFiles)
                    wWriter.write(self.convertFromSize(tiTally.getFileSize(),iOptions))
                    wWriter.write(self._footerSize)
                    wWriter.write(self._endOfEntry)
                    wWriter.write(self.convertFromCount(tiTally.getNumberOfEntries()))
                    wWriter.write(self._footerDirs)
                    try:
                        wWriter.write(self.convertFromSize(tiTally.getFreeSpace(),iOptions))
                        wWriter.write(self._footerFreeSpace)
                    except BaseException as _g:
                        None
                    wWriter.write(self._endOfSection)
            elif ((fiPrevious is None) or ((fiPrevious.getDrive() != fiCurrent.getDrive()))):
                if (fiPrevious is not None):
                    self.displayFooter(wWriter,fiPrevious.getDirectoryInfo(),iOptions,tiTally)
                wWriter.write(self._volumeInDrive)
                wWriter.write(fiCurrent.getDrive())
                wWriter.write(self._is)
                wWriter.write(fiCurrent.getLabel())
                wWriter.write(self._endOfEntry)
                wWriter.write(self._serial)
                wWriter.write(fiCurrent.getSerial())
                wWriter.write(self._endOfSection)
                wWriter.write(self._directoryOf)
                wWriter.write(fiCurrent.getDirectory())
                wWriter.write(self._endOfSection)
            elif (fiPrevious.getDirectory() != fiCurrent.getDirectory()):
                wWriter.write(self._directoryOf)
                wWriter.write(fiCurrent.getDirectory())
                wWriter.write(self._endOfSection)
            wWriter.write(self.convertFromDateTime(fiCurrent.getDate()))
            wWriter.write(self._dtSeparator)
            if fiCurrent.getIsDirectory():
                wWriter.write(self._dirIndicator)
                wWriter.write(self._dirIndicator2)
            elif fiCurrent.getIsJunction():
                wWriter.write(self._junctionIndicator)
                wWriter.write(self._junctionIndicator2)
            else:
                wWriter.write(self.convertFromSize(fiCurrent.getSize(),iOptions))
                if (((iOptions & com_sdtk_table_CMDDirHandler.OPTION_SHORT_NAME)) == com_sdtk_table_CMDDirHandler.OPTION_SHORT_NAME):
                    if (((iOptions & com_sdtk_table_CMDDirHandler.OPTION_LOWER_CASE_NAMES)) == com_sdtk_table_CMDDirHandler.OPTION_LOWER_CASE_NAMES):
                        wWriter.write(fiCurrent.getShortName().lower())
                    else:
                        wWriter.write(fiCurrent.getShortName())
                if (((iOptions & com_sdtk_table_CMDDirHandler.OPTION_OWNER_NAME)) == com_sdtk_table_CMDDirHandler.OPTION_OWNER_NAME):
                    wWriter.write(fiCurrent.getOwner())
                if (((iOptions & com_sdtk_table_CMDDirHandler.OPTION_LOWER_CASE_NAMES)) == com_sdtk_table_CMDDirHandler.OPTION_LOWER_CASE_NAMES):
                    wWriter.write(fiCurrent.getName().lower())
                else:
                    wWriter.write(fiCurrent.getName())
                if (((iOptions & com_sdtk_table_CMDDirHandler.OPTION_TRUE_NAME)) == com_sdtk_table_CMDDirHandler.OPTION_TRUE_NAME):
                    sTrueName = fiCurrent.getTrueName()
                    if ((sTrueName is not None) and ((len(sTrueName) > 0))):
                        wWriter.write(self._trueNameStart)
                        wWriter.write(sTrueName)
                        wWriter.write(self._trueNameEnd)
                wWriter.write(self._endOfEntry)

    def next(self,rReader,fiPrevious):
        rReader = rReader.switchToLineReader()
        sLine = rReader.next()
        if (sLine is not None):
            sCurrentDrive = None
            sCurrentLabel = None
            sCurrentSerial = None
            sCurrentDirectory = None
            bChanged = False
            if (fiPrevious is not None):
                sCurrentDrive = fiPrevious.getDrive()
                sCurrentLabel = fiPrevious.getLabel()
                sCurrentSerial = fiPrevious.getSerial()
                sCurrentDirectory = fiPrevious.getDirectory()
            while True:
                start = self._startOfSection
                if sLine.startswith(start):
                    break
                start1 = self._volumeInDrive
                if sLine.startswith(start1):
                    sLine = HxString.substr(sLine,0,len(self._volumeInDrive))
                    _hx_str = self._is
                    startIndex = None
                    iIs = None
                    if (startIndex is None):
                        iIs = sLine.rfind(_hx_str, 0, len(sLine))
                    elif (_hx_str == ""):
                        length = len(sLine)
                        if (startIndex < 0):
                            startIndex = (length + startIndex)
                            if (startIndex < 0):
                                startIndex = 0
                        iIs = (length if ((startIndex > length)) else startIndex)
                    else:
                        i = sLine.rfind(_hx_str, 0, (startIndex + 1))
                        startLeft = (max(0,((startIndex + 1) - len(_hx_str))) if ((i == -1)) else (i + 1))
                        check = sLine.find(_hx_str, startLeft, len(sLine))
                        iIs = (check if (((check > i) and ((check <= startIndex)))) else i)
                    sCurrentDrive = HxString.substr(sLine,0,iIs)
                    sCurrentLabel = HxString.substr(sLine,(iIs + len(self._is)),None)
                    bChanged = True
                else:
                    start2 = self._serial
                    if sLine.startswith(start2):
                        sCurrentSerial = HxString.substr(sLine,len(self._serial),None)
                        bChanged = True
                    else:
                        start3 = self._directoryOf
                        if sLine.startswith(start3):
                            sCurrentDirectory = HxString.substr(sLine,len(self._directoryOf),None)
                            bChanged = True
                sLine = rReader.next()
                if (sLine is None):
                    return None
            while True:
                tmp = None
                end = self._firstEntry
                if (not sLine.endswith(end)):
                    end1 = self._secondEntry
                    tmp = sLine.endswith(end1)
                else:
                    tmp = True
                if (not tmp):
                    break
                sLine = rReader.next()
                if (sLine is None):
                    return None
            fiNew = com_sdtk_table_FileInfo()
            if ((("" if ((1 >= len(sLine))) else sLine[1])) == self._driveIndicator):
                _hx_str = self._directorySeparator
                startIndex = None
                iSeparator = None
                if (startIndex is None):
                    iSeparator = sLine.rfind(_hx_str, 0, len(sLine))
                elif (_hx_str == ""):
                    length = len(sLine)
                    if (startIndex < 0):
                        startIndex = (length + startIndex)
                        if (startIndex < 0):
                            startIndex = 0
                    iSeparator = (length if ((startIndex > length)) else startIndex)
                else:
                    i = sLine.rfind(_hx_str, 0, (startIndex + 1))
                    startLeft = (max(0,((startIndex + 1) - len(_hx_str))) if ((i == -1)) else (i + 1))
                    check = sLine.find(_hx_str, startLeft, len(sLine))
                    iSeparator = (check if (((check > i) and ((check <= startIndex)))) else i)
                sNewDrive = HxString.substr(sLine,0,1)
                sNewDirectory = HxString.substr(sLine,0,iSeparator)
                diNew = None
                if ((sCurrentDirectory != sNewDirectory) or ((sCurrentDrive != sNewDrive))):
                    diNew = com_sdtk_table_DirectoryInfo()
                    diNew.setDrive(sNewDrive)
                    diNew.setFullPath(sNewDirectory)
                else:
                    diNew = fiPrevious.getDirectoryInfo()
                fiNew.setDirectoryInfo(diNew)
                fiNew.setName(HxString.substr(sLine,(iSeparator + 1),None))
            elif ((((len(sLine) < 27) or (((("" if ((2 >= len(sLine))) else sLine[2])) != self._dateIndicator))) or (((("" if ((5 >= len(sLine))) else sLine[5])) != self._dateIndicator))) or (((("" if ((14 >= len(sLine))) else sLine[14])) != self._timeIndicator))):
                fiNew.setName(sLine)
            else:
                diNew = None
                if bChanged:
                    diNew = com_sdtk_table_DirectoryInfo()
                    diNew.setDrive(sCurrentDrive)
                    diNew.setLabel(sCurrentLabel)
                    diNew.setSerial(sCurrentSerial)
                    diNew.setFullPath(sCurrentDirectory)
                elif (fiPrevious is not None):
                    diNew = fiPrevious.getDirectoryInfo()
                else:
                    diNew = com_sdtk_table_DirectoryInfo()
                fiNew.setDirectoryInfo(diNew)
                _hx_str = self._timeSeparator
                startIndex = None
                iSeparator = (sLine.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sLine,_hx_str,startIndex))
                fiNew.setDate(self.convertToDate(HxString.substr(sLine,0,iSeparator)))
                sLine = HxString.substr(sLine,(iSeparator + len(self._timeSeparator)),None)
                _hx_str = self._dtSeparator
                startIndex = None
                iSeparator = (sLine.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sLine,_hx_str,startIndex))
                fiNew.setTime(self.convertToTime(HxString.substr(sLine,0,iSeparator)))
                sLine = HxString.substr(sLine,(iSeparator + len(self._dtSeparator)),None)
                start = self._dirIndicator
                if sLine.startswith(start):
                    fiNew.setIsDirectory(True)
                    sLine = HxString.substr(sLine,len(self._dirIndicator),None)
                else:
                    start = self._junctionIndicator
                    if sLine.startswith(start):
                        fiNew.setIsJunction(True)
                        sLine = HxString.substr(sLine,len(self._junctionIndicator),None)
                    else:
                        sLine = StringTools.ltrim(sLine)
                        startIndex = None
                        iSeparator = (sLine.find(" ") if ((startIndex is None)) else HxString.indexOfImpl(sLine," ",startIndex))
                        fiNew.setSize(self.convertToSize(HxString.substring(sLine,0,iSeparator)))
                        sLine = HxString.substring(sLine,(iSeparator + 1),None)
                        _hx_str = self._driveIndicator
                        startIndex = None
                        iTruePathLocation = None
                        if (startIndex is None):
                            iTruePathLocation = sLine.rfind(_hx_str, 0, len(sLine))
                        elif (_hx_str == ""):
                            length = len(sLine)
                            if (startIndex < 0):
                                startIndex = (length + startIndex)
                                if (startIndex < 0):
                                    startIndex = 0
                            iTruePathLocation = (length if ((startIndex > length)) else startIndex)
                        else:
                            i = sLine.rfind(_hx_str, 0, (startIndex + 1))
                            startLeft = (max(0,((startIndex + 1) - len(_hx_str))) if ((i == -1)) else (i + 1))
                            check = sLine.find(_hx_str, startLeft, len(sLine))
                            iTruePathLocation = (check if (((check > i) and ((check <= startIndex)))) else i)
                        if (iTruePathLocation > 0):
                            iTruePathLocation = (iTruePathLocation - 1)
                            _hx_str = self._trueNameEnd
                            startIndex = None
                            iTruePathEnd = None
                            if (startIndex is None):
                                iTruePathEnd = sLine.rfind(_hx_str, 0, len(sLine))
                            elif (_hx_str == ""):
                                length = len(sLine)
                                if (startIndex < 0):
                                    startIndex = (length + startIndex)
                                    if (startIndex < 0):
                                        startIndex = 0
                                iTruePathEnd = (length if ((startIndex > length)) else startIndex)
                            else:
                                i = sLine.rfind(_hx_str, 0, (startIndex + 1))
                                startLeft = (max(0,((startIndex + 1) - len(_hx_str))) if ((i == -1)) else (i + 1))
                                check = sLine.find(_hx_str, startLeft, len(sLine))
                                iTruePathEnd = (check if (((check > i) and ((check <= startIndex)))) else i)
                            if (iTruePathEnd < iTruePathLocation):
                                iTruePathEnd = len(sLine)
                            fiNew.setTrueName(HxString.substr(sLine,iTruePathLocation,(iTruePathEnd - iTruePathLocation)))
                            sLine = HxString.substr(sLine,0,iTruePathLocation)
                            end = self._trueNameStart
                            if sLine.endswith(end):
                                sLine = HxString.substr(sLine,0,(iTruePathLocation - 1))
                            sLine = StringTools.rtrim(sLine)
                        _hx_str = self._startOfSection
                        startIndex = None
                        iEndOfFirstColumn = (sLine.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sLine,_hx_str,startIndex))
                        _hx_str = self._tilde
                        startIndex = None
                        iTilde = (sLine.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sLine,_hx_str,startIndex))
                        _hx_str = self._extension
                        startIndex = None
                        iNameLength = (sLine.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sLine,_hx_str,startIndex))
                        _hx_str = self._directorySeparator
                        startIndex = None
                        iDirectory = (sLine.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sLine,_hx_str,startIndex))
                        if ((((iEndOfFirstColumn > iTilde) and ((iEndOfFirstColumn > iNameLength))) and ((iNameLength >= iTilde))) and (((iDirectory < 0) or ((iDirectory > iEndOfFirstColumn))))):
                            fiNew.setShortName(HxString.substr(sLine,0,iEndOfFirstColumn))
                            sLine = HxString.substr(sLine,(iEndOfFirstColumn + 1),None)
                        sOwner = HxString.substr(sLine,0,23)
                        _hx_str = self._directorySeparator
                        startIndex = None
                        if (((sOwner.find(_hx_str) if ((startIndex is None)) else HxString.indexOfImpl(sOwner,_hx_str,startIndex))) > 0):
                            sOwner = StringTools.rtrim(sOwner)
                            fiNew.setOwner(sOwner)
                            sLine = HxString.substr(sLine,23,None)
                        fiNew.setName(sLine)
            return fiNew
        else:
            return None


class com_sdtk_table_DelimitedInfo:
    pass


class com_sdtk_table_CSVInfo:

    def __init__(self):
        pass

    def fileStart(self):
        return ""

    def fileEnd(self):
        return ""

    def delimiter(self):
        return ","

    def rowDelimiter(self):
        return "\n"

    def boolStart(self):
        return ""

    def boolEnd(self):
        return ""

    def stringStart(self):
        return "\""

    def stringEnd(self):
        return "\""

    def intStart(self):
        return ""

    def intEnd(self):
        return ""

    def floatStart(self):
        return ""

    def floatEnd(self):
        return ""

    def replacements(self):
        return ["\\\\", "\\", "\"\"", "\"", "\\\n", "\n", "\\\t", "\t", "\\\r", "\r"]

    def replacementIndicator(self):
        return "\\"

    def widthMinimum(self):
        return -1

    def widthMaximum(self):
        return -1


class com_sdtk_table_CodeInfo:
    pass


class com_sdtk_table_CSharpInfoAbstract:

    def __init__(self):
        pass

    def start(self):
        return ""

    def end(self):
        return ""

    def arrayStart(self):
        return "new [] { "

    def arrayEnd(self):
        return " }"

    def mapStart(self):
        return "new Dictionary<object, object> {"

    def mapEnd(self):
        return " }"

    def rowStart(self,name,index):
        return ""

    def rowEnd(self):
        return ""

    def betweenRows(self):
        return ",\n"

    def mapRowEnd(self):
        return "}"

    def arrayRowEnd(self):
        return ""

    def arrayRowStart(self,name,index):
        return ""

    def mapRowStart(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("[\"" + ("null" if name is None else name)) + "\"] = ")
        else:
            return (("[" + Std.string(index)) + "] = ")

    def mapIntEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return ((("[\"" + ("null" if name is None else name)) + "\"] = ") + Std.string(data))
        else:
            return ((("[" + Std.string(index)) + "] = ") + Std.string(data))

    def mapBoolEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return ((("[\"" + ("null" if name is None else name)) + "\"] = ") + Std.string(data))
        else:
            return ((("[" + Std.string(index)) + "] = ") + Std.string(data))

    def mapFloatEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return ((("[\"" + ("null" if name is None else name)) + "\"] = ") + Std.string(data))
        else:
            return ((("[" + Std.string(index)) + "] = ") + Std.string(data))

    def mapOtherEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("[\"" + ("null" if name is None else name)) + "\"] = \"") + ("null" if data is None else data)) + "\"")
        else:
            return (((("[" + Std.string(index)) + "] = \"") + ("null" if data is None else data)) + "\"")

    def mapNullEntry(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("[\"" + ("null" if name is None else name)) + "\"] = null")
        else:
            return (("[" + Std.string(index)) + "] = null")

    def arrayIntEntry(self,data,name,index):
        return Std.string(data)

    def arrayBoolEntry(self,data,name,index):
        return Std.string(data)

    def arrayFloatEntry(self,data,name,index):
        return Std.string(data)

    def arrayOtherEntry(self,data,name,index):
        return (("\"" + ("null" if data is None else data)) + "\"")

    def arrayNullEntry(self,name,index):
        return "null"

    def intEntry(self,data,name,index):
        return None

    def boolEntry(self,data,name,index):
        return None

    def floatEntry(self,data,name,index):
        return None

    def otherEntry(self,data,name,index):
        return None

    def nullEntry(self,name,index):
        return None

    def betweenEntries(self):
        return ","

    def replacements(self):
        return ["\\\"", "\"", "\\\n", "\n", "\\\t", "\t"]


class com_sdtk_table_CSharpInfoArrayOfArrays(com_sdtk_table_CSharpInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.arrayStart()

    def end(self):
        return self.arrayEnd()

    def rowEnd(self):
        return self.arrayEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.arrayRowStart(name,index)) + HxOverrides.stringOrNull(self.arrayStart()))

    def intEntry(self,data,name,index):
        return self.arrayIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.arrayBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.arrayFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.arrayOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.arrayNullEntry(name,index)


class com_sdtk_table_CSharpInfoArrayOfMaps(com_sdtk_table_CSharpInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.arrayStart()

    def end(self):
        return self.arrayEnd()

    def rowEnd(self):
        return self.mapEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.arrayRowStart(name,index)) + HxOverrides.stringOrNull(self.mapStart()))

    def intEntry(self,data,name,index):
        return self.mapIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntry(name,index)


class com_sdtk_table_CSharpInfoMapOfArrays(com_sdtk_table_CSharpInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.mapStart()

    def end(self):
        return self.mapEnd()

    def rowEnd(self):
        return self.arrayEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.mapRowStart(name,index)) + HxOverrides.stringOrNull(self.arrayStart()))

    def intEntry(self,data,name,index):
        return self.arrayIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.arrayBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.arrayFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.arrayOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.arrayNullEntry(name,index)


class com_sdtk_table_CSharpInfoMapOfMaps(com_sdtk_table_CSharpInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.mapStart()

    def end(self):
        return self.mapEnd()

    def rowEnd(self):
        return self.mapEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.mapRowStart(name,index)) + HxOverrides.stringOrNull(self.mapStart()))

    def intEntry(self,data,name,index):
        return self.mapIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntry(name,index)


class com_sdtk_table_CodeRowWriter(com_sdtk_table_DataTableRowWriter):

    def __init__(self,info,writer):
        self._writer = None
        self._done = False
        self._written = False
        self._info = None
        super().__init__()
        self.reuse(info,writer)

    def reuse(self,info,writer):
        self._done = False
        if self._written:
            self._writer.write(self._info.rowEnd())
            self._writer.flush()
        self._written = False
        self._info = info
        self._writer = writer

    def write(self,data,name,index):
        com_sdtk_table_CodeRowWriter._watch.start()
        buf = StringBuf()
        if (not self._done):
            if self._written:
                s = Std.string(self._info.betweenEntries())
                buf.b.write(s)
            else:
                self._written = True
            self.writeValue(data,name,index,buf)
            self._writer.write(buf.b.getvalue())
        com_sdtk_table_CodeRowWriter._watch.end()

    def replacement(self,data):
        replacements = self._info.replacements()
        if ((replacements is not None) and ((len(replacements) > 0))):
            replaceI = 1
            while (replaceI < len(replacements)):
                data = StringTools.replace(data,(replacements[replaceI] if replaceI >= 0 and replaceI < len(replacements) else None),python_internal_ArrayImpl._get(replacements, (replaceI - 1)))
                replaceI = (replaceI + 2)
        return data

    def writeValue(self,data,name,index,buf):
        if (data is not None):
            _g = Type.typeof(data)
            tmp = _g.index
            if (tmp == 1):
                s = Std.string(self._info.intEntry(data,name,index))
                buf.b.write(s)
            elif (tmp == 2):
                s = Std.string(self._info.floatEntry(data,name,index))
                buf.b.write(s)
            elif (tmp == 3):
                s = Std.string(self._info.boolEntry(data,name,index))
                buf.b.write(s)
            else:
                other = _g
                s = Std.string(self._info.otherEntry(self.replacement(data),name,index))
                buf.b.write(s)
        else:
            s = Std.string(self._info.nullEntry(name,index))
            buf.b.write(s)

    def dispose(self):
        if (not self._done):
            self._writer.write(self._info.rowEnd())
            self._writer.flush()
            self._done = True
            self._written = False


class com_sdtk_table_CodeWriter(com_sdtk_table_DataTableWriter):

    def __init__(self,diInfo,wWriter):
        self._writer = None
        self._done = False
        self._info = None
        super().__init__()
        self._info = diInfo
        self._writer = wWriter

    def start(self):
        self._writer.start()

    def writeStartI(self,name,index,rowWriter):
        if (self._written == 0):
            self._writer.write(self._info.start())
        if (rowWriter is None):
            self._writer.write(self._info.rowStart(name,index))
            rowWriter = com_sdtk_table_CodeRowWriter(self._info,self._writer)
        else:
            rw = rowWriter
            rw.reuse(self._info,self._writer)
            self._writer.write(self._info.betweenRows())
            self._writer.write(self._info.rowStart(name,index))
        return rowWriter

    def dispose(self):
        if (not self._done):
            self._writer.write(self._info.end())
            self._done = True
            self._writer.dispose()

    def writeHeaderFirst(self):
        return False

    def writeRowNameFirst(self):
        return False

    @staticmethod
    def createSQLSelectWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_SQLSelectInfo.instance,writer)

    @staticmethod
    def createSQLCreatetWriter(writer,name):
        return com_sdtk_table_CodeWriter(com_sdtk_table_SQLSelectInfo.createTable(name),writer)

    @staticmethod
    def createSQLCreatetOrReplaceWriter(writer,name):
        return com_sdtk_table_CodeWriter(com_sdtk_table_SQLSelectInfo.createOrReplaceTable(name),writer)

    @staticmethod
    def createSQLInsertSelectWriter(writer,name):
        return com_sdtk_table_CodeWriter(com_sdtk_table_SQLSelectInfo.insertIntoTable(name),writer)

    @staticmethod
    def createCSharpArrayOfArraysWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_CSharpInfoArrayOfArrays.instance,writer)

    @staticmethod
    def createCSharpArrayOfMapsWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_CSharpInfoArrayOfMaps.instance,writer)

    @staticmethod
    def createCSharpMapOfArraysWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_CSharpInfoMapOfArrays.instance,writer)

    @staticmethod
    def createCSharpMapOfMapsWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_CSharpInfoMapOfMaps.instance,writer)

    @staticmethod
    def createPythonArrayOfArraysWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_PythonInfoArrayOfArrays.instance,writer)

    @staticmethod
    def createPythonArrayOfMapsWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_PythonInfoArrayOfMaps.instance,writer)

    @staticmethod
    def createPythonMapOfArraysWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_PythonInfoMapOfArrays.instance,writer)

    @staticmethod
    def createPythonMapOfMapsWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_PythonInfoMapOfMaps.instance,writer)

    @staticmethod
    def createHaxeArrayOfArraysWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_HaxeInfoArrayOfArrays.instance,writer)

    @staticmethod
    def createHaxeArrayOfMapsWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_HaxeInfoArrayOfMaps.instance,writer)

    @staticmethod
    def createHaxeMapOfArraysWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_HaxeInfoMapOfArrays.instance,writer)

    @staticmethod
    def createHaxeMapOfMapsWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_HaxeInfoMapOfMaps.instance,writer)

    @staticmethod
    def createJavaArrayOfArraysWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_JavaInfoArrayOfArrays.instance,writer)

    @staticmethod
    def createJavaArrayOfMapsWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_JavaInfoArrayOfMaps.instance,writer)

    @staticmethod
    def createJavaMapOfArraysWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_JavaInfoMapOfArrays.instance,writer)

    @staticmethod
    def createJavaMapOfMapsWriter(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_JavaInfoMapOfMaps.instance,writer)

    @staticmethod
    def createJavaArrayOfMapsWriterLegacy(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_JavaInfoArrayOfMapsLegacy.instance,writer)

    @staticmethod
    def createJavaMapOfArraysWriterLegacy(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_JavaInfoMapOfArraysLegacy.instance,writer)

    @staticmethod
    def createJavaMapOfMapsWriterLegacy(writer):
        return com_sdtk_table_CodeWriter(com_sdtk_table_JavaInfoMapOfMapsLegacy.instance,writer)


class com_sdtk_table_ColumnFilterDataTableReader(com_sdtk_table_DataTableReader):

    def __init__(self,dtrReader,fColumnHeaderFilter):
        self._header = None
        self._columnHeaderFilter = None
        self._current = None
        self._remove = None
        self._reader = None
        self._prev = None
        self._sentHeader = False
        super().__init__()
        self._reader = dtrReader
        self._columnHeaderFilter = fColumnHeaderFilter

    def startI(self):
        self._reader.start()
        super().startI()
        if self._reader.hasNext():
            self._header = list()
            self._remove = list()
            dtrrHeader = self._reader.next()
            dtrrHeader.start()
            i = 0
            while dtrrHeader.hasNext():
                sValue = dtrrHeader.next()
                if (self._columnHeaderFilter.filter(sValue) is None):
                    _this = self._remove
                    _this.append(True)
                else:
                    _this1 = self._remove
                    _this1.append(False)
                _this2 = self._header
                _this2.append(sValue)
                i = (i + 1)

    def hasNext(self):
        if self._sentHeader:
            return self._reader.hasNext()
        else:
            return (self._header is not None)

    def nextReuse(self,rowReader):
        nextValue = None
        if ((rowReader is None) or ((self._index <= 0))):
            nextValue = self.nextI()
            nextValue = com_sdtk_table_ColumnFilterDataTableRowReader(nextValue,self._remove)
        else:
            rr = rowReader
            rr.reuse(self.nextI(),self._remove)
            nextValue = rr
        self.incrementTo(self._reader.name(),nextValue,self._reader.rawIndex())
        return self.value()

    def nextI(self):
        if self._sentHeader:
            self._prev = self._reader.nextReuse(self._prev)
            return self._prev
        else:
            self._sentHeader = True
            return com_sdtk_table_ArrayRowReader.readWholeArray(self._header)

    def next(self):
        return self.nextReuse(None)

    def isAutoNamed(self):
        return self._reader.isAutoNamed()

    def isNameIndex(self):
        return self._reader.isNameIndex()

    def headerRowNotIncluded(self):
        return self._reader.headerRowNotIncluded()

    def dispose(self):
        if (self._reader is not None):
            super().dispose()
            self._reader.dispose()
            self._reader = None
            self._remove = None
            self._current = None
            self._columnHeaderFilter = None
            self._header = None
            self._prev = None

    def reset(self):
        self._reader.reset()


class com_sdtk_table_ColumnFilterDataTableRowReader(com_sdtk_table_DataTableRowReader):

    def __init__(self,dtrrReader,iRemove):
        self._current = None
        self._remove = None
        self._reader = None
        super().__init__()
        self.reuse(dtrrReader,iRemove)

    def reuse(self,dtrrReader,iRemove):
        self._reader = dtrrReader
        self._remove = iRemove
        self._current = None
        self._started = False
        self._index = -1

    def startI(self):
        self._reader.start()
        self.check()
        super().startI()

    def check(self):
        if (self._reader is not None):
            self._current = self._reader.next()
            while python_internal_ArrayImpl._get(self._remove, self._reader.index()):
                self._current = self._reader.next()
                if (self._current is None):
                    return

    def hasNext(self):
        return (self._current is not None)

    def next(self):
        oCurrent = self._current
        self.incrementTo(self._reader.name(),oCurrent,self._reader.rawIndex())
        self.check()
        return oCurrent

    def isAutoNamed(self):
        return self._reader.isAutoNamed()

    def isNameIndex(self):
        return self._reader.isNameIndex()

    def dispose(self):
        if (self._reader is not None):
            super().dispose()
            self._reader.dispose()
            self._reader = None
            self._remove = None
            self._current = None


class com_sdtk_table_Converter:

    @staticmethod
    def convert(oSource,oTarget):
        com_sdtk_table_Converter.convertWithOptions(oSource,None,oTarget,None,None,None,None,None,None,False,False,None,None)

    @staticmethod
    def length(o):
        if com_sdtk_table_Converter.isString(o):
            s = o
            return Reflect.field(o,"length")
        elif Std.isOfType(o,list):
            a = o
            return len(a)
        else:
            return -1

    @staticmethod
    def isString(o):
        return Std.isOfType(o,str)

    @staticmethod
    def convertWithOptions(oSource,fSource,oTarget,fTarget,sFilterColumnsExclude,sFilterColumnsInclude,sFilterRowsExclude,sFilterRowsInclude,sSortRowsBy,leftTrim,rightTrim,inputOptions,outputOptions):
        com_sdtk_table_Converter._watch.start()
        aStages = list()
        error = None
        try:
            if ((sSortRowsBy is not None) and ((com_sdtk_table_Converter.length(sSortRowsBy) > 0))):
                awWriter = None
                if Std.isOfType(oTarget,com_sdtk_table_Array2DWriter):
                    awWriter = oTarget
                else:
                    awWriter = com_sdtk_table_Array2DWriter.writeToExpandableArray(None)
                x = com_sdtk_table_ConverterStageStandard(oSource,fSource,awWriter,com_sdtk_table_Format.ARRAY,sFilterColumnsExclude,sFilterColumnsInclude,sFilterRowsExclude,sFilterRowsInclude,leftTrim,rightTrim,inputOptions,None)
                aStages.append(x)
                if com_sdtk_table_Converter.isString(sSortRowsBy):
                    x = com_sdtk_table_ConverterStageSort.createWithArrayAndColumnsString(awWriter.getArray(),sSortRowsBy)
                    aStages.append(x)
                else:
                    x = com_sdtk_table_ConverterStageSort.createWithArrayAndColumns(awWriter.getArray(),sSortRowsBy)
                    aStages.append(x)
                if (awWriter != oTarget):
                    arReader = awWriter.flip()
                    x = com_sdtk_table_ConverterStageStandard(arReader,com_sdtk_table_Format.ARRAY,oTarget,fTarget,None,None,None,None,False,False,None,outputOptions)
                    aStages.append(x)
            else:
                x = com_sdtk_table_ConverterStageStandard(oSource,fSource,oTarget,fTarget,sFilterColumnsExclude,sFilterColumnsInclude,sFilterRowsExclude,sFilterRowsInclude,leftTrim,rightTrim,inputOptions,outputOptions)
                aStages.append(x)
            _g = 0
            while (_g < len(aStages)):
                csStage = (aStages[_g] if _g >= 0 and _g < len(aStages) else None)
                _g = (_g + 1)
                csStage.convert()
        except BaseException as _g:
            None
            message = haxe_Exception.caught(_g).unwrap()
            error = message
        _g = 0
        while (_g < len(aStages)):
            csStage = (aStages[_g] if _g >= 0 and _g < len(aStages) else None)
            _g = (_g + 1)
            try:
                csStage.dispose()
            except BaseException as _g1:
                None
        com_sdtk_table_Converter._watch.end()
        if (error is not None):
            raise haxe_Exception.thrown(error)

    @staticmethod
    def main():
        pParameters = com_sdtk_table_Parameters()
        if pParameters.getRunInTestMode():
            _hx_str = Std.string(com_sdtk_table_Tests.runTests(pParameters.getRecordPass(),pParameters.getVerbose()))
            python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        elif ((pParameters.getInput() is None) or ((pParameters.getOutput() is None))):
            pParameters.fullPrint()
        else:
            com_sdtk_table_Converter.convertWithOptions(pParameters.getInput(),pParameters.getInputFormat(),pParameters.getOutput(),pParameters.getOutputFormat(),pParameters.getFilterColumnsExclude(),pParameters.getFilterColumnsInclude(),pParameters.getFilterRowsExclude(),pParameters.getFilterRowsInclude(),pParameters.getSortRowsBy(),pParameters.getLeftTrim(),pParameters.getRightTrim(),pParameters.getInputOptions(),pParameters.getOutputOptions())
        com_sdtk_table_Stopwatch.printResults()

    @staticmethod
    def start():
        return com_sdtk_table_ConverterInputOptions()

    @staticmethod
    def quick():
        return com_sdtk_table_ConverterQuickInputOptions()


class com_sdtk_table_ConverterInputFormatOptions:

    def __init__(self,values = None):
        if (values is None):
            values = haxe_ds_StringMap()
        self._values = values

    def raw(self):
        return self.setSourceFormatDelimited(com_sdtk_table_Format.RAW)

    def csv(self):
        return self.setSourceFormatDelimited(com_sdtk_table_Format.CSV)

    def psv(self):
        return self.setSourceFormatDelimited(com_sdtk_table_Format.PSV)

    def tsv(self):
        return self.setSourceFormatDelimited(com_sdtk_table_Format.TSV)

    def htmlTable(self):
        return self.setSourceFormat(com_sdtk_table_Format.HTMLTable)

    def dir(self):
        return self.setSourceFormat(com_sdtk_table_Format.DIR)

    def ini(self):
        return self.setSourceFormat(com_sdtk_table_Format.INI)

    def json(self):
        return self.setSourceFormat(com_sdtk_table_Format.JSON)

    def properties(self):
        return self.setSourceFormat(com_sdtk_table_Format.PROPERTIES)

    def splunk(self):
        return self.setSourceFormat(com_sdtk_table_Format.SPLUNK)

    def setSourceFormat(self,value):
        self._values.h["sourceFormat"] = value
        return com_sdtk_table_ConverterInputOperationsOptions(self._values)

    def setSourceFormatDelimited(self,value):
        self._values.h["sourceFormat"] = value
        return com_sdtk_table_ConverterInputOperationsOptionsDelimited(self._values)


class com_sdtk_table_ConverterInputOperationsOptions:

    def __init__(self,values = None):
        if (values is None):
            values = haxe_ds_StringMap()
        self._values = values

    def excludeColumn(self,value):
        return self.mergeFilter("filterColumnsExclude",com_sdtk_std_FilterBlockEqualString(value))

    def includeColumn(self,value):
        return self.mergeFilter("filterColumnsInclude",com_sdtk_std_FilterAllowEqualString(value))

    def excludeRow(self,value):
        return self.mergeFilter("filterRowsExclude",com_sdtk_std_FilterBlockEqualString(value))

    def includeRow(self,value):
        return self.mergeFilter("filterRowsIncludee",com_sdtk_std_FilterAllowEqualString(value))

    def mergeFilter(self,key,value):
        current = self._values.h.get(key,None)
        if (current is None):
            current = list()
        current.append(value)
        self._values.h[key] = current
        return self

    def output(self):
        return com_sdtk_table_ConverterOutputOptions(self._values)


class com_sdtk_table_ConverterInputOperationsOptionsDelimited(com_sdtk_table_ConverterInputOperationsOptions):

    def __init__(self,values = None):
        super().__init__(values)

    def excludeHeader(self,value = None):
        if (value is None):
            value = True
        return self.setValue("header",(not value))

    def textOnly(self,value = None):
        if (value is None):
            value = True
        return self.setValue("textOnly",(not value))

    def setValue(self,key,value):
        options = self._values.h.get("inputOptions",None)
        if (options is None):
            options = haxe_ds_StringMap()
            self._values.h["inputOptions"] = options
        options.h[key] = value
        return self


class com_sdtk_table_ConverterInputOptions:

    def __init__(self,values = None):
        if (values is None):
            values = haxe_ds_StringMap()
        self._values = values

    def readFile(self,file):
        return self.setSource(file,"file")

    def readString(self,value):
        return self.setSource(value,"string")

    def readDatabase(self,value):
        self._values.h["source"] = value
        self._values.h["sourceType"] = "db"
        self._values.h["sourceFormat"] = com_sdtk_table_Format.DB
        return com_sdtk_table_ConverterInputOperationsOptions(self._values)

    def readArrayOfArrays(self,value):
        self._values.h["source"] = value
        self._values.h["sourceType"] = "array"
        self._values.h["sourceFormat"] = com_sdtk_table_Format.ARRAY
        return com_sdtk_table_ConverterInputOperationsOptions(self._values)

    def setSource(self,value,sourceType):
        self._values.h["source"] = value
        self._values.h["sourceType"] = sourceType
        return com_sdtk_table_ConverterInputFormatOptions(self._values)


class com_sdtk_table_ConverterOutputFormatOptions:

    def __init__(self,values = None):
        if (values is None):
            values = haxe_ds_StringMap()
        self._values = values

    def tex(self):
        return self.setTargetFormatDelimited(com_sdtk_table_Format.TEX)

    def raw(self):
        return self.setTargetFormatDelimited(com_sdtk_table_Format.RAW)

    def csv(self):
        return self.setTargetFormatDelimited(com_sdtk_table_Format.CSV)

    def psv(self):
        return self.setTargetFormatDelimited(com_sdtk_table_Format.PSV)

    def tsv(self):
        return self.setTargetFormatDelimited(com_sdtk_table_Format.TSV)

    def htmlTable(self):
        return self.setTargetFormat(com_sdtk_table_Format.HTMLTable)

    def dir(self):
        return self.setTargetFormat(com_sdtk_table_Format.DIR)

    def ini(self):
        return self.setTargetFormat(com_sdtk_table_Format.INI)

    def json(self):
        return self.setTargetFormat(com_sdtk_table_Format.JSON)

    def properties(self):
        return self.setTargetFormat(com_sdtk_table_Format.PROPERTIES)

    def splunk(self):
        return self.setTargetFormat(com_sdtk_table_Format.SPLUNK)

    def sql(self):
        self._values.h["targetFormat"] = com_sdtk_table_Format.SQL
        return com_sdtk_table_ConverterOutputOperationsOptionsSQL(self._values)

    def csharp(self):
        return self.setTargetFormat(com_sdtk_table_Format.CSharp)

    def java(self):
        return self.setTargetFormat(com_sdtk_table_Format.Java)

    def haxe(self):
        return self.setTargetFormat(com_sdtk_table_Format.Haxe)

    def python(self):
        return self.setTargetFormat(com_sdtk_table_Format.Python)

    def setTargetFormat(self,value):
        self._values.h["targetFormat"] = value
        return com_sdtk_table_ConverterOutputOperationsOptions(self._values)

    def setTargetFormatDelimited(self,value):
        self._values.h["targetFormat"] = value
        return com_sdtk_table_ConverterOutputOperationsOptionsDelimited(self._values)


class com_sdtk_table_ConverterOutputOperationsOptions:

    def __init__(self,values = None):
        if (values is None):
            values = haxe_ds_StringMap()
        self._values = values

    def sortRowsBy(self,value):
        return self.mergeSortBy("sortRowsBy",value)

    def mergeSortBy(self,key,value):
        current = self._values.h.get(key,None)
        if (current is None):
            current = list()
        current.append(value)
        self._values.h[key] = current
        return self

    def execute(self,callback = None):
        result = None
        eTarget = None
        if ((self._values.h.get("targetType",None) == "element") and ((self._values.h.get("targetFormat",None) != com_sdtk_table_Format.HTMLTable))):
            eTarget = self._values.h.get("target",None)
            this1 = self._values
            value = StringBuf()
            this1.h["target"] = value
            self._values.h["targetType"] = "string"
        com_sdtk_table_Converter.convertWithOptions(self._values.h.get("source",None),self._values.h.get("sourceFormat",None),self._values.h.get("target",None),self._values.h.get("targetFormat",None),self._values.h.get("filterColumnsExclude",None),self._values.h.get("filterColumnsInclude",None),self._values.h.get("filterRowsExclude",None),self._values.h.get("filterRowsInclude",None),self._values.h.get("sortRowsBy",None),False,False,self._values.h.get("inputOptions",None),self._values.h.get("outputOptions",None))
        _g = self._values.h.get("targetType",None)
        if (_g == "array"):
            result = self._values.h.get("target",None)
        elif (_g == "string"):
            sb = self._values.h.get("target",None)
            result = sb.b.getvalue()
        else:
            pass
        if (eTarget is not None):
            result = None
        if (callback is None):
            return result
        else:
            callback(result)
            return None


class com_sdtk_table_ConverterOutputOperationsOptionsSQL(com_sdtk_table_ConverterOutputOperationsOptions):

    def __init__(self,values = None):
        super().__init__(values)

    def createTable(self,name):
        return self.setValue("Create",name)

    def createOrReplaceTable(self,name):
        return self.setValue("CreateOrReplace",name)

    def insertIntoTable(self,name):
        return self.setValue("Insert",name)

    def setValue(self,sqlType,tableName):
        options = self._values.h.get("outputOptions",None)
        if (options is None):
            options = haxe_ds_StringMap()
            self._values.h["outputOptions"] = options
        options.h["sqlType"] = sqlType
        options.h["tableName"] = tableName
        return com_sdtk_table_ConverterOutputOperationsOptions(self._values)


class com_sdtk_table_ConverterOutputOperationsOptionsDelimited(com_sdtk_table_ConverterOutputOperationsOptions):

    def __init__(self,values = None):
        super().__init__(values)

    def excludeHeader(self,value = None):
        if (value is None):
            value = True
        return self.setValue("header",(not value))

    def textOnly(self,value = None):
        if (value is None):
            value = True
        return self.setValue("textOnly",(not value))

    def setValue(self,key,value):
        options = self._values.h.get("outputOptions",None)
        if (options is None):
            options = haxe_ds_StringMap()
            self._values.h["outputOptions"] = options
        options.h[key] = value
        return self


class com_sdtk_table_ConverterOutputOptions:

    def __init__(self,values = None):
        if (values is None):
            values = haxe_ds_StringMap()
        self._values = values

    def writeFile(self,file):
        return self.setTarget(file,"file")

    def writeElement(self,e):
        return self.setTarget(e,"element")

    def writeString(self):
        return self.setTarget(StringBuf(),"string")

    def writeArrayOfArrays(self):
        this1 = self._values
        value = list()
        this1.h["target"] = value
        self._values.h["targetType"] = "array"
        self._values.h["targetFormat"] = com_sdtk_table_Format.ARRAY
        return com_sdtk_table_ConverterOutputOperationsOptions(self._values)

    def setTarget(self,value,targetType):
        self._values.h["target"] = value
        self._values.h["targetType"] = targetType
        return com_sdtk_table_ConverterOutputFormatOptions(self._values)


class com_sdtk_table_ConverterQuickInputOptions:

    def __init__(self):
        pass

    def raw(self,value):
        return self.next(self.read(value).raw())

    def csv(self,value):
        return self.next(self.read(value).csv())

    def psv(self,value):
        return self.next(self.read(value).psv())

    def tsv(self,value):
        return self.next(self.read(value).tsv())

    def htmlTable(self,value):
        return self.next(self.read(value).htmlTable())

    def dir(self,value):
        return self.next(self.read(value).dir())

    def ini(self,value):
        return self.next(self.read(value).ini())

    def json(self,value):
        return self.next(self.read(value).json())

    def properties(self,value):
        return self.next(self.read(value).properties())

    def splunk(self,value):
        return self.next(self.read(value).splunk())

    def readDatabase(self,value):
        return self.next(com_sdtk_table_Converter.start().readDatabase(value))

    def readArrayOfArrays(self,value):
        return self.next(com_sdtk_table_Converter.start().readArrayOfArrays(value))

    def read(self,value):
        return com_sdtk_table_Converter.start().readString(value)

    def next(self,value):
        return com_sdtk_table_ConverterQuickOutputOptions(value.output())


class com_sdtk_table_ConverterQuickOutputOptions:

    def __init__(self,values):
        self._values = values

    def tex(self,callback = None):
        return self._values.writeString().tex().execute(callback)

    def raw(self,callback = None):
        return self._values.writeString().raw().execute(callback)

    def csv(self,callback = None):
        return self._values.writeString().csv().execute(callback)

    def psv(self,callback = None):
        return self._values.writeString().psv().execute(callback)

    def tsv(self,callback = None):
        return self._values.writeString().tsv().execute(callback)

    def htmlTable(self,callback = None):
        return self._values.writeString().htmlTable().execute(callback)

    def dir(self,callback = None):
        return self._values.writeString().dir().execute(callback)

    def ini(self,callback = None):
        return self._values.writeString().ini().execute(callback)

    def json(self,callback = None):
        return self._values.writeString().json().execute(callback)

    def properties(self,callback = None):
        return self._values.writeString().properties().execute(callback)

    def splunk(self,callback = None):
        return self._values.writeString().splunk().execute(callback)

    def sql(self,callback = None):
        return self._values.writeString().sql().execute(callback)

    def csharp(self,callback = None):
        return self._values.writeString().csharp().execute(callback)

    def java(self,callback = None):
        return self._values.writeString().java().execute(callback)

    def haxe(self,callback = None):
        return self._values.writeString().haxe().execute(callback)

    def python(self,callback = None):
        return self._values.writeString().python().execute(callback)

    def writeArrayOfArrays(self,callback = None):
        return self._values.writeArrayOfArrays().execute(callback)


class com_sdtk_table_ConverterStage:
    pass


class com_sdtk_table_ConverterStageSort:

    def __init__(self):
        self._names = None
        self._reverse = None
        self._columns = None
        self._array = None

    def setArray(self,aArray):
        self._array = aArray

    def addColumn(self,iColumn,bReverse):
        if (self._columns is None):
            self._columns = list()
            self._reverse = list()
        _this = self._columns
        _this.append(iColumn)
        _this = self._reverse
        _this.append(bReverse)

    def addColumnName(self,sColumn,bReverse):
        if (self._names is None):
            self._names = list()
            self._reverse = list()
        _this = self._names
        _this.append(sColumn)
        _this = self._reverse
        _this.append(bReverse)

    def findNames(self):
        oFirstRow = (self._array[0] if 0 < len(self._array) else None)
        self._columns = list()
        if (len(self._names) == 1):
            _g = 0
            _g1 = self._names
            while (_g < len(_g1)):
                sName = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self._columns
                x = python_internal_ArrayImpl.indexOf(oFirstRow,sName,None)
                _this.append(x)
        else:
            i = 0
            mFirstRow = haxe_ds_StringMap()
            _g = 0
            while (_g < len(oFirstRow)):
                o = (oFirstRow[_g] if _g >= 0 and _g < len(oFirstRow) else None)
                _g = (_g + 1)
                value = i
                i = (i + 1)
                mFirstRow.h[o] = value
            _g = 0
            _g1 = self._names
            while (_g < len(_g1)):
                sName = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                _this = self._columns
                x = mFirstRow.h.get(sName,None)
                _this.append(x)

    def convert(self):
        _gthis = self
        com_sdtk_table_ConverterStageSort._watch.start()
        oFirstRow = None
        if ((self._columns is None) and ((self._names is not None))):
            self.findNames()
            oFirstRow = (self._array[0] if 0 < len(self._array) else None)
        def _hx_local_2(a,b):
            if (a is oFirstRow):
                return -1
            elif (b is oFirstRow):
                return 1
            i = 0
            _g = 0
            _g1 = _gthis._columns
            while (_g < len(_g1)):
                iColumn = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                _g = (_g + 1)
                bReverse = (_gthis._reverse[i] if i >= 0 and i < len(_gthis._reverse) else None)
                columnA = Std.string((a[iColumn] if iColumn >= 0 and iColumn < len(a) else None))
                columnB = Std.string((b[iColumn] if iColumn >= 0 and iColumn < len(b) else None))
                _g2 = (-1 if ((columnA < columnB)) else (1 if ((columnA > columnB)) else 0))
                if (_g2 == -1):
                    if bReverse:
                        return 1
                    else:
                        return -1
                elif (_g2 == 1):
                    if bReverse:
                        return -1
                    else:
                        return 1
                else:
                    pass
                i = (i + 1)
            return 0
        self._array.sort(key= python_lib_Functools.cmp_to_key(_hx_local_2))
        com_sdtk_table_ConverterStageSort._watch.end()

    def dispose(self):
        if (self._array is not None):
            self._array = None
            self._columns = None
            self._reverse = None
            self._names = None

    @staticmethod
    def createWithArrayAndColumns(aArray,sColumns):
        stage = com_sdtk_table_ConverterStageSort()
        stage.setArray(aArray)
        _g = 0
        while (_g < len(sColumns)):
            sColumn = (sColumns[_g] if _g >= 0 and _g < len(sColumns) else None)
            _g = (_g + 1)
            stage.addColumnName(sColumn,False)
        return stage

    @staticmethod
    def createWithArrayAndColumnsString(aArray,sColumns):
        return com_sdtk_table_ConverterStageSort.createWithArrayAndColumns(aArray,sColumns.split(","))


class com_sdtk_table_ConverterStageStandard:

    def __init__(self,oSource,fSource,oTarget,fTarget,sFilterColumnsExclude,sFilterColumnsInclude,sFilterRowsExclude,sFilterRowsInclude,leftTrim,rightTrim,inputOptions,outputOptions):
        self._reader = None
        self._writer = None
        self._writer = com_sdtk_table_ConverterStageStandard.createWriter(oTarget,fTarget,outputOptions)
        self._reader = com_sdtk_table_ConverterStageStandard.createReader(oSource,fSource,sFilterColumnsExclude,sFilterColumnsInclude,sFilterRowsExclude,sFilterRowsInclude,leftTrim,rightTrim,inputOptions)

    def convert(self):
        self._reader.convertTo(self._writer)

    def dispose(self):
        if (self._writer is not None):
            self._writer.dispose()
            self._writer = None
            self._reader.dispose()
            self._reader = None

    @staticmethod
    def isString(o):
        return Std.isOfType(o,str)

    @staticmethod
    def isInt(o):
        return Std.isOfType(o,Int)

    @staticmethod
    def mergeFilters(a,b):
        if ((((a is None) or ((len(a) <= 0)))) and (((b is None) or ((len(b) <= 0))))):
            return None
        else:
            mergedA = None
            mergedB = None
            if ((a is None) or ((len(a) <= 0))):
                mergedA = None
            else:
                _hx_filter = None
                _g = 0
                while (_g < len(a)):
                    f = (a[_g] if _g >= 0 and _g < len(a) else None)
                    _g = (_g + 1)
                    if (_hx_filter is None):
                        _hx_filter = f
                    else:
                        _hx_filter = _hx_filter._hx_or(f)
                mergedA = _hx_filter
            if ((b is None) or ((len(b) <= 0))):
                mergedB = None
            else:
                _hx_filter = None
                _g = 0
                while (_g < len(a)):
                    f = (a[_g] if _g >= 0 and _g < len(a) else None)
                    _g = (_g + 1)
                    if (_hx_filter is None):
                        _hx_filter = f
                    else:
                        _hx_filter = _hx_filter._hx_and(f)
                mergedB = _hx_filter
            if ((mergedA is not None) and ((mergedB is not None))):
                return mergedA._hx_and(mergedB)
            elif (mergedA is not None):
                return mergedA
            else:
                return mergedB

    @staticmethod
    def getOption(options,key,_hx_def = None):
        if (options is None):
            return _hx_def
        else:
            value = options.h.get(key,None)
            if (value is None):
                return _hx_def
            else:
                return value

    @staticmethod
    def createWriter(oTarget,fTarget,outputOptions):
        writer = None
        if (oTarget is not None):
            if Std.isOfType(oTarget,com_sdtk_table_DataTableWriter):
                writer = oTarget
            if (writer is None):
                sTarget = None
                if (oTarget == Std.string(oTarget)):
                    sTarget = "STRING"
                else:
                    sTarget = Type.getClassName(Type.getClass(oTarget)).upper()
                sTarget1 = sTarget
                _hx_local_0 = len(sTarget1)
                if (_hx_local_0 == 9):
                    if (sTarget1 == "STRINGBUF"):
                        oTarget = com_sdtk_std_StringWriter(oTarget)
                elif (_hx_local_0 == 5):
                    if (sTarget1 == "ARRAY"):
                        if (fTarget is None):
                            fTarget = com_sdtk_table_Format.ARRAY
                elif (_hx_local_0 == 6):
                    if (sTarget1 == "STRING"):
                        def _hx_local_2():
                            _hx_local_1 = oTarget
                            if (Std.isOfType(_hx_local_1,str) or ((_hx_local_1 is None))):
                                _hx_local_1
                            else:
                                raise "Class cast error"
                            return _hx_local_1
                        sString = _hx_local_2()
                        _g = ("" if ((0 >= len(sString))) else sString[0])
                        if ((_g == ".") or ((_g == "#"))):
                            oTarget = com_sdtk_table_ConverterStageStandard.getControl(oTarget)
                        else:
                            oTarget = com_sdtk_std_FileWriter(sString,False).convertToStringWriter().switchToDroppingCharacters()
                else:
                    pass
                if (fTarget is None):
                    if (com_sdtk_table_ConverterStageStandard.getControlType(oTarget) == 1):
                        fTarget = com_sdtk_table_Format.CSV
                diTarget = None
                ciTarget = None
                tiTarget = None
                fshTarget = None
                kvhTarget = None
                if (fTarget is not None):
                    tmp = fTarget.index
                    if (tmp == 0):
                        diTarget = com_sdtk_table_CSVInfo.instance
                    elif (tmp == 1):
                        diTarget = com_sdtk_table_PSVInfo.instance
                    elif (tmp == 2):
                        diTarget = com_sdtk_table_TSVInfo.instance
                    elif (tmp == 3):
                        fshTarget = com_sdtk_table_CMDDirHandler.instance
                        writer = com_sdtk_table_FileSystemWriter.createCMDDirWriter(oTarget)
                    elif (tmp == 4):
                        kvhTarget = com_sdtk_table_INIHandler.instance
                        writer = com_sdtk_table_KeyValueWriter.createINIWriter(oTarget)
                    elif (tmp == 5):
                        kvhTarget = com_sdtk_table_JSONHandler.instance
                        writer = com_sdtk_table_KeyValueWriter.createJSONWriter(oTarget)
                    elif (tmp == 6):
                        kvhTarget = com_sdtk_table_PropertiesHandler.instance
                        writer = com_sdtk_table_KeyValueWriter.createPropertiesWriter(oTarget)
                    elif (tmp == 7):
                        sqlType = com_sdtk_table_ConverterStageStandard.getOption(outputOptions,"sqlType")
                        if (sqlType is not None):
                            tableName = com_sdtk_table_ConverterStageStandard.getOption(outputOptions,"tableName")
                            sqlType1 = sqlType
                            _hx_local_3 = len(sqlType1)
                            if (_hx_local_3 == 15):
                                if (sqlType1 == "CreateOrReplace"):
                                    ciTarget = com_sdtk_table_SQLSelectInfo.createOrReplaceTable(tableName)
                                else:
                                    ciTarget = com_sdtk_table_SQLSelectInfo.instance
                            elif (_hx_local_3 == 6):
                                if (sqlType1 == "Create"):
                                    ciTarget = com_sdtk_table_SQLSelectInfo.createTable(tableName)
                                elif (sqlType1 == "Insert"):
                                    ciTarget = com_sdtk_table_SQLSelectInfo.insertIntoTable(tableName)
                                else:
                                    ciTarget = com_sdtk_table_SQLSelectInfo.instance
                            else:
                                ciTarget = com_sdtk_table_SQLSelectInfo.instance
                        else:
                            ciTarget = com_sdtk_table_SQLSelectInfo.instance
                    elif (tmp == 8):
                        ciTarget = com_sdtk_table_HaxeInfoArrayOfMaps.instance
                    elif (tmp == 9):
                        ciTarget = com_sdtk_table_PythonInfoArrayOfMaps.instance
                    elif (tmp == 10):
                        ciTarget = com_sdtk_table_JavaInfoArrayOfMaps.instance
                    elif (tmp == 11):
                        ciTarget = com_sdtk_table_CSharpInfoArrayOfMaps.instance
                    elif (tmp == 12):
                        kvhTarget = com_sdtk_table_SplunkHandler.instance
                        writer = com_sdtk_table_KeyValueWriter.createSplunkWriter(oTarget)
                    elif (tmp == 13):
                        tiTarget = com_sdtk_table_StandardTableInfo.instance
                        if Std.isOfType(oTarget,com_sdtk_std_Writer):
                            writer = com_sdtk_table_TableWriter.createStandardTableWriterForWriter(oTarget)
                        else:
                            writer = com_sdtk_table_TableWriter.createStandardTableWriterForElement(oTarget)
                    elif (tmp == 14):
                        writer = com_sdtk_table_Array2DWriter.writeToExpandableArrayI(oTarget)
                    elif (tmp == 18):
                        pass
                    elif (tmp == 19):
                        diTarget = com_sdtk_table_RAWInfo.instance
                    elif (tmp == 20):
                        diTarget = com_sdtk_table_TeXInfo.instance
                    else:
                        pass
                if (diTarget is not None):
                    dwWriter = com_sdtk_table_DelimitedWriter(diTarget,oTarget)
                    writer = dwWriter
                    if com_sdtk_table_ConverterStageStandard.getOption(outputOptions,"header",True):
                        dwWriter.noHeaderIncluded(False)
                    else:
                        dwWriter.noHeaderIncluded(True)
                elif (ciTarget is not None):
                    writer = com_sdtk_table_CodeWriter(ciTarget,oTarget)
        return writer

    @staticmethod
    def createReader(oSource,fSource,sFilterColumnsExclude,sFilterColumnsInclude,sFilterRowsExclude,sFilterRowsInclude,leftTrim,rightTrim,inputOptions):
        reader = None
        if (oSource is not None):
            if Std.isOfType(oSource,com_sdtk_table_DataTableReader):
                reader = oSource
            if (reader is None):
                sSource = None
                if (oSource == Std.string(oSource)):
                    sSource = "STRING"
                else:
                    sSource = Type.getClassName(Type.getClass(oSource)).upper()
                if (sSource == "STRINGBUF"):
                    sb = oSource
                    oSource = sb.b.getvalue()
                    sSource = "STRING"
                sSource1 = sSource
                _hx_local_0 = len(sSource1)
                if (_hx_local_0 == 5):
                    if (sSource1 == "ARRAY"):
                        if (fSource is None):
                            fSource = com_sdtk_table_Format.ARRAY
                elif (_hx_local_0 == 6):
                    if (sSource1 == "STRING"):
                        def _hx_local_2():
                            _hx_local_1 = oSource
                            if (Std.isOfType(_hx_local_1,str) or ((_hx_local_1 is None))):
                                _hx_local_1
                            else:
                                raise "Class cast error"
                            return _hx_local_1
                        sString = _hx_local_2()
                        _g = ("" if ((0 >= len(sString))) else sString[0])
                        if ((_g == ".") or ((_g == "#"))):
                            oSource = com_sdtk_table_ConverterStageStandard.getControl(oSource)
                        else:
                            tmp = None
                            tmp1 = None
                            tmp2 = None
                            startIndex = None
                            if (((sString.find("\n") if ((startIndex is None)) else HxString.indexOfImpl(sString,"\n",startIndex))) < 0):
                                startIndex = None
                                tmp2 = (((sString.find("\t") if ((startIndex is None)) else HxString.indexOfImpl(sString,"\t",startIndex))) >= 0)
                            else:
                                tmp2 = True
                            if (not tmp2):
                                startIndex = None
                                tmp1 = (((sString.find(",") if ((startIndex is None)) else HxString.indexOfImpl(sString,",",startIndex))) >= 0)
                            else:
                                tmp1 = True
                            if (not tmp1):
                                startIndex = None
                                tmp = (((sString.find("|") if ((startIndex is None)) else HxString.indexOfImpl(sString,"|",startIndex))) >= 0)
                            else:
                                tmp = True
                            if tmp:
                                oSource = com_sdtk_std_StringReader(sString)
                            else:
                                oSource = com_sdtk_std_FileReader(sString).convertToStringReader().switchToDroppingCharacters()
                else:
                    pass
                if (fSource is None):
                    if (com_sdtk_table_ConverterStageStandard.getControlType(oSource) == 0):
                        fSource = com_sdtk_table_Format.HTMLTable
                diSource = None
                ciSource = None
                tiSource = None
                fshSource = None
                kvhSource = None
                if (fSource is not None):
                    tmp = fSource.index
                    if (tmp == 0):
                        diSource = com_sdtk_table_CSVInfo.instance
                    elif (tmp == 1):
                        diSource = com_sdtk_table_PSVInfo.instance
                    elif (tmp == 2):
                        diSource = com_sdtk_table_TSVInfo.instance
                    elif (tmp == 3):
                        fshSource = com_sdtk_table_CMDDirHandler.instance
                        reader = com_sdtk_table_FileSystemReader.createCMDDirReader(oSource)
                    elif (tmp == 4):
                        kvhSource = com_sdtk_table_INIHandler.instance
                        reader = com_sdtk_table_KeyValueReader.createINIReader(oSource)
                    elif (tmp == 5):
                        kvhSource = com_sdtk_table_JSONHandler.instance
                        reader = com_sdtk_table_KeyValueReader.createJSONReader(oSource)
                    elif (tmp == 6):
                        kvhSource = com_sdtk_table_PropertiesHandler.instance
                        reader = com_sdtk_table_KeyValueReader.createPropertiesReader(oSource)
                    elif (tmp == 7):
                        ciSource = com_sdtk_table_SQLSelectInfo.instance
                    elif (tmp == 8):
                        ciSource = com_sdtk_table_HaxeInfoArrayOfMaps.instance
                    elif (tmp == 9):
                        ciSource = com_sdtk_table_PythonInfoArrayOfMaps.instance
                    elif (tmp == 10):
                        ciSource = com_sdtk_table_JavaInfoArrayOfMaps.instance
                    elif (tmp == 11):
                        ciSource = com_sdtk_table_CSharpInfoArrayOfMaps.instance
                    elif (tmp == 12):
                        kvhSource = com_sdtk_table_SplunkHandler.instance
                        reader = com_sdtk_table_KeyValueReader.createSplunkReader(oSource)
                    elif (tmp == 13):
                        tiSource = com_sdtk_table_StandardTableInfo.instance
                        reader = com_sdtk_table_TableReader.createStandardTableReader(oSource)
                    elif (tmp == 14):
                        reader = com_sdtk_table_Array2DReader.readWholeArrayI(oSource)
                    elif (tmp == 18):
                        reader = com_sdtk_table_DatabaseReader.read(oSource)
                    elif (tmp == 19):
                        diSource = com_sdtk_table_RAWInfo.instance
                    else:
                        pass
                if (diSource is not None):
                    drReader = com_sdtk_table_DelimitedReader(diSource,oSource)
                    reader = drReader
                    if com_sdtk_table_ConverterStageStandard.getOption(inputOptions,"header",True):
                        drReader.noHeaderIncluded(False)
                    else:
                        drReader.noHeaderIncluded(True)
                    if com_sdtk_table_ConverterStageStandard.getOption(inputOptions,"textOnly",False):
                        drReader.alwaysString(True)
                    else:
                        drReader.alwaysString(False)
                else:
                    tmp = (ciSource is not None)
                if (leftTrim and rightTrim):
                    reader = com_sdtk_table_DataTableReaderTrim(reader)
                elif leftTrim:
                    reader = com_sdtk_table_DataTableReaderLeftTrim(reader)
                elif rightTrim:
                    reader = com_sdtk_table_DataTableReaderRightTrim(reader)
                if ((sFilterRowsInclude is not None) or ((sFilterRowsExclude is not None))):
                    fFilter = None
                    if (com_sdtk_table_ConverterStageStandard.isString(sFilterRowsInclude) or com_sdtk_table_ConverterStageStandard.isString(sFilterRowsExclude)):
                        if ((sFilterRowsInclude is not None) and ((sFilterRowsExclude is not None))):
                            fFilter = com_sdtk_std_Filter.parse(sFilterRowsInclude,False)
                            fFilter._hx_and(com_sdtk_std_Filter.parse(sFilterRowsExclude,True))
                        elif (sFilterRowsInclude is not None):
                            fFilter = com_sdtk_std_Filter.parse(sFilterRowsInclude,False)
                        else:
                            fFilter = com_sdtk_std_Filter.parse(sFilterRowsExclude,True)
                    else:
                        fFilter = com_sdtk_table_ConverterStageStandard.mergeFilters(sFilterRowsInclude,sFilterRowsExclude)
                    reader = com_sdtk_table_RowFilterDataTableReader(reader,fFilter)
            if ((sFilterColumnsInclude is not None) or ((sFilterColumnsExclude is not None))):
                fFilter = None
                if (com_sdtk_table_ConverterStageStandard.isString(sFilterColumnsInclude) or com_sdtk_table_ConverterStageStandard.isString(sFilterColumnsExclude)):
                    if ((sFilterColumnsInclude is not None) and ((sFilterColumnsExclude is not None))):
                        fFilter = com_sdtk_std_Filter.parse(sFilterColumnsInclude,False)
                        fFilter._hx_and(com_sdtk_std_Filter.parse(sFilterColumnsExclude,True))
                    elif (sFilterColumnsInclude is not None):
                        fFilter = com_sdtk_std_Filter.parse(sFilterColumnsInclude,False)
                    else:
                        fFilter = com_sdtk_std_Filter.parse(sFilterColumnsExclude,True)
                else:
                    if ((sFilterColumnsInclude is not None) and ((Reflect.field(sFilterColumnsInclude,"length") > 0))):
                        if (com_sdtk_table_ConverterStageStandard.isString(HxOverrides.arrayGet(sFilterColumnsInclude, 0)) or com_sdtk_table_ConverterStageStandard.isInt(HxOverrides.arrayGet(sFilterColumnsInclude, 0))):
                            fFilters = list()
                            sFilters = sFilterColumnsInclude
                            _g = 0
                            while (_g < len(sFilters)):
                                sFilter = (sFilters[_g] if _g >= 0 and _g < len(sFilters) else None)
                                _g = (_g + 1)
                                fFilter1 = com_sdtk_std_Filter.parse(sFilter,False)
                                fFilters.append(fFilter1)
                            sFilterColumnsInclude = fFilters
                    if ((sFilterColumnsExclude is not None) and ((Reflect.field(sFilterColumnsExclude,"length") > 0))):
                        if (com_sdtk_table_ConverterStageStandard.isString(HxOverrides.arrayGet(sFilterColumnsExclude, 0)) or com_sdtk_table_ConverterStageStandard.isInt(HxOverrides.arrayGet(sFilterColumnsExclude, 0))):
                            fFilters = list()
                            sFilters = sFilterColumnsExclude
                            _g = 0
                            while (_g < len(sFilters)):
                                sFilter = (sFilters[_g] if _g >= 0 and _g < len(sFilters) else None)
                                _g = (_g + 1)
                                fFilter1 = com_sdtk_std_Filter.parse(sFilter,True)
                                fFilters.append(fFilter1)
                    fFilter = com_sdtk_table_ConverterStageStandard.mergeFilters(sFilterColumnsInclude,sFilterColumnsExclude)
                reader = com_sdtk_table_ColumnFilterDataTableReader(reader,fFilter)
        return reader

    @staticmethod
    def getControl(sName):
        return None

    @staticmethod
    def getControlType(oControl):
        sTag = None
        if (sTag is None):
            return -1
        else:
            sTag1 = sTag
            _hx_local_0 = len(sTag1)
            if (_hx_local_0 == 4):
                if (sTag1 == "BODY"):
                    return 1
                elif (sTag1 == "HEAD"):
                    return 1
                elif (sTag1 == "HTML"):
                    return 1
                else:
                    return -1
            elif (_hx_local_0 == 5):
                if (sTag1 == "TABLE"):
                    return 0
                else:
                    return -1
            elif (_hx_local_0 == 3):
                if (sTag1 == "DIV"):
                    return 1
                else:
                    return -1
            elif (_hx_local_0 == 8):
                if (sTag1 == "DOCUMENT"):
                    return 1
                else:
                    return -1
            else:
                return -1


class com_sdtk_table_DataEntryReaderDecorator(com_sdtk_table_DataEntryReader):

    def __init__(self,reader):
        self._reader = None
        super().__init__()
        self._reader = reader

    def hasNext(self):
        return self._reader.hasNext()

    def next(self):
        return self._reader.next()

    def iterator(self):
        return self

    def name(self):
        return self._reader.name()

    def index(self):
        return self._reader.index()

    def value(self):
        return self._reader.value()

    def isAutoNamed(self):
        return self._reader.isAutoNamed()

    def isNameIndex(self):
        return self._reader.isNameIndex()

    def start(self):
        self._reader.start()

    def dispose(self):
        self._reader.dispose()


class com_sdtk_table_DataTableReaderIterable:

    def __init__(self,shared,f):
        self._shared = shared
        self._f = f

    def iterator(self):
        return com_sdtk_table_DataTableReaderIterator(self._shared,self._f)


class com_sdtk_table_DataTableReaderIterator:

    def __init__(self,shared,f):
        self._row = 0
        self._shared = shared
        self._f = f

    def hasNext(self):
        return False

    def next(self):
        self._shared.moveTo((self._row + 1))
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._row
        _hx_local_0._row = (_hx_local_1 + 1)
        _hx_local_1
        return self._f()


class com_sdtk_table_DataTableReaderSharedIterator:

    def __init__(self,reader):
        self._dataByName = None
        self._dataByIndex = None
        self._row = 0
        self._reader = reader

    def moveTo(self,row = None):
        if (row != self._row):
            self._reader.moveTo(row)


class com_sdtk_table_DataTableReaderDecorator(com_sdtk_table_DataTableReader):

    def __init__(self,reader):
        self._reader = None
        super().__init__()
        self._reader = reader

    def hasNext(self):
        return self._reader.hasNext()

    def nextReuse(self,rowReader):
        return self._reader.nextReuse(rowReader)

    def next(self):
        return self._reader.next()

    def iterator(self):
        return self

    def name(self):
        return self._reader.name()

    def index(self):
        return self._reader.index()

    def value(self):
        return self._reader.value()

    def isAutoNamed(self):
        return self._reader.isAutoNamed()

    def isNameIndex(self):
        return self._reader.isNameIndex()

    def start(self):
        self._reader.start()

    def alwaysString(self,value = None):
        self._reader.alwaysString(value)
        return super().alwaysString(value)

    def dispose(self):
        self._reader.dispose()

    def headerRowNotIncluded(self):
        return self._reader.headerRowNotIncluded()

    def oneRowPerFile(self):
        return self._reader.oneRowPerFile()

    def reset(self):
        self._reader.reset()


class com_sdtk_table_DataTableReaderTrimAbstract(com_sdtk_table_DataTableReaderDecorator):

    def __init__(self,reader):
        super().__init__(reader)

    def rowReaderInstance(self,reader):
        return None

    def nextReuse(self,rowReader):
        if (rowReader is None):
            rowReader = self.rowReaderInstance(self._reader.next())
        else:
            rr = rowReader
            rr.reuse(rr.reader())
        return rowReader

    def next(self):
        return self.nextReuse(None)

    def value(self):
        return self._value


class com_sdtk_table_DataTableReaderLeftTrim(com_sdtk_table_DataTableReaderTrimAbstract):

    def __init__(self,reader):
        super().__init__(reader)

    def rowReaderInstance(self,reader):
        return com_sdtk_table_DataTableRowReaderLeftTrim(reader)


class com_sdtk_table_DataTableRowReaderDecorator(com_sdtk_table_DataTableRowReader):

    def __init__(self,reader):
        self._reader = None
        super().__init__()
        self.reuse(reader)

    def reuse(self,reader):
        self._reader = reader
        self._index = -1
        self._started = False
        self._value = None

    def reader(self):
        return self._reader

    def hasNext(self):
        return self._reader.hasNext()

    def next(self):
        return self._reader.next()

    def iterator(self):
        return self

    def name(self):
        return self._reader.name()

    def index(self):
        return self._reader.index()

    def value(self):
        return self._reader.value()

    def isAutoNamed(self):
        return self._reader.isAutoNamed()

    def isNameIndex(self):
        return self._reader.isNameIndex()

    def start(self):
        self._reader.start()

    def alwaysString(self,value = None):
        self._reader.alwaysString(value)
        return super().alwaysString(value)

    def dispose(self):
        self._reader.dispose()


class com_sdtk_table_DataTableRowReaderTrimAbstract(com_sdtk_table_DataTableRowReaderDecorator):

    def __init__(self,reader):
        super().__init__(reader)

    def trimI(self,value):
        return None

    def trim(self,value):
        if Std.isOfType(value,str):
            return self.trimI(Std.string(value))
        else:
            return value

    def next(self):
        self._value = self.trim(self._reader.next())
        return self._value

    def value(self):
        return self._value


class com_sdtk_table_DataTableRowReaderLeftTrim(com_sdtk_table_DataTableRowReaderTrimAbstract):

    def __init__(self,reader):
        super().__init__(reader)

    def trimI(self,value):
        return StringTools.ltrim(value)


class com_sdtk_table_DataTableReaderRightTrim(com_sdtk_table_DataTableReaderTrimAbstract):

    def __init__(self,reader):
        super().__init__(reader)

    def rowReaderInstance(self,reader):
        return com_sdtk_table_DataTableRowReaderRightTrim(reader)


class com_sdtk_table_DataTableRowReaderRightTrim(com_sdtk_table_DataTableRowReaderTrimAbstract):

    def __init__(self,reader):
        super().__init__(reader)

    def trimI(self,value):
        return StringTools.rtrim(value)


class com_sdtk_table_DataTableReaderTrim(com_sdtk_table_DataTableReaderTrimAbstract):

    def __init__(self,reader):
        super().__init__(reader)

    def rowReaderInstance(self,reader):
        return com_sdtk_table_DataTableRowReaderTrim(reader)


class com_sdtk_table_DataTableRowReaderTrim(com_sdtk_table_DataTableRowReaderTrimAbstract):

    def __init__(self,reader):
        super().__init__(reader)

    def trimI(self,value):
        return StringTools.trim(value)


class com_sdtk_table_DatabaseReader(com_sdtk_table_DataTableReader):

    def __init__(self):
        self._done = False
        super().__init__()

    def reset(self):
        pass

    @staticmethod
    def initMappings():
        if (com_sdtk_table_DatabaseReader._mappings is None):
            com_sdtk_table_DatabaseReader._mappings = list()
            _this = com_sdtk_table_DatabaseReader._mappings
            _this.append("execute")
            _this = com_sdtk_table_DatabaseReader._mappings
            _this.append("__iter__")
            _this = com_sdtk_table_DatabaseReader._mappings
            _this.append("iterator")
            com_sdtk_table_DatabaseReader._finalMappings = haxe_ds_StringMap()
            com_sdtk_table_DatabaseReader._finalMappings.h["next"] = com_sdtk_table_DatabaseReader.dbIterator
            com_sdtk_table_DatabaseReader._finalMappings.h["__next__"] = com_sdtk_table_DatabaseReader.dbIterator
            com_sdtk_table_DatabaseReader._finalMappings.h["fetch"] = com_sdtk_table_DatabaseReader.dbIterator
            com_sdtk_table_DatabaseReader._columnMappings = haxe_ds_StringMap()
            com_sdtk_table_DatabaseReader._columnMappings.h["__iter__-description"] = com_sdtk_table_DatabaseReader.columnDescription
            com_sdtk_table_DatabaseReader._columnMappings.h["execute-getColumnName"] = com_sdtk_table_DatabaseReader.columnGetColumnName
            com_sdtk_table_DatabaseReader._retrievalTypes = haxe_ds_StringMap()
            com_sdtk_table_DatabaseReader._retrievalTypes.h[""] = com_sdtk_table_DatabaseReader.getArrayValue
            com_sdtk_table_DatabaseReader._retrievalTypes.h["getColumnValue"] = com_sdtk_table_DatabaseReader.getColumnValue
            com_sdtk_table_DatabaseReader._retrievalPrepTypes = haxe_ds_StringMap()
            com_sdtk_table_DatabaseReader._retrievalPrepTypes.h[""] = com_sdtk_table_DatabaseReader.getArrayPrep
            com_sdtk_table_DatabaseReader._retrievalPrepTypes.h["getColumnValue"] = com_sdtk_table_DatabaseReader.noPrep

    @staticmethod
    def read(o):
        com_sdtk_table_DatabaseReader.initMappings()
        trail = haxe_ds_StringMap()
        t = com_sdtk_table_DatabaseReader.getTypeIfNeeded(o)
        _g = 0
        _g1 = com_sdtk_table_DatabaseReader._mappings
        while (_g < len(_g1)):
            mapping = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            o2 = com_sdtk_table_DatabaseReader.executeFunctionIfThere(o,t,mapping,trail)
            if (o2 is not None):
                o = o2
                t = com_sdtk_table_DatabaseReader.getTypeIfNeeded(o)
        mapping = com_sdtk_table_DatabaseReader._finalMappings.keys()
        while mapping.hasNext():
            mapping1 = mapping.next()
            if com_sdtk_table_DatabaseReader.hasFunction(t,mapping1):
                return com_sdtk_table_DatabaseReader._finalMappings.h.get(mapping1,None)(o,t,mapping1,com_sdtk_table_DatabaseReader.getColumnNames(o,t,trail))
        return None

    @staticmethod
    def getArrayValue(o,t,i):
        return o[i]

    @staticmethod
    def getArrayPrep(o):
        return list(o)

    @staticmethod
    def getColumnValue(o,t,i):
        return o.getColumnValue(i + 1)

    @staticmethod
    def noPrep(o):
        return o

    @staticmethod
    def dbIterator(o,t,mapping,columns):
        return com_sdtk_table_DatabaseIteratorReader(o,t,mapping,columns)

    @staticmethod
    def getTypeIfNeeded(o):
        return o

    @staticmethod
    def hasFunction(t,f):
        return hasattr(t, f)

    @staticmethod
    def executeFunction(o,t,f):
        return getattr(o, f)()

    @staticmethod
    def executeFunctionIfThere(o,t,f,trail = None):
        if com_sdtk_table_DatabaseReader.hasFunction(t,f):
            if (trail is not None):
                trail.h[f] = o
                try:
                    return com_sdtk_table_DatabaseReader.executeFunction(o,t,f)
                except BaseException as _g:
                    None
                    return None
            else:
                return None
        else:
            return None

    @staticmethod
    def columnDescription(o,t):
        col = ','.join([col[0] for col in o.description])
        return col.split(",")

    @staticmethod
    def columnGetColumnName(o,t):
        return None

    @staticmethod
    def getColumnNames(o,t,trail):
        mapping = com_sdtk_table_DatabaseReader._columnMappings.keys()
        while mapping.hasNext():
            mapping1 = mapping.next()
            _hx_map = mapping1.split("-")
            f = python_internal_ArrayImpl._get(_hx_map, (len(_hx_map) - 1))
            ref = None
            if (len(_hx_map) == 1):
                ref = None
            else:
                ref = (_hx_map[0] if 0 < len(_hx_map) else None)
            if (ref is None):
                if com_sdtk_table_DatabaseReader.hasFunction(t,f):
                    return com_sdtk_table_DatabaseReader._columnMappings.h.get(mapping1,None)(o,t)
            else:
                refO = trail.h.get(ref,None)
                if (refO is not None):
                    refT = com_sdtk_table_DatabaseReader.getTypeIfNeeded(refO)
                    if com_sdtk_table_DatabaseReader.hasFunction(refT,f):
                        return com_sdtk_table_DatabaseReader._columnMappings.h.get(mapping1,None)(refO,refT)
        return None


class com_sdtk_table_DatabaseIteratorReader(com_sdtk_table_DatabaseReader):

    def __init__(self,data,dataType,mapping,columns):
        self._current = None
        self._next = None
        self._mapping = None
        self._dataType = None
        self._data = None
        self._columns = None
        self._prep = None
        self._retrieval = None
        super().__init__()
        self._columns = columns
        self._data = data
        self._dataType = dataType
        self._mapping = mapping
        self.getRetrievalType()

    def doNext(self):
        self._next = None
        try:
            self._next = com_sdtk_table_DatabaseReader.executeFunction(self._data,self._dataType,self._mapping)
        except BaseException as _g:
            None

    def columns(self):
        return len(self._columns)

    def columnName(self,i):
        return (self._columns[i] if i >= 0 and i < len(self._columns) else None)

    def readColumn(self,i):
        return self._retrieval(self._current,self._dataType,i)

    def getRetrievalType(self):
        self.doNext()
        if (self._next is not None):
            mapping = com_sdtk_table_DatabaseReader._retrievalTypes.keys()
            while mapping.hasNext():
                mapping1 = mapping.next()
                if (mapping1 != ""):
                    if com_sdtk_table_DatabaseReader.hasFunction(self._dataType,mapping1):
                        self._retrieval = com_sdtk_table_DatabaseReader._retrievalTypes.h.get(mapping1,None)
                        self._prep = com_sdtk_table_DatabaseReader._retrievalPrepTypes.h.get(mapping1,None)
            if (self._retrieval is None):
                self._retrieval = com_sdtk_table_DatabaseReader._retrievalTypes.h.get("",None)
                self._prep = com_sdtk_table_DatabaseReader._retrievalPrepTypes.h.get("",None)

    def dispose(self):
        if (not self._done):
            com_sdtk_table_DatabaseReader.executeFunctionIfThere(self._data,self._dataType,"close")
            com_sdtk_table_DatabaseReader.executeFunctionIfThere(self._data,self._dataType,"dispose")
            self._columns = None
            self._data = None
            self._dataType = None

    def hasNext(self):
        return (self._next is not None)

    def nextReuse(self,rowReader):
        self._current = self._prep(self._next)
        self.doNext()
        if (rowReader is None):
            return com_sdtk_table_DatabaseIteratorRowReader(self)
        else:
            rr = rowReader
            rr.reuse(self)
            return rr

    def next(self):
        return self.nextReuse(None)


class com_sdtk_table_DatabaseIteratorRowReader(com_sdtk_table_DataTableRowReader):

    def __init__(self,reader):
        self._reader = None
        super().__init__()
        self.reuse(reader)

    def reuse(self,reader):
        self._reader = reader
        self._index = -1

    def hasNext(self):
        return (self.index() < self._reader.columns())

    def startI(self):
        pass

    def next(self):
        self.incrementTo(self._reader.columnName((self.index() + 1)),self._reader.readColumn((self.index() + 1)),-1)
        return self.value()

    def dispose(self):
        self._reader = None


class com_sdtk_table_DelimitedInfoCustom:

    def fileStart(self):
        return self._fileStart

    def fileEnd(self):
        return self._fileEnd

    def delimiter(self):
        return self._delimiter

    def rowDelimiter(self):
        return self._boolStart

    def boolStart(self):
        return self._boolStart

    def boolEnd(self):
        return self._boolEnd

    def stringStart(self):
        return self._stringStart

    def stringEnd(self):
        return self._stringEnd

    def intStart(self):
        return self._intStart

    def intEnd(self):
        return self._intEnd

    def floatStart(self):
        return self._floatStart

    def floatEnd(self):
        return self._floatEnd

    def replacements(self):
        return self._replacements

    def replacementIndicator(self):
        return None

    def widthMinimum(self):
        return -1

    def widthMaximum(self):
        return -1


class com_sdtk_table_DelimitedReader(com_sdtk_table_DataTableReader):

    def __init__(self,diInfo,rReader):
        self._reader = None
        self._noHeaderIncluded = False
        self._header = None
        self._done = False
        self._info = None
        super().__init__()
        self._info = diInfo
        self._reader = rReader

    def startI(self):
        self._reader.start()

    def dispose(self):
        if (not self._done):
            self._done = True
            self._header = None
            self._reader.dispose()

    def hasNext(self):
        return self._reader.hasNext()

    def nextReuse(self,rowReader):
        while (self._reader.hasNext() and ((self._reader.peek() == self._info.rowDelimiter()))):
            self._reader.next()
        if (not self._reader.hasNext()):
            rowReader = None
        elif (self._header is None):
            self._header = list()
            if (rowReader is None):
                rowReader = com_sdtk_table_DelimitedRowReader(self._info,self._reader,self._header,(not self._noHeaderIncluded))
            else:
                rr = rowReader
                rr.reuse(self._info,self._reader,self._header,True)
        elif (rowReader is None):
            rowReader = com_sdtk_table_DelimitedRowReader(self._info,self._reader,self._header,False)
        else:
            rr = rowReader
            rr.reuse(self._info,self._reader,self._header,False)
        self.incrementTo(None,rowReader,self._reader.rawIndex())
        return rowReader

    def next(self):
        return self.nextReuse(None)

    def headerRowNotIncluded(self):
        return self._noHeaderIncluded

    def noHeaderIncluded(self,noHeader):
        self._noHeaderIncluded = noHeader

    def allowNoHeaderInclude(self):
        return True

    def skipRows(self,rows):
        noHeaderIncluded = self._noHeaderIncluded
        reader = None
        while (rows > 0):
            reader = self.nextReuse(reader)
            rows = (rows - 1)
        self._noHeaderIncluded = noHeaderIncluded

    def reset(self):
        self._reader.reset()
        self._header = None
        self._done = False

    @staticmethod
    def createRawReader(reader):
        return com_sdtk_table_DelimitedReader(com_sdtk_table_RAWInfo.instance,reader)

    @staticmethod
    def createCSVReader(reader):
        return com_sdtk_table_DelimitedReader(com_sdtk_table_CSVInfo.instance,reader)

    @staticmethod
    def createTSVReader(reader):
        return com_sdtk_table_DelimitedReader(com_sdtk_table_TSVInfo.instance,reader)

    @staticmethod
    def createPSVReader(reader):
        return com_sdtk_table_DelimitedReader(com_sdtk_table_PSVInfo.instance,reader)


class com_sdtk_table_DelimitedRowReader(com_sdtk_table_DataTableRowReader):

    def __init__(self,diInfo,rReader,sHeader,bInitHeader):
        self._initHeader = None
        self._currentRawIndex = None
        self._current = None
        self._reader = None
        self._header = None
        self._done = False
        self._info = None
        super().__init__()
        self.reuse(diInfo,rReader,sHeader,bInitHeader)

    def reuse(self,diInfo,rReader,sHeader,bInitHeader):
        self._info = diInfo
        self._reader = rReader
        self._header = sHeader
        self._initHeader = bInitHeader
        self._done = False
        self._index = -1
        self._rawIndex = -1
        self._started = False
        self._value = None

    def check(self):
        if ((self._reader is not None) and ((self._done != True))):
            com_sdtk_table_DelimitedRowReader._watch.start()
            sChar = ""
            iGettingValue = -1
            iGot = -1
            iCount = 0
            sValue = StringBuf()
            self._currentRawIndex = self._reader.rawIndex()
            if (not self._reader.hasNext()):
                self._current = None
                self._done = True
                return
            rowDelimiter = self._info.rowDelimiter()
            delimiter = self._info.delimiter()
            hasNext = self._reader.hasNext()
            minimum = self._info.widthMinimum()
            maximum = self._info.widthMaximum()
            replacementIndicator = self._info.replacementIndicator()
            replacements = self._info.replacements()
            while ((hasNext and (((iGettingValue >= 0) or (((sChar != rowDelimiter) and ((sChar != delimiter))))))) and (not self._done)):
                bSkip = False
                bNoNext = False
                bEndValue = False
                sChar = self._reader.peek()
                if (iGettingValue >= 0):
                    if (iGettingValue == self.isEnd(sChar)):
                        bEndValue = True
                        bSkip = True
                elif (sChar == delimiter):
                    bSkip = True
                elif (sChar == rowDelimiter):
                    bSkip = True
                    self._done = True
                elif (sChar == "\r"):
                    bSkip = True
                elif (iCount == 0):
                    iGettingValue = self.isStart(sChar)
                    if (iGettingValue >= 0):
                        iGot = iGettingValue
                        bSkip = True
                elif ((iCount >= maximum) and ((maximum > 0))):
                    bSkip = True
                    bNoNext = True
                iCount = (iCount + 1)
                if (not bNoNext):
                    self._reader.next()
                if ((replacementIndicator is None) or ((replacementIndicator == sChar))):
                    if ((replacements is not None) and ((len(replacements) > 0))):
                        checkReplace = (("null" if sChar is None else sChar) + HxOverrides.stringOrNull(self._reader.peek()))
                        replaceI = (len(replacements) - 2)
                        while (replaceI >= 0):
                            if ((replacements[replaceI] if replaceI >= 0 and replaceI < len(replacements) else None) == checkReplace):
                                sChar = python_internal_ArrayImpl._get(replacements, (replaceI + 1))
                                bSkip = False
                                bEndValue = False
                                self._reader.next()
                                break
                            replaceI = (replaceI - 2)
                hasNext = self._reader.hasNext()
                if (not bSkip):
                    s = Std.string(sChar)
                    sValue.b.write(s)
                if bEndValue:
                    iGettingValue = -1
            com_sdtk_table_DelimitedRowReader._watch.end()
            if (sValue.get_length() <= 0):
                self._current = None
            else:
                self._current = self.fromStringToType(sValue.b.getvalue())
        else:
            self._current = None

    def hasNext(self):
        if (self._current is None):
            return (not self._done)
        else:
            return True

    def isStart(self,sChar):
        if (self._info.boolStart() == sChar):
            return 0
        elif (self._info.floatStart() == sChar):
            return 1
        elif (self._info.intStart() == sChar):
            return 2
        elif (self._info.stringStart() == sChar):
            return 3
        else:
            return -1

    def isEnd(self,sChar):
        if (self._info.boolEnd() == sChar):
            return 0
        elif (self._info.floatEnd() == sChar):
            return 1
        elif (self._info.intEnd() == sChar):
            return 2
        elif (self._info.stringEnd() == sChar):
            return 3
        else:
            return -1

    def startI(self):
        self.check()

    def next(self):
        sCurrent = self._current
        iRawIndex = self._currentRawIndex
        self.check()
        if (self._header is None):
            self.incrementTo(None,sCurrent,iRawIndex)
        else:
            if self._initHeader:
                _this = self._header
                _this.append(sCurrent)
            self.incrementTo(python_internal_ArrayImpl._get(self._header, (self.index() + 1)),sCurrent,iRawIndex)
        return sCurrent

    def dispose(self):
        self._current = None
        self._info = None
        self._reader = None
        self._header = None


class com_sdtk_table_DelimitedRowWriter(com_sdtk_table_DataTableRowWriter):

    def __init__(self,info,writer):
        self._writer = None
        self._done = False
        self._written = False
        self._info = None
        super().__init__()
        self.reuse(info,writer)

    def reuse(self,info,writer):
        self._done = False
        if self._written:
            self._writer.write(self._info.rowDelimiter())
        self._written = False
        self._info = info
        self._writer = writer

    def write(self,data,name,index):
        com_sdtk_table_DelimitedRowWriter._watch.start()
        buf = StringBuf()
        if (not self._done):
            if self._written:
                s = Std.string(self._info.delimiter())
                buf.b.write(s)
            else:
                self._written = True
            self.writeValue(data,buf)
            self._writer.write(buf.b.getvalue())
        com_sdtk_table_DelimitedRowWriter._watch.end()

    def replacement(self,data):
        replacements = self._info.replacements()
        if ((replacements is not None) and ((len(replacements) > 0))):
            replaceI = 1
            while (replaceI < len(replacements)):
                data = StringTools.replace(data,(replacements[replaceI] if replaceI >= 0 and replaceI < len(replacements) else None),python_internal_ArrayImpl._get(replacements, (replaceI - 1)))
                replaceI = (replaceI + 2)
        return data

    def writeValue(self,data,buf):
        if (data is not None):
            t = Type.typeof(data)
            tmp = t.index
            if (tmp == 1):
                s = Std.string(self._info.intStart())
                buf.b.write(s)
                s = Std.string(Std.string(data))
                buf.b.write(s)
                s = Std.string(self._info.intEnd())
                buf.b.write(s)
            elif (tmp == 2):
                s = Std.string(self._info.floatStart())
                buf.b.write(s)
                s = Std.string(Std.string(data))
                buf.b.write(s)
                s = Std.string(self._info.floatEnd())
                buf.b.write(s)
            elif (tmp == 3):
                s = Std.string(self._info.boolStart())
                buf.b.write(s)
                s = Std.string(Std.string(data))
                buf.b.write(s)
                s = Std.string(self._info.boolEnd())
                buf.b.write(s)
            else:
                other = t
                s = Std.string(self._info.stringStart())
                buf.b.write(s)
                s = Std.string(self.replacement(Std.string(data)))
                buf.b.write(s)
                s = Std.string(self._info.stringEnd())
                buf.b.write(s)

    def dispose(self):
        if (not self._done):
            self._writer.write(self._info.rowDelimiter())
            self._writer.flush()
            self._done = True
            self._written = False


class com_sdtk_table_DelimitedWriter(com_sdtk_table_DataTableWriter):

    def __init__(self,diInfo,wWriter):
        self._writer = None
        self._noHeaderIncluded = False
        self._done = False
        self._info = None
        super().__init__()
        self._info = diInfo
        self._writer = wWriter

    def start(self):
        self._writer.start()
        self._writer.write(self._info.fileStart())

    def noHeaderIncluded(self,noHeader):
        self._noHeaderIncluded = noHeader

    def writeStartI(self,name,index,rowWriter):
        if (rowWriter is None):
            rowWriter = com_sdtk_table_DelimitedRowWriter(self._info,self._writer)
        else:
            rw = rowWriter
            rw.reuse(self._info,self._writer)
        return rowWriter

    def dispose(self):
        if (not self._done):
            self._writer.write(self._info.fileEnd())
            self._done = True
            self._writer.dispose()

    def writeHeaderFirst(self):
        return (not self._noHeaderIncluded)

    def writeRowNameFirst(self):
        return True

    @staticmethod
    def createTeXWriter(writer):
        return com_sdtk_table_DelimitedWriter(com_sdtk_table_TeXInfo.instance,writer)

    @staticmethod
    def createRawWriter(writer):
        return com_sdtk_table_DelimitedWriter(com_sdtk_table_RAWInfo.instance,writer)

    @staticmethod
    def createCSVWriter(writer):
        return com_sdtk_table_DelimitedWriter(com_sdtk_table_CSVInfo.instance,writer)

    @staticmethod
    def createTSVWriter(writer):
        return com_sdtk_table_DelimitedWriter(com_sdtk_table_TSVInfo.instance,writer)

    @staticmethod
    def createPSVWriter(writer):
        return com_sdtk_table_DelimitedWriter(com_sdtk_table_PSVInfo.instance,writer)


class com_sdtk_table_DirectoryInfo:

    def __init__(self):
        self._name = None
        self._path = None
        self._serial = None
        self._label = None
        self._count = 0
        self._size = 0
        self._drive = None

    def setDrive(self,sDrive):
        self._drive = sDrive

    def setLabel(self,sLabel):
        self._label = sLabel

    def setSerial(self,sSerial):
        self._serial = sSerial

    def setFullPath(self,sPath):
        self._path = sPath

    def setName(self,sName):
        self._name = sName

    def addFile(self,fiInfo):
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._size
        _hx_local_0._size = (_hx_local_1 + fiInfo.getSize())
        _hx_local_0._size
        _hx_local_2 = self
        _hx_local_3 = _hx_local_2._count
        _hx_local_2._count = (_hx_local_3 + 1)
        _hx_local_3

    def getDrive(self):
        return self._drive

    def getLabel(self):
        return self._label

    def getSerial(self):
        return self._serial

    def getFullPath(self):
        return self._path

    def getName(self):
        return self._name

    def getCount(self):
        return self._count

    def getSize(self):
        return self._size


class com_sdtk_table_FileInfo:

    def __init__(self):
        self._date = None
        self._time = 0
        self._type = 0
        self._size = 0
        self._owner = None
        self._shortName = None
        self._trueName = None
        self._name = None
        self._parent = None

    def getDirectoryInfo(self):
        return self._parent

    def getDirectory(self):
        return self._parent.getFullPath()

    def setDirectory(self,sDirectory):
        self._parent.setFullPath(sDirectory)

    def setDirectoryInfo(self,diParent):
        self._parent = diParent

    def setDrive(self,sDrive):
        self._parent.setDrive(sDrive)

    def setLabel(self,sLabel):
        self._parent.setLabel(sLabel)

    def setSerial(self,sSerial):
        self._parent.setSerial(sSerial)

    def setFullPath(self,sPath):
        startIndex = None
        iEnd = None
        if (startIndex is None):
            iEnd = sPath.rfind("\\", 0, len(sPath))
        else:
            i = sPath.rfind("\\", 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len("\\"))) if ((i == -1)) else (i + 1))
            check = sPath.find("\\", startLeft, len(sPath))
            iEnd = (check if (((check > i) and ((check <= startIndex)))) else i)
        self._parent.setName(HxString.substr(sPath,iEnd,None))
        self._name = HxString.substr(sPath,(iEnd + 1),None)

    def setName(self,sName):
        self._name = sName

    def addFile(self,fiInfo):
        self._parent.addFile(fiInfo)

    def getDrive(self):
        return self.getDirectoryInfo().getDrive()

    def getLabel(self):
        return self.getDirectoryInfo().getLabel()

    def getSerial(self):
        return self.getDirectoryInfo().getSerial()

    def getFullPath(self):
        return ((Std.string(self.getDirectoryInfo().getFullPath) + "\\") + HxOverrides.stringOrNull(self.getName()))

    def getName(self):
        return self._name

    def getCount(self):
        return self.getDirectoryInfo().getCount()

    def getDate(self):
        return self._date

    def getTime(self):
        return self._time

    def getIsDirectory(self):
        return (((self._type & com_sdtk_table_FileInfo.IS_DIRECTORY)) == com_sdtk_table_FileInfo.IS_DIRECTORY)

    def getIsJunction(self):
        return (((self._type & com_sdtk_table_FileInfo.IS_JUNCTION)) == com_sdtk_table_FileInfo.IS_JUNCTION)

    def MergeDateTime(self):
        pass

    def setTrueName(self,sTrueName):
        self._trueName = sTrueName

    def getTrueName(self):
        return self._trueName

    def setShortName(self,sShortName):
        self._shortName = sShortName

    def getShortName(self):
        return self._shortName

    def setOwner(self,sOwner):
        self._owner = sOwner

    def getOwner(self):
        return self._owner

    def setDate(self,dDate):
        self._date = dDate
        self.MergeDateTime()

    def setTime(self,iTime):
        self._time = iTime
        self.MergeDateTime()

    def setSize(self,iSize):
        self._size = iSize

    def getSize(self):
        return self._size

    def setIsDirectory(self,bIsDirectory):
        self._type = ((self._type | com_sdtk_table_FileInfo.IS_DIRECTORY) if bIsDirectory else (self._type & ((-1 ^ com_sdtk_table_FileInfo.IS_DIRECTORY))))

    def setIsJunction(self,bIsJunction):
        self._type = ((self._type | com_sdtk_table_FileInfo.IS_JUNCTION) if bIsJunction else (self._type & ((-1 ^ com_sdtk_table_FileInfo.IS_JUNCTION))))


class com_sdtk_table_FileSystemReader(com_sdtk_table_DataTableReader):

    def __init__(self,fshHandler,rReader):
        self._current = None
        self._previous = None
        self._reader = None
        self._handler = None
        super().__init__()
        self._handler = fshHandler
        self._reader = rReader

    def check(self,reuse):
        if (reuse == False):
            self._current = com_sdtk_table_FileSystemRowReader(self._handler,self._reader,self._current)
        elif (self._previous is None):
            self.check(False)
        else:
            self._previous.reuse(self._handler,self._reader,self._current)
            self._current = self._previous

    def startI(self):
        self._reader.start()
        self.check(False)

    def dispose(self):
        if (self._reader is not None):
            self._reader.dispose()
            self._reader = None
            self._handler = None
            self._previous = None
            self._current = None

    def hasNext(self):
        return (self._current is not None)

    def nextI(self,reuse):
        if (self._current is not None):
            fsrrCurrent = self._current
            self.check(reuse)
            self._previous = fsrrCurrent
            return fsrrCurrent
        else:
            return None

    def nextReuse(self,rowReader):
        return self.nextI(True)

    def next(self):
        return self.nextI(False)

    def reset(self):
        self._reader.reset()
        self._previous = None
        self._current = None

    @staticmethod
    def createCMDDirReader(rReader):
        return com_sdtk_table_FileSystemReader(com_sdtk_table_CMDDirHandler.instance,rReader)


class com_sdtk_table_FileSystemRowReader(com_sdtk_table_DataTableRowReader):

    def __init__(self,fshHandler,rReader,fsrrPrevious):
        self._array = None
        self._current = None
        self._reader = None
        self._handler = None
        super().__init__()
        self.reuse(fshHandler,rReader,fsrrPrevious)

    def reuse(self,fshHandler,rReader,fsrrPrevious):
        self._handler = fshHandler
        self._reader = rReader
        if (fsrrPrevious is not None):
            self._current = self._handler.next(self._reader,fsrrPrevious._current)
            fsrrPrevious._current = None
        else:
            self._current = self._handler.next(self._reader,None)
        if (self._current is not None):
            self._array = list()
            _this = self._array
            x = self._current.getDrive()
            _this.append(x)
            _this = self._array
            x = self._current.getLabel()
            _this.append(x)
            _this = self._array
            x = self._current.getSerial()
            _this.append(x)
            _this = self._array
            x = self._current.getDirectory()
            _this.append(x)
            _this = self._array
            x = self._current.getOwner()
            _this.append(x)
            _this = self._array
            x = self._current.getName()
            _this.append(x)
            _this = self._array
            x = self._current.getShortName()
            _this.append(x)
            _this = self._array
            x = self._current.getTrueName()
            _this.append(x)
            _this = self._array
            x = self._current.getDate()
            _this.append(x)
            _this = self._array
            x = self._current.getSize()
            _this.append(x)
            _this = self._array
            x = ("Directory" if (self._current.getIsDirectory()) else ("Junction" if (self._current.getIsJunction()) else "File"))
            _this.append(x)
        self._index = -1
        self._started = False
        self._value = None

    def startI(self):
        pass

    def dispose(self):
        if (self._reader is not None):
            self._reader.dispose()
            self._reader = None
            self._handler = None
            self._array = None

    def hasNext(self):
        if (self._current is not None):
            return (self.index() < len(self._array))
        else:
            return False

    def next(self):
        self.incrementTo(python_internal_ArrayImpl._get(com_sdtk_table_FileSystemRowReader._fields, self.index()),python_internal_ArrayImpl._get(self._array, self.index()),self.index())
        return self.value()


class com_sdtk_table_FileSystemRowWriter(com_sdtk_table_DataTableRowWriter):

    def __init__(self,fshHandler,wWriter,fsrwPrevious,iOptions):
        self._options = None
        self._tally = None
        self._current = None
        self._previous = None
        self._writer = None
        self._handler = None
        super().__init__()
        self.reuse(fshHandler,wWriter,fsrwPrevious,iOptions)

    def reuse(self,fshHandler,wWriter,fsrwPrevious,iOptions):
        self._current = com_sdtk_table_FileInfo()
        self._handler = fshHandler
        self._writer = wWriter
        if ((fsrwPrevious is not None) and ((fsrwPrevious != self))):
            self._previous = fsrwPrevious._current
            self._tally = fsrwPrevious._tally
            fsrwPrevious._current = None
            fsrwPrevious._tally = None
        else:
            self._tally = com_sdtk_table_TallyInfo()
        self._options = iOptions

    def write(self,data,name,index):
        _g = StringTools.trim(name).lower()
        _hx_local_0 = len(_g)
        if (_hx_local_0 == 9):
            if (_g == "directory"):
                self._current.setDirectory(data)
        elif (_hx_local_0 == 5):
            if (_g == "drive"):
                self._current.setDrive(data)
            elif (_g == "label"):
                self._current.setLabel(data)
            elif (_g == "owner"):
                self._current.setOwner(data)
            elif (_g == "short"):
                self._current.setShortName(data)
        elif (_hx_local_0 == 4):
            if (_g == "file"):
                self._current.setName(data)
            elif (_g == "size"):
                self._current.setSize(data)
            elif (_g == "true"):
                self._current.setTrueName(data)
            elif (_g == "type"):
                _g = HxString.substr(StringTools.trim(Std.string(data)),0,3).lower()
                if (_g == "dir"):
                    self._current.setIsDirectory(True)
                elif (_g == "jun"):
                    self._current.setIsJunction(True)
                else:
                    pass
        elif (_hx_local_0 == 8):
            if (_g == "modified"):
                self._current.setDate(data)
        elif (_hx_local_0 == 6):
            if (_g == "serial"):
                self._current.setSerial(data)
        else:
            pass

    def dispose(self):
        if (self._writer is not None):
            self._writer = None
            self._handler = None
            self._previous = None
            super().dispose()


class com_sdtk_table_FileSystemWriter(com_sdtk_table_DataTableWriter):

    def __init__(self,fshHandler,wWriter):
        self._previous = None
        self._writer = None
        self._handler = None
        super().__init__()
        self._handler = fshHandler
        self._writer = wWriter

    def start(self):
        self._writer.start()

    def writeStartI(self,name,index,rowWriter):
        if (rowWriter is None):
            self._previous = com_sdtk_table_FileSystemRowWriter(self._handler,self._writer,self._previous,0)
        else:
            self._previous = rowWriter
            self._previous.reuse(self._handler,self._writer,self._previous,0)
        return self._previous

    def dispose(self):
        if (self._writer is not None):
            self._writer.dispose()
            self._writer = None
            self._handler = None
            self._previous = None
            super().dispose()

    @staticmethod
    def createCMDDirWriter(wWriter):
        return com_sdtk_table_FileSystemWriter(com_sdtk_table_CMDDirHandler.instance,wWriter)

class com_sdtk_table_Format(Enum):
    __slots__ = ()
    _hx_class_name = "com.sdtk.table.Format"
    _hx_constructs = ["CSV", "PSV", "TSV", "DIR", "INI", "JSON", "PROPERTIES", "SQL", "Haxe", "Python", "Java", "CSharp", "SPLUNK", "HTMLTable", "ARRAY", "MAP", "ARRAYMAP", "MAPARRAY", "DB", "RAW", "TEX"]
com_sdtk_table_Format.CSV = com_sdtk_table_Format("CSV", 0, ())
com_sdtk_table_Format.PSV = com_sdtk_table_Format("PSV", 1, ())
com_sdtk_table_Format.TSV = com_sdtk_table_Format("TSV", 2, ())
com_sdtk_table_Format.DIR = com_sdtk_table_Format("DIR", 3, ())
com_sdtk_table_Format.INI = com_sdtk_table_Format("INI", 4, ())
com_sdtk_table_Format.JSON = com_sdtk_table_Format("JSON", 5, ())
com_sdtk_table_Format.PROPERTIES = com_sdtk_table_Format("PROPERTIES", 6, ())
com_sdtk_table_Format.SQL = com_sdtk_table_Format("SQL", 7, ())
com_sdtk_table_Format.Haxe = com_sdtk_table_Format("Haxe", 8, ())
com_sdtk_table_Format.Python = com_sdtk_table_Format("Python", 9, ())
com_sdtk_table_Format.Java = com_sdtk_table_Format("Java", 10, ())
com_sdtk_table_Format.CSharp = com_sdtk_table_Format("CSharp", 11, ())
com_sdtk_table_Format.SPLUNK = com_sdtk_table_Format("SPLUNK", 12, ())
com_sdtk_table_Format.HTMLTable = com_sdtk_table_Format("HTMLTable", 13, ())
com_sdtk_table_Format.ARRAY = com_sdtk_table_Format("ARRAY", 14, ())
com_sdtk_table_Format.MAP = com_sdtk_table_Format("MAP", 15, ())
com_sdtk_table_Format.ARRAYMAP = com_sdtk_table_Format("ARRAYMAP", 16, ())
com_sdtk_table_Format.MAPARRAY = com_sdtk_table_Format("MAPARRAY", 17, ())
com_sdtk_table_Format.DB = com_sdtk_table_Format("DB", 18, ())
com_sdtk_table_Format.RAW = com_sdtk_table_Format("RAW", 19, ())
com_sdtk_table_Format.TEX = com_sdtk_table_Format("TEX", 20, ())
com_sdtk_table_Format._hx_class = com_sdtk_table_Format


class com_sdtk_table_Formats:

    def __init__(self):
        pass

    @staticmethod
    def CSV():
        return com_sdtk_table_Format.CSV

    @staticmethod
    def PSV():
        return com_sdtk_table_Format.PSV

    @staticmethod
    def TSV():
        return com_sdtk_table_Format.TSV

    @staticmethod
    def DIR():
        return com_sdtk_table_Format.DIR

    @staticmethod
    def INI():
        return com_sdtk_table_Format.INI

    @staticmethod
    def JSON():
        return com_sdtk_table_Format.JSON

    @staticmethod
    def PROPERTIES():
        return com_sdtk_table_Format.PROPERTIES

    @staticmethod
    def SQL():
        return com_sdtk_table_Format.SQL

    @staticmethod
    def Haxe():
        return com_sdtk_table_Format.Haxe

    @staticmethod
    def Python():
        return com_sdtk_table_Format.Python

    @staticmethod
    def Java():
        return com_sdtk_table_Format.Java

    @staticmethod
    def CSharp():
        return com_sdtk_table_Format.CSharp

    @staticmethod
    def SPLUNK():
        return com_sdtk_table_Format.SPLUNK

    @staticmethod
    def HTMLTable():
        return com_sdtk_table_Format.HTMLTable

    @staticmethod
    def ARRAY():
        return com_sdtk_table_Format.ARRAY

    @staticmethod
    def MAP():
        return com_sdtk_table_Format.MAP

    @staticmethod
    def ARRAYMAP():
        return com_sdtk_table_Format.ARRAYMAP

    @staticmethod
    def MAPARRAY():
        return com_sdtk_table_Format.MAPARRAY

    @staticmethod
    def DB():
        return com_sdtk_table_Format.DB

    @staticmethod
    def RAW():
        return com_sdtk_table_Format.RAW

    @staticmethod
    def TEX():
        return com_sdtk_table_Format.TEX


class com_sdtk_table_HaxeInfoAbstract:

    def __init__(self):
        pass

    def start(self):
        return "["

    def end(self):
        return "]"

    def rowStart(self,name,index):
        return ""

    def betweenRows(self):
        return ",\n"

    def rowEnd(self):
        return "]"

    def arrayRowStart(self,name,index):
        return "[ "

    def mapRowStart(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("\"" + ("null" if name is None else name)) + "\" => [")
        else:
            return (Std.string(index) + " => [")

    def mapIntEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return ((("\"" + ("null" if name is None else name)) + "\" => ") + Std.string(data))
        else:
            return ((Std.string(index) + " => ") + Std.string(data))

    def mapBoolEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return ((("\"" + ("null" if name is None else name)) + "\" => ") + Std.string(data))
        else:
            return ((Std.string(index) + " => ") + Std.string(data))

    def mapFloatEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return ((("\"" + ("null" if name is None else name)) + "\" => ") + Std.string(data))
        else:
            return ((Std.string(index) + " => ") + Std.string(data))

    def mapOtherEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("\"" + ("null" if name is None else name)) + "\" => \"") + ("null" if data is None else data)) + "\"")
        else:
            return (((Std.string(index) + " => \"") + ("null" if data is None else data)) + "\"")

    def mapNullEntry(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("\"" + ("null" if name is None else name)) + "\" => null")
        else:
            return (Std.string(index) + " => null")

    def arrayIntEntry(self,data,name,index):
        return Std.string(data)

    def arrayBoolEntry(self,data,name,index):
        return Std.string(data)

    def arrayFloatEntry(self,data,name,index):
        return Std.string(data)

    def arrayOtherEntry(self,data,name,index):
        return (("\"" + ("null" if data is None else data)) + "\"")

    def arrayNullEntry(self,name,index):
        return "null"

    def intEntry(self,data,name,index):
        return None

    def boolEntry(self,data,name,index):
        return None

    def floatEntry(self,data,name,index):
        return None

    def otherEntry(self,data,name,index):
        return None

    def nullEntry(self,name,index):
        return None

    def betweenEntries(self):
        return ","

    def replacements(self):
        return ["\\\"", "\"", "\\\n", "\n", "\\\t", "\t"]


class com_sdtk_table_HaxeInfoArrayOfArrays(com_sdtk_table_HaxeInfoAbstract):

    def __init__(self):
        super().__init__()

    def rowStart(self,name,index):
        return self.arrayRowStart(name,index)

    def intEntry(self,data,name,index):
        return self.arrayIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.arrayBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.arrayFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.arrayOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.arrayNullEntry(name,index)


class com_sdtk_table_HaxeInfoArrayOfMaps(com_sdtk_table_HaxeInfoAbstract):

    def __init__(self):
        super().__init__()

    def rowStart(self,name,index):
        return self.arrayRowStart(name,index)

    def intEntry(self,data,name,index):
        return self.mapIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntry(name,index)


class com_sdtk_table_HaxeInfoMapOfArrays(com_sdtk_table_HaxeInfoAbstract):

    def __init__(self):
        super().__init__()

    def rowStart(self,name,index):
        return self.mapRowStart(name,index)

    def intEntry(self,data,name,index):
        return self.arrayIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.arrayBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.arrayFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.arrayOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.arrayNullEntry(name,index)


class com_sdtk_table_HaxeInfoMapOfMaps(com_sdtk_table_HaxeInfoAbstract):

    def __init__(self):
        super().__init__()

    def rowStart(self,name,index):
        return self.mapRowStart(name,index)

    def intEntry(self,data,name,index):
        return self.mapIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntry(name,index)


class com_sdtk_table_KeyValueHandler:
    pass


class com_sdtk_table_INIHandler:

    def __init__(self):
        pass

    def favorReadAll(self):
        return True

    def oneRowPerFile(self):
        return False

    def read(self,rReader):
        rReader = rReader.switchToLineReader()
        mMap = haxe_ds_StringMap()
        while rReader.hasNext():
            sLine = rReader.peek()
            sFirst = ("" if ((0 >= len(sLine))) else sLine[0])
            if (sFirst == "["):
                break
            elif ((sFirst == ";") or (((sFirst == "#") and (((("" if ((1 >= len(sLine))) else sLine[1])) == " "))))):
                rReader.next()
                continue
            else:
                startIndex = None
                iIndex = (sLine.find("=") if ((startIndex is None)) else HxString.indexOfImpl(sLine,"=",startIndex))
                key = com_sdtk_table_INIHandler.convertFrom(HxString.substr(sLine,0,iIndex))
                value = com_sdtk_table_INIHandler.convertFrom(HxString.substr(sLine,(iIndex + 1),None))
                mMap.h[key] = value
                rReader.next()
        return mMap

    def write(self,wWriter,mMap):
        wWriter = wWriter.switchToLineWriter()
        value = mMap.h.get("__name__",None)
        if (value is not None):
            wWriter.write((("[" + HxOverrides.stringOrNull(com_sdtk_table_INIHandler.convertTo(Std.string(value)))) + "]\n"))
            value = None
        key = mMap.keys()
        while key.hasNext():
            key1 = key.next()
            value = mMap.h.get(key1,None)
            if (key1 != "__name__"):
                wWriter.write((((HxOverrides.stringOrNull(com_sdtk_table_INIHandler.convertTo(key1)) + "=") + HxOverrides.stringOrNull(com_sdtk_table_INIHandler.convertTo(Std.string(value)))) + "\n"))

    def readAll(self,rReader,aMaps,aNames):
        rReader = rReader.switchToLineReader()
        while rReader.hasNext():
            sLine = rReader.peek()
            sFirst = ("" if ((0 >= len(sLine))) else sLine[0])
            if ((sFirst == ";") or (((sFirst == "#") and (((("" if ((1 >= len(sLine))) else sLine[1])) == " "))))):
                continue
            elif (sFirst == "["):
                sKey = HxString.substr(sLine,1,None)
                index = (len(sKey) - 1)
                if ((("" if (((index < 0) or ((index >= len(sKey))))) else sKey[index])) == "\n"):
                    sKey = HxString.substr(sKey,0,(len(sKey) - 1))
                index1 = (len(sKey) - 1)
                if ((("" if (((index1 < 0) or ((index1 >= len(sKey))))) else sKey[index1])) == "]"):
                    sKey = HxString.substr(sKey,0,(len(sKey) - 1))
                sKey = com_sdtk_table_INIHandler.convertTo(sKey)
                rReader.next()
                x = self.read(rReader)
                aMaps.append(x)
                aNames.append(sKey)
            else:
                x1 = self.read(rReader)
                aMaps.append(x1)
                aNames.append("")

    def writeAll(self,wWriter,aMaps,aNames):
        i = 0
        wWriter = wWriter.switchToLineWriter()
        while (i < len(aMaps)):
            wWriter.write((("[" + HxOverrides.stringOrNull(com_sdtk_table_INIHandler.convertTo((aNames[i] if i >= 0 and i < len(aNames) else None)))) + "]"))
            aMaps1 = i
            i = (i + 1)
            self.write(wWriter,(aMaps[aMaps1] if aMaps1 >= 0 and aMaps1 < len(aMaps) else None))

    @staticmethod
    def convertFrom(sValue):
        sValue = StringTools.trim(sValue)
        sValue = StringTools.replace(sValue,"\\\\","\\")
        sValue = StringTools.replace(sValue,"\\'","'")
        sValue = StringTools.replace(sValue,"\\\"","\"")
        sValue = StringTools.replace(sValue,"\\0","\x00")
        sValue = StringTools.replace(sValue,"\\a","\x07")
        sValue = StringTools.replace(sValue,"\\b","\x08")
        sValue = StringTools.replace(sValue,"\\t","\t")
        sValue = StringTools.replace(sValue,"\\r","\r")
        sValue = StringTools.replace(sValue,"\\n","\n")
        sValue = StringTools.replace(sValue,"\\;",";")
        sValue = StringTools.replace(sValue,"\\#","#")
        sValue = StringTools.replace(sValue,"\\=","=")
        sValue = StringTools.replace(sValue,"\\:",":")
        return sValue

    @staticmethod
    def convertTo(sValue):
        sValue = StringTools.replace(sValue,"\\","\\\\")
        sValue = StringTools.replace(sValue,"'","\\'")
        sValue = StringTools.replace(sValue,"\"","\\\"")
        sValue = StringTools.replace(sValue,"\x00","\\0")
        sValue = StringTools.replace(sValue,"\x07","\\a")
        sValue = StringTools.replace(sValue,"\x08","\\b")
        sValue = StringTools.replace(sValue,"\t","\\t")
        sValue = StringTools.replace(sValue,"\r","\\r")
        sValue = StringTools.replace(sValue,"\n","\\n")
        sValue = StringTools.replace(sValue,";","\\;")
        sValue = StringTools.replace(sValue,"#","\\#")
        sValue = StringTools.replace(sValue,"=","\\=")
        sValue = StringTools.replace(sValue,":","\\:")
        sValue = StringTools.trim(sValue)
        return sValue


class com_sdtk_table_JSONHandler:

    def __init__(self):
        pass

    def favorReadAll(self):
        return True

    def oneRowPerFile(self):
        return False

    def read(self,rReader):
        return com_sdtk_table_JSONHandler.buildMap(python_lib_Json.loads(com_sdtk_table_JSONHandler.readValue(rReader),**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'object_hook': python_Lib.dictToAnon}))))

    def write(self,wWriter,mMap):
        wWriter.write(haxe_format_JsonPrinter.print(mMap,None,None))

    def readAll(self,rReader,aMaps,aNames):
        dData = python_lib_Json.loads(com_sdtk_table_JSONHandler.readValue(rReader),**python__KwArgs_KwArgs_Impl_.fromT(_hx_AnonObject({'object_hook': python_Lib.dictToAnon})))
        _g = 0
        _g1 = python_Boot.fields(dData)
        while (_g < len(_g1)):
            keyRow = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            valueRow = Reflect.field(dData,keyRow)
            x = com_sdtk_table_JSONHandler.buildMap(valueRow)
            aMaps.append(x)
            aNames.append(keyRow)

    def writeAll(self,wWriter,aMaps,aNames):
        if (((aNames[0] if 0 < len(aNames) else None) == 0) and ((python_internal_ArrayImpl._get(aNames, (len(aNames) - 1)) == ((len(aNames) - 1))))):
            aValues = list()
            _g = 0
            while (_g < len(aMaps)):
                value = (aMaps[_g] if _g >= 0 and _g < len(aMaps) else None)
                _g = (_g + 1)
                aValues.append(value)
            wWriter.write(haxe_format_JsonPrinter.print(aValues,None,None))
        else:
            i = 0
            wWriter.write("{\n")
            while (i < len(aNames)):
                aName = (aNames[i] if i >= 0 and i < len(aNames) else None)
                sName = Std.string(aName)
                mValue = (aMaps[i] if i >= 0 and i < len(aMaps) else None)
                if (aName == sName):
                    wWriter.write("\"")
                    wWriter.write(sName)
                    wWriter.write("\"")
                else:
                    wWriter.write(sName)
                wWriter.write(":")
                self.write(wWriter,mValue)
                wWriter.write(",\n")
                i = (i + 1)
            wWriter.write("}")

    @staticmethod
    def buildMap(dData):
        mMap = haxe_ds_StringMap()
        _g = 0
        _g1 = python_Boot.fields(dData)
        while (_g < len(_g1)):
            key = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            value = Reflect.field(dData,key)
            mMap.h[key] = value
        return mMap

    @staticmethod
    def readValue(rReader):
        sbBuffer_b = python_lib_io_StringIO()
        while rReader.hasNext():
            sbBuffer_b.write(Std.string(rReader.next()))
        return sbBuffer_b.getvalue()


class com_sdtk_table_JavaInfoAbstract:

    def __init__(self):
        pass

    def start(self):
        return ""

    def end(self):
        return ""

    def arrayStart(self):
        return "{"

    def arrayEnd(self):
        return "}"

    def mapStart(self):
        return "java.util.Map.ofEntries("

    def mapEnd(self):
        return ")"

    def mapStartLegacy(self):
        return "new java.util.HashMap<String, String>() {{"

    def mapEndLegacy(self):
        return "}};"

    def rowStart(self,name,index):
        return ""

    def rowEnd(self):
        return ""

    def betweenRows(self):
        return ",\n"

    def mapRowEnd(self):
        return ")"

    def mapRowEndLegacy(self):
        return "}}"

    def arrayRowEnd(self):
        return ""

    def arrayRowStart(self,name,index):
        return ""

    def mapRowStart(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("entry(\"" + ("null" if name is None else name)) + "\", ")
        else:
            return (("entry(" + Std.string(index)) + ", ")

    def mapIntEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("entry(\"" + ("null" if name is None else name)) + "\", ") + Std.string(data)) + ")")
        else:
            return (((("entry(" + Std.string(index)) + ", ") + Std.string(data)) + ")")

    def mapBoolEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("entry(\"" + ("null" if name is None else name)) + "\", ") + Std.string(data)) + ")")
        else:
            return (((("entry(" + Std.string(index)) + ", ") + Std.string(data)) + ")")

    def mapFloatEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("entry(\"" + ("null" if name is None else name)) + "\", ") + Std.string(data)) + ")")
        else:
            return (((("entry(" + Std.string(index)) + ", ") + Std.string(data)) + ")")

    def mapOtherEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("entry(\"" + ("null" if name is None else name)) + "\", \"") + ("null" if data is None else data)) + "\")")
        else:
            return (((("entry(" + Std.string(index)) + ", \"") + ("null" if data is None else data)) + "\")")

    def mapNullEntry(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("entry(\"" + ("null" if name is None else name)) + "\", null)")
        else:
            return (("entry(" + Std.string(index)) + ",  null)")

    def mapRowStartLegacy(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("put(\"" + ("null" if name is None else name)) + "\", ")
        else:
            return (("put(" + Std.string(index)) + ", ")

    def mapIntEntryLegacy(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("put(\"" + ("null" if name is None else name)) + "\", ") + Std.string(data)) + ")")
        else:
            return (((("put(" + Std.string(index)) + ", ") + Std.string(data)) + ")")

    def mapBoolEntryLegacy(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("put(\"" + ("null" if name is None else name)) + "\", ") + Std.string(data)) + ")")
        else:
            return (((("put(" + Std.string(index)) + ", ") + Std.string(data)) + ")")

    def mapFloatEntryLegacy(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("put(\"" + ("null" if name is None else name)) + "\", ") + Std.string(data)) + ")")
        else:
            return (((("put(" + Std.string(index)) + ", ") + Std.string(data)) + ")")

    def mapOtherEntryLegacy(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("put(\"" + ("null" if name is None else name)) + "\", \"") + ("null" if data is None else data)) + "\")")
        else:
            return (((("put(" + Std.string(index)) + ", \"") + ("null" if data is None else data)) + "\")")

    def mapNullEntryLegacy(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("put(\"" + ("null" if name is None else name)) + "\", null)")
        else:
            return (("put(" + Std.string(index)) + ",  null)")

    def arrayIntEntry(self,data,name,index):
        return Std.string(data)

    def arrayBoolEntry(self,data,name,index):
        return Std.string(data)

    def arrayFloatEntry(self,data,name,index):
        return Std.string(data)

    def arrayOtherEntry(self,data,name,index):
        return (("\"" + ("null" if data is None else data)) + "\"")

    def arrayNullEntry(self,name,index):
        return "null"

    def intEntry(self,data,name,index):
        return None

    def boolEntry(self,data,name,index):
        return None

    def floatEntry(self,data,name,index):
        return None

    def otherEntry(self,data,name,index):
        return None

    def nullEntry(self,name,index):
        return None

    def betweenEntries(self):
        return ","

    def replacements(self):
        return ["\\\"", "\"", "\\\n", "\n", "\\\t", "\t"]


class com_sdtk_table_JavaInfoArrayOfArrays(com_sdtk_table_JavaInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.arrayStart()

    def end(self):
        return self.arrayEnd()

    def rowEnd(self):
        return self.arrayEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.arrayRowStart(name,index)) + HxOverrides.stringOrNull(self.arrayStart()))

    def intEntry(self,data,name,index):
        return self.arrayIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.arrayBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.arrayFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.arrayOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.arrayNullEntry(name,index)


class com_sdtk_table_JavaInfoArrayOfMaps(com_sdtk_table_JavaInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.arrayStart()

    def rowEnd(self):
        return self.mapEnd()

    def end(self):
        return self.arrayEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.arrayRowStart(name,index)) + HxOverrides.stringOrNull(self.mapStart()))

    def intEntry(self,data,name,index):
        return self.mapIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntry(name,index)


class com_sdtk_table_JavaInfoArrayOfMapsLegacy(com_sdtk_table_JavaInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.arrayStart()

    def rowEnd(self):
        return self.mapEndLegacy()

    def end(self):
        return self.arrayEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.arrayRowStart(name,index)) + HxOverrides.stringOrNull(self.mapStartLegacy()))

    def intEntry(self,data,name,index):
        return self.mapIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntry(name,index)


class com_sdtk_table_JavaInfoMapOfArrays(com_sdtk_table_JavaInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.mapStart()

    def rowEnd(self):
        return self.arrayEnd()

    def end(self):
        return self.mapEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.mapRowStart(name,index)) + HxOverrides.stringOrNull(self.arrayStart()))

    def intEntry(self,data,name,index):
        return self.arrayIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.arrayBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.arrayFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.arrayOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.arrayNullEntry(name,index)


class com_sdtk_table_JavaInfoMapOfArraysLegacy(com_sdtk_table_JavaInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.mapStartLegacy()

    def rowEnd(self):
        return self.arrayEnd()

    def end(self):
        return self.mapEndLegacy()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.mapRowStartLegacy(name,index)) + HxOverrides.stringOrNull(self.arrayStart()))

    def intEntry(self,data,name,index):
        return self.arrayIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.arrayBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.arrayFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.arrayOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.arrayNullEntry(name,index)


class com_sdtk_table_JavaInfoMapOfMaps(com_sdtk_table_JavaInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.mapStart()

    def end(self):
        return self.mapEnd()

    def rowEnd(self):
        return self.mapEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.mapRowStart(name,index)) + HxOverrides.stringOrNull(self.mapStart()))

    def intEntry(self,data,name,index):
        return self.mapIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntry(name,index)


class com_sdtk_table_JavaInfoMapOfMapsLegacy(com_sdtk_table_JavaInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.mapStartLegacy()

    def end(self):
        return self.mapEndLegacy()

    def rowEnd(self):
        return self.mapEndLegacy()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.mapRowStartLegacy(name,index)) + HxOverrides.stringOrNull(self.mapStartLegacy()))

    def intEntry(self,data,name,index):
        return self.mapIntEntryLegacy(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntryLegacy(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntryLegacy(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntryLegacy(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntryLegacy(name,index)


class com_sdtk_table_KeyValueReader(com_sdtk_table_DataTableReader):

    def __init__(self,fshHandler,rReader):
        self._columns = None
        self._names = None
        self._maps = None
        self._reader = None
        self._handler = None
        super().__init__()
        self._handler = fshHandler
        self._reader = rReader

    def check(self):
        self._maps = list()
        self._names = list()
        self._handler.readAll(self._reader,self._maps,self._names)
        self._columns = list()
        mDefinedColumns = haxe_ds_StringMap()
        _g = 0
        _g1 = self._maps
        while (_g < len(_g1)):
            mMap = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
            _g = (_g + 1)
            key = mMap.keys()
            while key.hasNext():
                key1 = key.next()
                value = mMap.h.get(key1,None)
                keyString = ("" + ("null" if key1 is None else key1))
                if (mDefinedColumns.h.get(keyString,None) is None):
                    mDefinedColumns.h[keyString] = len(self._columns)
                    _this = self._columns
                    _this.append(key1)

    def startI(self):
        self._reader.start()
        self.check()

    def dispose(self):
        if (self._reader is not None):
            self._reader.dispose()
            self._reader = None
            self._handler = None
            self._maps = None
            self._names = None
            self._columns = None
            super().dispose()

    def hasNext(self):
        return (self.index() < ((len(self._maps) - 1)))

    def nextReuse(self,rowReader):
        if self.hasNext():
            if (rowReader is None):
                rowReader = com_sdtk_table_KeyValueRowReader(python_internal_ArrayImpl._get(self._maps, (self.index() + 1)),self._columns)
            else:
                rr = rowReader
                rr.reuse(python_internal_ArrayImpl._get(self._maps, (self.index() + 1)),self._columns)
            self.incrementTo(python_internal_ArrayImpl._get(self._names, (self.index() + 1)),rowReader,(self.index() + 1))
            return self.value()
        else:
            return None

    def next(self):
        return self.nextReuse(None)

    def reset(self):
        self._reader.reset()
        self._maps = None
        self._names = None
        self._columns = None

    @staticmethod
    def createINIReader(rReader):
        return com_sdtk_table_KeyValueReader(com_sdtk_table_INIHandler.instance,rReader)

    @staticmethod
    def createJSONReader(rReader):
        return com_sdtk_table_KeyValueReader(com_sdtk_table_JSONHandler.instance,rReader)

    @staticmethod
    def createPropertiesReader(rReader):
        return com_sdtk_table_KeyValueReader(com_sdtk_table_PropertiesHandler.instance,rReader)

    @staticmethod
    def createSplunkReader(rReader):
        return com_sdtk_table_KeyValueReader(com_sdtk_table_SplunkHandler.instance,rReader)


class com_sdtk_table_KeyValueRowReader(com_sdtk_table_DataTableRowReader):

    def __init__(self,mMap,cColumns):
        self._columns = None
        self._map = None
        super().__init__()
        self.reuse(mMap,cColumns)

    def reuse(self,mMap,cColumns):
        self._map = mMap
        self._columns = cColumns
        self._index = -1
        self._rawIndex = -1
        self._started = False
        self._value = None

    def startI(self):
        pass

    def dispose(self):
        self._map = None
        self._columns = None

    def hasNext(self):
        return (self.index() < ((len(self._columns) - 1)))

    def next(self):
        sColumn = python_internal_ArrayImpl._get(self._columns, (self.index() + 1))
        self.incrementTo(sColumn,self._map.h.get(sColumn,None),(self.index() + 1))
        return self.value()


class com_sdtk_table_KeyValueRowWriter(com_sdtk_table_DataTableRowWriter):

    def __init__(self,fshHandler,wWriter,name,index):
        self._rowIndex = None
        self._map = haxe_ds_StringMap()
        self._name = None
        self._writer = None
        self._handler = None
        super().__init__()
        self.reuse(fshHandler,wWriter,name,index)

    def reuse(self,fshHandler,wWriter,name,index):
        self._handler = fshHandler
        self._writer = wWriter
        self._name = name
        self._rowIndex = index

    def start(self):
        self._writer.start()

    def write(self,data,name,index):
        if (data is not None):
            self._map.h[name] = data

    def dispose(self):
        if (self._writer is not None):
            self._handler.write(self._writer,self._map)
            self._writer = None
            self._handler = None
            self._name = None
            self._map = None
            super().dispose()


class com_sdtk_table_KeyValueWriter(com_sdtk_table_DataTableWriter):

    def __init__(self,fshHandler,wWriter):
        self._writer = None
        self._handler = None
        super().__init__()
        self._handler = fshHandler
        self._writer = wWriter

    def start(self):
        self._writer.start()

    def writeStartI(self,name,index,rowWriter):
        if (rowWriter is None):
            rowWriter = com_sdtk_table_KeyValueRowWriter(self._handler,self._writer,name,index)
        else:
            rw = rowWriter
            rw.reuse(self._handler,self._writer,name,index)
        return rowWriter

    def oneRowPerFile(self):
        return self._handler.oneRowPerFile()

    def dispose(self):
        if (self._writer is not None):
            self._writer.dispose()
            self._writer = None
            self._handler = None
            super().dispose()

    @staticmethod
    def createINIWriter(wWriter):
        return com_sdtk_table_KeyValueWriter(com_sdtk_table_INIHandler.instance,wWriter)

    @staticmethod
    def createJSONWriter(wWriter):
        return com_sdtk_table_KeyValueWriter(com_sdtk_table_JSONHandler.instance,wWriter)

    @staticmethod
    def createPropertiesWriter(wWriter):
        return com_sdtk_table_KeyValueWriter(com_sdtk_table_PropertiesHandler.instance,wWriter)

    @staticmethod
    def createSplunkWriter(wWriter):
        return com_sdtk_table_KeyValueWriter(com_sdtk_table_SplunkHandler.instance,wWriter)


class com_sdtk_table_MatrixInfo:

    def __init__(self):
        self._currentRow = None
        self._headersFlatten = None
        self._headers = None
        self._columnList = None
        self._headerRows = None
        self._headerColumns = None
        self._currentI = 0


class com_sdtk_table_MatrixReader(com_sdtk_table_DataTableReaderDecorator):

    def __init__(self,reader,headerColumns,headerRows,columnList):
        self._info = com_sdtk_table_MatrixInfo()
        super().__init__(reader)
        self._info._headerColumns = headerColumns
        self._info._headerRows = headerRows
        self._info._columnList = columnList
        self._info._headers = list()
        _this = self._info._headers
        l = len(_this)
        if (l < headerColumns):
            idx = (headerColumns - 1)
            v = None
            l1 = len(_this)
            while (l1 < idx):
                _this.append(None)
                l1 = (l1 + 1)
            if (l1 == idx):
                _this.append(v)
            else:
                _this[idx] = v
        elif (l > headerColumns):
            pos = headerColumns
            _hx_len = (l - headerColumns)
            if (pos < 0):
                pos = (len(_this) + pos)
            if (pos < 0):
                pos = 0
            res = _this[pos:(pos + _hx_len)]
            del _this[pos:(pos + _hx_len)]
        reader.noHeaderIncluded(True)
        if (headerRows > 0):
            i = 0
            while (i < headerRows):
                rowBuffer = list()
                python_internal_ArrayImpl._set(self._info._headers, i, rowBuffer)
                rowReader = reader.next()
                rowReader.start()
                while rowReader.hasNext():
                    x = rowReader.next()
                    rowBuffer.append(x)
                i = (i + 1)
            self._info._headersFlatten = list()
            i = 0
            while (i < len(python_internal_ArrayImpl._get(self._info._headers, 0))):
                j = 0
                while (j < headerRows):
                    _this = self._info._headersFlatten
                    x = python_internal_ArrayImpl._get(python_internal_ArrayImpl._get(self._info._headers, j), i)
                    _this.append(x)
                    j = (j + 1)
                i = (i + 1)

    def dispose(self):
        self._info = None
        super().dispose()

    def nextReuse(self,rowReader):
        reader = None
        if (self._info._currentI == 0):
            reader = self._reader.next()
        else:
            reader = self._reader.value()
        if (rowReader is None):
            rowReader = com_sdtk_table_MatrixRowReader(self._info,reader)
        else:
            rr = rowReader
            rr.reuse(reader)
        self.incrementTo(None,rowReader,self._reader.rawIndex())
        return rowReader

    def next(self):
        return self.nextReuse(None)

    def skipRows(self,rows):
        pass

    @staticmethod
    def createMatrixReader(reader,headerColumns,headerRows,columnList):
        return com_sdtk_table_MatrixReader(reader,headerColumns,headerRows,columnList)


class com_sdtk_table_MatrixRowReader(com_sdtk_table_DataTableRowReaderDecorator):

    def __init__(self,info,reader):
        self._info = None
        super().__init__(reader)
        self._info = info
        self._started = False

    def reuse(self,reader):
        super().reuse(reader)
        self._started = False

    def next(self):
        current = None
        name = None
        i = (self.index() + 1)
        j = (i - len(self._info._currentRow))
        if (j < 0):
            current = python_internal_ArrayImpl._get(self._info._currentRow, i)
        elif (j < len(self._info._headers)):
            current = python_internal_ArrayImpl._get(python_internal_ArrayImpl._get(self._info._headers, j), (self._info._currentI + self._info._headerColumns))
        elif (j == len(self._info._headers)):
            current = self._reader.next()
            _hx_local_0 = self._info
            _hx_local_1 = _hx_local_0._currentI
            _hx_local_0._currentI = (_hx_local_1 + 1)
            _hx_local_1
            if (not self._reader.hasNext()):
                self._info._currentI = 0
        if ((self._info._columnList is not None) and ((i < len(self._info._columnList)))):
            name = python_internal_ArrayImpl._get(self._info._columnList, i)
        else:
            name = None
        self.incrementTo(name,current,self._reader.rawIndex())
        return current

    def hasNext(self):
        i = (self.index() + 1)
        j = (i - len(self._info._currentRow))
        return (j <= len(self._info._headers))

    def start(self):
        if (not self._started):
            self._started = True
            if (self._info._currentI == 0):
                super().start()
                i = 0
                if (self._info._currentRow is None):
                    self._info._currentRow = list()
                    _this = self._info._currentRow
                    _hx_len = self._info._headerColumns
                    l = len(_this)
                    if (l < _hx_len):
                        idx = (_hx_len - 1)
                        v = None
                        l1 = len(_this)
                        while (l1 < idx):
                            _this.append(None)
                            l1 = (l1 + 1)
                        if (l1 == idx):
                            _this.append(v)
                        else:
                            _this[idx] = v
                    elif (l > _hx_len):
                        pos = _hx_len
                        len1 = (l - _hx_len)
                        if (pos < 0):
                            pos = (len(_this) + pos)
                        if (pos < 0):
                            pos = 0
                        res = _this[pos:(pos + len1)]
                        del _this[pos:(pos + len1)]
                while (i < self._info._headerColumns):
                    python_internal_ArrayImpl._set(self._info._currentRow, i, self._reader.next())
                    i = (i + 1)

    def name(self):
        return self._name

    def value(self):
        return self._value

    def index(self):
        return self._index


class com_sdtk_table_NullRowWriter(com_sdtk_table_DataTableRowWriter):

    def __init__(self):
        super().__init__()


class com_sdtk_table_PSVInfo:

    def __init__(self):
        pass

    def fileStart(self):
        return ""

    def fileEnd(self):
        return ""

    def delimiter(self):
        return "|"

    def rowDelimiter(self):
        return "\n"

    def boolStart(self):
        return ""

    def boolEnd(self):
        return ""

    def stringStart(self):
        return "\""

    def stringEnd(self):
        return "\""

    def intStart(self):
        return ""

    def intEnd(self):
        return ""

    def floatStart(self):
        return ""

    def floatEnd(self):
        return ""

    def replacements(self):
        return ["\\\\", "\\", "\\\n", "\n", "\\\t", "\t", "\\\r", "\r"]

    def replacementIndicator(self):
        return "\\"

    def widthMinimum(self):
        return -1

    def widthMaximum(self):
        return -1


class com_sdtk_table_Parameters(com_sdtk_std_Parameters):

    def __init__(self):
        self._sortRowsBy = None
        self._filterColumnsInclude = None
        self._filterRowsInclude = None
        self._filterColumnsExclude = None
        self._filterRowsExclude = None
        self._input = None
        self._output = None
        self._outputOptions = None
        self._inputOptions = None
        self._rightTrim = False
        self._leftTrim = False
        self._recordPass = False
        self._verbose = False
        self._runInTestMode = False
        super().__init__()
        i = 0
        sParameter = None
        sLocations = list()
        while True:
            sParameter = self.getParameter(i)
            if (sParameter is not None):
                _g = sParameter.upper()
                _hx_local_0 = len(_g)
                if (_hx_local_0 == 15):
                    if (_g == "CREATEORREPLACE"):
                        self._outputOptions = com_sdtk_table_Parameters.setValue(self._outputOptions,"sqlType","CreateOrReplace")
                        i = (i + 1)
                        self._outputOptions = com_sdtk_table_Parameters.setValue(self._outputOptions,"tableName",self.getParameter(i))
                    else:
                        sLocations.append(sParameter)
                elif (_hx_local_0 == 10):
                    if (_g == "RECORDPASS"):
                        self._recordPass = True
                    else:
                        sLocations.append(sParameter)
                elif (_hx_local_0 == 11):
                    if (_g == "EXCLUDEROWS"):
                        i = (i + 1)
                        self._filterRowsExclude = self.getParameter(i)
                    elif (_g == "INCLUDEROWS"):
                        i = (i + 1)
                        self._filterRowsInclude = self.getParameter(i)
                    else:
                        sLocations.append(sParameter)
                elif (_hx_local_0 == 9):
                    if (_g == "RIGHTTRIM"):
                        self._rightTrim = True
                    else:
                        sLocations.append(sParameter)
                elif (_hx_local_0 == 4):
                    if (_g == "TRIM"):
                        self._leftTrim = True
                        self._rightTrim = True
                    else:
                        sLocations.append(sParameter)
                elif (_hx_local_0 == 13):
                    if (_g == "EXCLUDEHEADER"):
                        if (len(sLocations) == 1):
                            self._inputOptions = com_sdtk_table_Parameters.setValue(self._inputOptions,"header",False)
                        elif (len(sLocations) == 2):
                            self._outputOptions = com_sdtk_table_Parameters.setValue(self._outputOptions,"header",False)
                    else:
                        sLocations.append(sParameter)
                elif (_hx_local_0 == 7):
                    if (_g == "ORDERBY"):
                        i = (i + 1)
                        self._sortRowsBy = self.getParameter(i)
                    elif (_g == "PROFILE"):
                        com_sdtk_table_Stopwatch.setDefaultActual(True)
                    elif (_g == "RUNTIME"):
                        com_sdtk_table_Stopwatch.setActual("Converter")
                    elif (_g == "VERBOSE"):
                        self._verbose = True
                    elif (_g == "VERSION"):
                        self.printVersion()
                    else:
                        sLocations.append(sParameter)
                elif (_hx_local_0 == 8):
                    if (_g == "LEFTTRIM"):
                        self._leftTrim = True
                    elif (_g == "RUNTESTS"):
                        self._runInTestMode = True
                    elif (_g == "TEXTONLY"):
                        if (len(sLocations) == 1):
                            self._inputOptions = com_sdtk_table_Parameters.setValue(self._inputOptions,"textOnly",True)
                        elif (len(sLocations) == 2):
                            self._outputOptions = com_sdtk_table_Parameters.setValue(self._outputOptions,"textOnly",True)
                    else:
                        sLocations.append(sParameter)
                elif (_hx_local_0 == 14):
                    if (_g == "EXCLUDECOLUMNS"):
                        i = (i + 1)
                        self._filterColumnsExclude = self.getParameter(i)
                    elif (_g == "INCLUDECOLUMNS"):
                        i = (i + 1)
                        self._filterColumnsInclude = self.getParameter(i)
                    else:
                        sLocations.append(sParameter)
                elif (_hx_local_0 == 6):
                    if (_g == "CREATE"):
                        self._outputOptions = com_sdtk_table_Parameters.setValue(self._outputOptions,"sqlType","Create")
                        i = (i + 1)
                        self._outputOptions = com_sdtk_table_Parameters.setValue(self._outputOptions,"tableName",self.getParameter(i))
                    elif (_g == "INSERT"):
                        self._outputOptions = com_sdtk_table_Parameters.setValue(self._outputOptions,"sqlType","Insert")
                        i = (i + 1)
                        self._outputOptions = com_sdtk_table_Parameters.setValue(self._outputOptions,"tableName",self.getParameter(i))
                    else:
                        sLocations.append(sParameter)
                else:
                    sLocations.append(sParameter)
            i = (i + 1)
            if (sParameter is None):
                break
        _g = len(sLocations)
        if (_g == 0):
            pass
        elif (_g == 1):
            self.setInput((sLocations[0] if 0 < len(sLocations) else None))
        elif (_g == 2):
            self.setInput((sLocations[0] if 0 < len(sLocations) else None))
            self.setOutput((sLocations[1] if 1 < len(sLocations) else None))
        else:
            raise haxe_Exception.thrown("More than two files specified.  This indicates that the tool was run improperly.")

    def fullPrint(self):
        self.printName()
        self.printVersion()
        self.printDetails()

    def printName(self):
        _hx_str = "Simple Data Toolkit - Simple Table Converter"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))

    def printVersion(self):
        _hx_str = Std.string(("Version " + HxOverrides.stringOrNull(com_sdtk_std_Version.get())))
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))

    def printDetails(self):
        _hx_str = "Copyright (C) 2019 Vis LLC - All Rights Reserved"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = ""
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "Project Home - https://sourceforge.net/projects/simple-data-toolkit/"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = ""
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "This program is free software: you can redistribute it and/or modify"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "it under the terms of the GNU Lesser General Public License as published by"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "the Free Software Foundation, either version 3 of the License, or"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "(at your option) any later version."
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = ""
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "This program is distributed in the hope that it will be useful,"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "but WITHOUT ANY WARRANTY; without even the implied warranty of"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "GNU General Public License for more details."
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = ""
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "You should have received a copy of the GNU Lesser General Public License"
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))
        _hx_str = "along with this program.  If not, see <https://www.gnu.org/licenses/>."
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))

    def print(self,s):
        _hx_str = Std.string(s)
        python_Lib.printString((("" + ("null" if _hx_str is None else _hx_str)) + HxOverrides.stringOrNull(python_Lib.lineEnd)))

    def getType(self,sLocation):
        startIndex = None
        iDot = (sLocation.find(".") if ((startIndex is None)) else HxString.indexOfImpl(sLocation,".",startIndex))
        startIndex = None
        iHash = (sLocation.find("#") if ((startIndex is None)) else HxString.indexOfImpl(sLocation,"#",startIndex))
        if ((iDot == 0) or ((iHash == 0))):
            return 0
        elif (iDot > 0):
            return 1
        else:
            return -1

    def setInput(self,sLocation):
        _g = self.getType(sLocation)
        if (_g == 0):
            self._input = sLocation
        elif (_g == 1):
            self._input = sLocation
        else:
            pass

    def setOutput(self,sLocation):
        _g = self.getType(sLocation)
        if (_g == 0):
            self._output = sLocation
        elif (_g == 1):
            self._output = sLocation
        else:
            pass

    def getRunInTestMode(self):
        return self._runInTestMode

    def getRecordPass(self):
        return self._recordPass

    def getVerbose(self):
        return self._verbose

    def getOutput(self):
        return self._output

    def getInput(self):
        return self._input

    def getOutputFormat(self):
        return com_sdtk_table_Parameters.getFormat(self.getOutput())

    def getInputFormat(self):
        return com_sdtk_table_Parameters.getFormat(self.getInput())

    def getFilterRowsExclude(self):
        return self._filterRowsExclude

    def getFilterRowsInclude(self):
        return self._filterRowsInclude

    def getFilterColumnsExclude(self):
        return self._filterColumnsExclude

    def getFilterColumnsInclude(self):
        return self._filterColumnsInclude

    def getSortRowsBy(self):
        return self._sortRowsBy

    def getLeftTrim(self):
        return self._leftTrim

    def getRightTrim(self):
        return self._rightTrim

    def getInputOptions(self):
        return self._inputOptions

    def getOutputOptions(self):
        return self._outputOptions

    @staticmethod
    def setValue(options,key,value):
        if (options is None):
            options = haxe_ds_StringMap()
        options.h[key] = value
        return options

    @staticmethod
    def endsWith(s,t):
        s1 = len(s)
        startIndex = None
        tmp = None
        if (startIndex is None):
            tmp = s.rfind(t, 0, len(s))
        elif (t == ""):
            length = len(s)
            if (startIndex < 0):
                startIndex = (length + startIndex)
                if (startIndex < 0):
                    startIndex = 0
            tmp = (length if ((startIndex > length)) else startIndex)
        else:
            i = s.rfind(t, 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len(t))) if ((i == -1)) else (i + 1))
            check = s.find(t, startLeft, len(s))
            tmp = (check if (((check > i) and ((check <= startIndex)))) else i)
        return ((s1 - tmp) == len(t))

    @staticmethod
    def getFormat(sName):
        if ((sName is None) or ((len(sName) <= 0))):
            return com_sdtk_table_Format.CSV
        sName = sName.lower()
        startIndex = None
        pos = None
        if (startIndex is None):
            pos = sName.rfind(".", 0, len(sName))
        else:
            i = sName.rfind(".", 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len("."))) if ((i == -1)) else (i + 1))
            check = sName.find(".", startLeft, len(sName))
            pos = (check if (((check > i) and ((check <= startIndex)))) else i)
        _g = HxString.substr(sName,pos,None)
        _hx_local_0 = len(_g)
        if (_hx_local_0 == 11):
            if (_g == ".properties"):
                return com_sdtk_table_Format.PROPERTIES
            else:
                return None
        elif (_hx_local_0 == 4):
            if (_g == ".csv"):
                return com_sdtk_table_Format.CSV
            elif (_g == ".ini"):
                return com_sdtk_table_Format.INI
            elif (_g == ".psv"):
                return com_sdtk_table_Format.PSV
            elif (_g == ".sql"):
                return com_sdtk_table_Format.SQL
            elif (_g == ".tex"):
                return com_sdtk_table_Format.TEX
            elif (_g == ".tsv"):
                return com_sdtk_table_Format.TSV
            elif (_g == ".txt"):
                return com_sdtk_table_Format.RAW
            else:
                return None
        elif (_hx_local_0 == 5):
            if (_g == ".html"):
                return com_sdtk_table_Format.HTMLTable
            elif (_g == ".java"):
                return com_sdtk_table_Format.Java
            elif (_g == ".json"):
                return com_sdtk_table_Format.JSON
            else:
                return None
        elif (_hx_local_0 == 3):
            if (_g == ".cs"):
                return com_sdtk_table_Format.CSharp
            elif (_g == ".hx"):
                return com_sdtk_table_Format.Haxe
            elif (_g == ".py"):
                return com_sdtk_table_Format.Python
            else:
                return None
        else:
            return None


class com_sdtk_table_PropertiesHandler:

    def __init__(self):
        pass

    def favorReadAll(self):
        return True

    def oneRowPerFile(self):
        return True

    def read(self,rReader):
        rReader = rReader.switchToLineReader()
        mMap = haxe_ds_StringMap()
        while rReader.hasNext():
            sLine = rReader.peek()
            sFirst = ("" if ((0 >= len(sLine))) else sLine[0])
            if ((sFirst == "!") or ((sFirst == "#"))):
                rReader.next()
                continue
            else:
                startIndex = None
                iIndex1 = (sLine.find("=") if ((startIndex is None)) else HxString.indexOfImpl(sLine,"=",startIndex))
                startIndex1 = None
                iIndex2 = (sLine.find(":") if ((startIndex1 is None)) else HxString.indexOfImpl(sLine,":",startIndex1))
                iIndexFinal = (iIndex2 if ((iIndex1 < 0)) else (iIndex1 if ((iIndex2 < 0)) else (iIndex1 if ((iIndex1 < iIndex2)) else iIndex2)))
                key = com_sdtk_table_PropertiesHandler.convertFrom(StringTools.trim(HxString.substr(sLine,0,iIndexFinal)),None)
                value = com_sdtk_table_PropertiesHandler.convertFrom(StringTools.ltrim(HxString.substr(sLine,(iIndexFinal + 1),None)),rReader)
                mMap.h[key] = value
                rReader.next()
        return mMap

    def write(self,wWriter,mMap):
        wWriter = wWriter.switchToLineWriter()
        key = mMap.keys()
        while key.hasNext():
            key1 = key.next()
            value = mMap.h.get(key1,None)
            wWriter.write((((HxOverrides.stringOrNull(com_sdtk_table_PropertiesHandler.convertTo(key1)) + "=") + HxOverrides.stringOrNull(com_sdtk_table_PropertiesHandler.convertTo(Std.string(value)))) + "\n"))

    def readAll(self,rReader,aMaps,aNames):
        x = self.read(rReader)
        aMaps.append(x)
        aNames.append("")

    def writeAll(self,wWriter,aMaps,aNames):
        self.write(wWriter,(aMaps[0] if 0 < len(aMaps) else None))

    @staticmethod
    def convertFrom(sValue,rReader):
        sValue = StringTools.replace(sValue,"\\\\","\\")
        sValue = StringTools.replace(sValue,"\\ "," ")
        if (rReader is not None):
            while sValue.endswith("\\"):
                sValue = HxString.substr(sValue,0,(len(sValue) - 1))
                if rReader.hasNext():
                    rReader.next()
                    sValue = (("null" if sValue is None else sValue) + HxOverrides.stringOrNull(rReader.peek()))
                else:
                    break
        if sValue.endswith("\n"):
            sValue = HxString.substr(sValue,0,(len(sValue) - 1))
        return sValue

    @staticmethod
    def convertTo(sValue):
        sValue = StringTools.replace(sValue,"\\","\\\\")
        sValue = StringTools.replace(sValue," ","\\ ")
        sValue = StringTools.replace(sValue,"\n","\\\n")
        return sValue


class com_sdtk_table_PythonInfoAbstract:

    def __init__(self):
        pass

    def start(self):
        return ""

    def end(self):
        return ""

    def arrayStart(self):
        return "["

    def arrayEnd(self):
        return "]"

    def mapStart(self):
        return "{"

    def mapEnd(self):
        return "}"

    def rowStart(self,name,index):
        return ""

    def rowEnd(self):
        return ""

    def betweenRows(self):
        return ","

    def mapRowEnd(self):
        return "}"

    def arrayRowEnd(self):
        return ""

    def arrayRowStart(self,name,index):
        return ""

    def mapRowStart(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("\"" + ("null" if name is None else name)) + "\": ")
        else:
            return (Std.string(index) + ": ")

    def mapIntEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return ((("\"" + ("null" if name is None else name)) + "\": ") + Std.string(data))
        else:
            return ((Std.string(index) + ": ") + Std.string(data))

    def mapBoolEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return ((("\"" + ("null" if name is None else name)) + "\": ") + Std.string(data))
        else:
            return ((Std.string(index) + ": ") + Std.string(data))

    def mapFloatEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return ((("\"" + ("null" if name is None else name)) + "\": ") + Std.string(data))
        else:
            return ((Std.string(index) + ": ") + Std.string(data))

    def mapOtherEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("\"" + ("null" if name is None else name)) + "\": \"") + ("null" if data is None else data)) + "\"")
        else:
            return (((Std.string(index) + ": \"") + ("null" if data is None else data)) + "\"")

    def mapNullEntry(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("\"" + ("null" if name is None else name)) + "\": None")
        else:
            return (Std.string(index) + ": None")

    def arrayIntEntry(self,data,name,index):
        return Std.string(data)

    def arrayBoolEntry(self,data,name,index):
        return Std.string(data)

    def arrayFloatEntry(self,data,name,index):
        return Std.string(data)

    def arrayOtherEntry(self,data,name,index):
        return (("\"" + ("null" if data is None else data)) + "\"")

    def arrayNullEntry(self,name,index):
        return "None"

    def intEntry(self,data,name,index):
        return None

    def boolEntry(self,data,name,index):
        return None

    def floatEntry(self,data,name,index):
        return None

    def otherEntry(self,data,name,index):
        return None

    def nullEntry(self,name,index):
        return None

    def betweenEntries(self):
        return ","

    def replacements(self):
        return ["\\\"", "\"", "\\\n", "\n", "\\\t", "\t"]


class com_sdtk_table_PythonInfoArrayOfArrays(com_sdtk_table_PythonInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.arrayStart()

    def end(self):
        return self.arrayEnd()

    def rowEnd(self):
        return self.arrayEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.arrayRowStart(name,index)) + HxOverrides.stringOrNull(self.arrayStart()))

    def intEntry(self,data,name,index):
        return self.arrayIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.arrayBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.arrayFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.arrayOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.arrayNullEntry(name,index)


class com_sdtk_table_PythonInfoArrayOfMaps(com_sdtk_table_PythonInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.arrayStart()

    def end(self):
        return self.arrayEnd()

    def rowEnd(self):
        return self.mapEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.arrayRowStart(name,index)) + HxOverrides.stringOrNull(self.mapStart()))

    def intEntry(self,data,name,index):
        return self.mapIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntry(name,index)


class com_sdtk_table_PythonInfoMapOfArrays(com_sdtk_table_PythonInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.mapStart()

    def end(self):
        return self.mapEnd()

    def rowEnd(self):
        return self.arrayEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.mapRowStart(name,index)) + HxOverrides.stringOrNull(self.arrayStart()))

    def intEntry(self,data,name,index):
        return self.arrayIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.arrayBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.arrayFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.arrayOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.arrayNullEntry(name,index)


class com_sdtk_table_PythonInfoMapOfMaps(com_sdtk_table_PythonInfoAbstract):

    def __init__(self):
        super().__init__()

    def start(self):
        return self.mapStart()

    def end(self):
        return self.mapEnd()

    def rowEnd(self):
        return self.mapEnd()

    def rowStart(self,name,index):
        return (HxOverrides.stringOrNull(self.mapRowStart(name,index)) + HxOverrides.stringOrNull(self.mapStart()))

    def intEntry(self,data,name,index):
        return self.mapIntEntry(data,name,index)

    def boolEntry(self,data,name,index):
        return self.mapBoolEntry(data,name,index)

    def floatEntry(self,data,name,index):
        return self.mapFloatEntry(data,name,index)

    def otherEntry(self,data,name,index):
        return self.mapOtherEntry(data,name,index)

    def nullEntry(self,name,index):
        return self.mapNullEntry(name,index)


class com_sdtk_table_RAWInfo:

    def __init__(self):
        pass

    def fileStart(self):
        return ""

    def fileEnd(self):
        return ""

    def delimiter(self):
        return ""

    def rowDelimiter(self):
        return "\n"

    def boolStart(self):
        return ""

    def boolEnd(self):
        return ""

    def stringStart(self):
        return ""

    def stringEnd(self):
        return ""

    def intStart(self):
        return ""

    def intEnd(self):
        return ""

    def floatStart(self):
        return ""

    def floatEnd(self):
        return ""

    def replacements(self):
        return []

    def replacementIndicator(self):
        return None

    def widthMinimum(self):
        return 1

    def widthMaximum(self):
        return 1


class com_sdtk_table_RowFilterDataTableReader(com_sdtk_table_DataTableReader):

    def __init__(self,dtrReader,fFilter):
        self._buffer2 = None
        self._bufferReaderPrevious = None
        self._bufferReader = None
        self._buffer = None
        self._reader = None
        self._filter = None
        self._switch = 0
        super().__init__()
        self._filter = fFilter
        self._reader = dtrReader
        self._buffer = list()
        self._buffer2 = list()

    def startI(self):
        self._reader.start()
        self.check(True)

    def check(self,reuse):
        rowReader = self._reader.next()
        if (rowReader is not None):
            self._bufferReader = None
            while ((rowReader is not None) and ((self._bufferReader is None))):
                rowReader.start()
                row = rowReader.next()
                if (self._filter.filter(row) is not None):
                    buffer = None
                    if (self._switch == 0):
                        buffer = self._buffer
                    else:
                        buffer = self._buffer2
                    while (len(buffer) > 0):
                        if (len(buffer) != 0):
                            buffer.pop()
                    buffer.append(row)
                    while rowReader.hasNext():
                        x = rowReader.next()
                        buffer.append(x)
                    if (reuse or ((self._bufferReaderPrevious is None))):
                        self._bufferReader = com_sdtk_table_ArrayRowReader.readWholeArrayReuse(buffer,self._bufferReaderPrevious)
                    else:
                        self._bufferReader = com_sdtk_table_ArrayRowReader.readWholeArray(buffer)
                else:
                    while rowReader.hasNext():
                        rowReader.next()
                    rowReader = self._reader.next()
        else:
            self._bufferReader = None
            self.dispose()

    def dispose(self):
        if (self._reader is not None):
            super().dispose()
            self._filter = None
            self._reader = None
            self._buffer = None
            self._bufferReader = None
            self._bufferReaderPrevious = None

    def hasNext(self):
        return (self._buffer is not None)

    def nextI(self,reuse):
        current = self._bufferReader
        if (self._switch == 0):
            self._switch = 122
        else:
            self._switch = 0
        self.incrementTo(self._reader.name(),current,self._reader.rawIndex())
        self.check(reuse)
        self._bufferReaderPrevious = current
        return current

    def nextReuse(self,rowReader):
        return self.nextI(True)

    def next(self):
        return self.nextI(False)

    def isAutoNamed(self):
        return self._reader.isAutoNamed()

    def isNameIndex(self):
        return self._reader.isNameIndex()

    def headerRowNotIncluded(self):
        return self._reader.headerRowNotIncluded()

    def reset(self):
        self._reader.reset()


class com_sdtk_table_SQLSelectInfo:

    def __init__(self):
        self._appendEnd = ""
        self._appendBeginning = ""

    def start(self):
        return self._appendBeginning

    def end(self):
        return self._appendEnd

    def rowStart(self,name,index):
        return "SELECT "

    def betweenRows(self):
        return "\nUNION ALL\n"

    def rowEnd(self):
        return "\nFROM dual"

    def intEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((Std.string(data) + " AS \"") + ("null" if name is None else name)) + "\"")
        else:
            return Std.string(data)

    def boolEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((Std.string(data) + " AS \"") + ("null" if name is None else name)) + "\"")
        else:
            return Std.string(data)

    def floatEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((Std.string(data) + " AS \"") + ("null" if name is None else name)) + "\"")
        else:
            return Std.string(data)

    def otherEntry(self,data,name,index):
        if ((name is not None) and ((name != ""))):
            return (((("'" + ("null" if data is None else data)) + "' AS \"") + ("null" if name is None else name)) + "\"")
        else:
            return (("'" + ("null" if data is None else data)) + "'")

    def nullEntry(self,name,index):
        if ((name is not None) and ((name != ""))):
            return (("null AS \"" + ("null" if name is None else name)) + "\"")
        else:
            return "null"

    def betweenEntries(self):
        return ","

    def replacements(self):
        return ["''", "'"]

    @staticmethod
    def createTable(name):
        info = com_sdtk_table_SQLSelectInfo()
        info._appendBeginning = (("CREATE TABLE " + ("null" if name is None else name)) + " AS\n")
        info._appendEnd = ";"
        return info

    @staticmethod
    def createOrReplaceTable(name):
        info = com_sdtk_table_SQLSelectInfo()
        info._appendBeginning = (("CREATE OR REPLACE TABLE " + ("null" if name is None else name)) + " AS\n")
        info._appendEnd = ";"
        return info

    @staticmethod
    def insertIntoTable(name):
        info = com_sdtk_table_SQLSelectInfo()
        info._appendBeginning = (("INSERT INTO " + ("null" if name is None else name)) + "\n")
        info._appendEnd = ";"
        return info


class com_sdtk_table_SplunkHandler:

    def __init__(self):
        pass

    def favorReadAll(self):
        return True

    def oneRowPerFile(self):
        return False

    def read(self,rReader):
        i = 0
        rReader = rReader.switchToLineReader()
        mMap = haxe_ds_StringMap()
        _this = rReader.next()
        sLine = _this.split(" ")
        _g = 0
        while (_g < len(sLine)):
            sPart = (sLine[_g] if _g >= 0 and _g < len(sLine) else None)
            _g = (_g + 1)
            startIndex = None
            iIndex = (sPart.find("=") if ((startIndex is None)) else HxString.indexOfImpl(sPart,"=",startIndex))
            if (iIndex > 0):
                sKey = HxString.substr(sPart,0,iIndex)
                sValue = HxString.substr(sPart,(iIndex + 1),None)
                mMap.h[sKey] = sValue
            else:
                key = Std.string(i)
                mMap.h[key] = sPart
        return mMap

    def write(self,wWriter,mMap):
        sbStart_b = python_lib_io_StringIO()
        sbBuffer = StringBuf()
        wWriter = wWriter.switchToLineWriter()
        key = mMap.keys()
        while key.hasNext():
            key1 = key.next()
            value = mMap.h.get(key1,None)
            if (Std.parseInt(key1) is not None):
                sbStart_b.write(Std.string(value))
                sbStart_b.write(" ")
            else:
                s = Std.string(key1)
                sbBuffer.b.write(s)
                sbBuffer.b.write("=")
                s1 = Std.string(com_sdtk_table_SplunkHandler.convertTo(Std.string(value)))
                sbBuffer.b.write(s1)
                sbBuffer.b.write(" ")
        sbStart_b.write(Std.string(sbBuffer))
        sbStart_b.write("\n")
        wWriter.write(sbStart_b.getvalue())

    def readAll(self,rReader,aMaps,aNames):
        rReader = rReader.switchToLineReader()
        while rReader.hasNext():
            x = self.read(rReader)
            aMaps.append(x)
            aNames.append("")

    def writeAll(self,wWriter,aMaps,aNames):
        i = 0
        wWriter = wWriter.switchToLineWriter()
        while (i < len(aMaps)):
            aMaps1 = i
            i = (i + 1)
            self.write(wWriter,(aMaps[aMaps1] if aMaps1 >= 0 and aMaps1 < len(aMaps) else None))

    @staticmethod
    def convertTo(sValue):
        sValue = StringTools.replace(sValue," ","")
        sValue = StringTools.replace(sValue,"\t","")
        sValue = StringTools.replace(sValue,"\n","")
        sValue = StringTools.replace(sValue,"\r","")
        return sValue


class com_sdtk_table_TableInfo:
    pass


class com_sdtk_table_StandardTableInfo:

    def __init__(self):
        pass

    def Tag(self):
        return ["table"]

    def HeaderRow(self):
        return ["tr"]

    def HeaderCell(self):
        return ["th", "td"]

    def Row(self):
        return ["tr"]

    def Cell(self):
        return ["td"]

    def RowNumber(self,i,e):
        pass

    def RowName(self,i,e):
        pass

    def ColumnNumber(self,i,e):
        pass

    def ColumnName(self,i,e):
        pass

    def setData(self,data,e):
        pass

    def FormatTableStart(self,writer):
        writer.write("<")
        writer.write(python_internal_ArrayImpl._get(self.Tag(), 0))
        writer.write(">")

    def FormatTableEnd(self,writer):
        writer.write("</")
        writer.write(python_internal_ArrayImpl._get(self.Tag(), 0))
        writer.write(">")

    def FormatRowStart(self,writer,header,i,n,rowCache,globalCache):
        writer.write("<")
        writer.write((python_internal_ArrayImpl._get(self.HeaderRow(), 0) if header else python_internal_ArrayImpl._get(self.Row(), 0)))
        writer.write(" RowNumber=")
        writer.write(Std.string(i))
        writer.write(" RowName=\"")
        writer.write(self.replacementName(n,rowCache))
        writer.write("\">")

    def FormatRowEnd(self,writer,header):
        writer.write("</")
        writer.write((python_internal_ArrayImpl._get(self.HeaderRow(), 0) if header else python_internal_ArrayImpl._get(self.Row(), 0)))
        writer.write(">")

    def FormatCell(self,writer,header,c,cn,r,rn,data,rowCache,globalCache):
        writer.write("<")
        writer.write((python_internal_ArrayImpl._get(self.HeaderCell(), 0) if header else python_internal_ArrayImpl._get(self.Cell(), 0)))
        writer.write(" ColumnNumber=")
        writer.write(Std.string(c))
        writer.write(" ColumnName=\"")
        writer.write(self.replacementName(cn,globalCache))
        writer.write("\" RowNumber=")
        writer.write(Std.string(r))
        writer.write(" RowName=\"")
        writer.write(self.replacementName(rn,rowCache))
        writer.write("\">")
        writer.write(self.replacementData(Std.string(data)))
        writer.write("</")
        writer.write((python_internal_ArrayImpl._get(self.HeaderCell(), 0) if header else python_internal_ArrayImpl._get(self.Cell(), 0)))
        writer.write(">")

    def replacementsName(self):
        return ["&amp;", "&", "&lt;", "<", "&quot;", "\""]

    def replacementsData(self):
        return ["&amp;", "&", "&lt;", "<"]

    def replacementName(self,data,cache):
        if (data is None):
            return None
        result = cache.h.get(data,None)
        if (result is None):
            result = data
            replacements = self.replacementsName()
            if (((replacements is not None) and ((len(replacements) > 0))) and ((result is not None))):
                replaceI = 1
                while (replaceI < len(replacements)):
                    result = StringTools.replace(result,(replacements[replaceI] if replaceI >= 0 and replaceI < len(replacements) else None),python_internal_ArrayImpl._get(replacements, (replaceI - 1)))
                    replaceI = (replaceI + 2)
            cache.h[data] = result
        return result

    def replacementData(self,data):
        replacements = self.replacementsData()
        if (((replacements is not None) and ((len(replacements) > 0))) and ((data is not None))):
            replaceI = 1
            while (replaceI < len(replacements)):
                data = StringTools.replace(data,(replacements[replaceI] if replaceI >= 0 and replaceI < len(replacements) else None),python_internal_ArrayImpl._get(replacements, (replaceI - 1)))
                replaceI = (replaceI + 2)
        return data


class com_sdtk_table_TSVInfo:

    def __init__(self):
        pass

    def fileStart(self):
        return ""

    def fileEnd(self):
        return ""

    def delimiter(self):
        return "\t"

    def rowDelimiter(self):
        return "\n"

    def boolStart(self):
        return ""

    def boolEnd(self):
        return ""

    def stringStart(self):
        return "\""

    def stringEnd(self):
        return "\""

    def intStart(self):
        return ""

    def intEnd(self):
        return ""

    def floatStart(self):
        return ""

    def floatEnd(self):
        return ""

    def replacements(self):
        return ["\\\\", "\\", "\\\n", "\n", "\\\t", "\t", "\\\r", "\r"]

    def replacementIndicator(self):
        return "\\"

    def widthMinimum(self):
        return -1

    def widthMaximum(self):
        return -1


class com_sdtk_table_TableRowReaderI:
    pass


class com_sdtk_table_TableDataRowReaderI(com_sdtk_table_AbstractTableReader):

    def __init__(self,tdInfo,oElement):
        super().__init__(tdInfo,oElement)

    def elementCheck(self,oElement):
        return False

    def getValue(self,oElement):
        return None


class com_sdtk_table_TableFirstRowWriter(com_sdtk_table_AbstractTableRowWriter):

    def __init__(self,tdInfo,writer,sHeader):
        super().__init__(tdInfo,writer,sHeader)

    def write(self,data,name,index):
        _this = self._header
        _this.append(data)
        self._writer.writeCell(False,data,name,index)


class com_sdtk_table_TableHeaderRowReaderI(com_sdtk_table_AbstractTableReader):

    def __init__(self,tdInfo,oElement):
        super().__init__(tdInfo,oElement)

    def elementCheck(self,oElement):
        return False

    def getValue(self,oElement):
        return None


class com_sdtk_table_TableHeaderRowWriter(com_sdtk_table_AbstractTableRowWriter):

    def __init__(self,tdInfo,oElement,sHeader):
        super().__init__(tdInfo,oElement,sHeader)

    def write(self,data,name,index):
        self._writer.writeCell(True,data,name,index)


class com_sdtk_table_TableReader(com_sdtk_table_DataTableReader):

    def __init__(self,tdInfo,oElement):
        self._header = None
        self._reader = None
        super().__init__()
        self._reader = com_sdtk_table_TableReaderI(tdInfo,oElement)
        self._index = -1
        self._header = list()

    def hasNext(self):
        return self._reader.hasNext()

    def nextReuse(self,rowReader):
        if self._reader.hasNext():
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0._index
            _hx_local_0._index = (_hx_local_1 + 1)
            _hx_local_1
            self._name = self._reader.peek()
            if (rowReader is None):
                rowReader = com_sdtk_table_TableRowReader(self._reader.next(),self._header)
            else:
                rr = rowReader
                rr.reuse(self._reader.next(),self._header)
            self._value = rowReader
        else:
            self._value = None
            return None
        return rowReader

    def next(self):
        return self.nextReuse(None)

    def dispose(self):
        self._reader = None
        self._header = None

    def reset(self):
        pass

    @staticmethod
    def createStandardTableReader(oElement):
        return com_sdtk_table_TableReader(com_sdtk_table_StandardTableInfo.instance,oElement)


class com_sdtk_table_TableReaderI(com_sdtk_table_AbstractTableReader):

    def __init__(self,tdInfo,oElement):
        super().__init__(tdInfo,oElement)

    def elementCheck(self,oElement):
        return False

    def getValue(self,oElement):
        bHasHeader = False
        if bHasHeader:
            return com_sdtk_table_TableHeaderRowReaderI(self._info,oElement)
        else:
            return com_sdtk_table_TableDataRowReaderI(self._info,oElement)


class com_sdtk_table_TableRowReader(com_sdtk_table_DataTableRowReader):

    def __init__(self,trReader,aHeader):
        self._header = None
        self._isHeader = None
        self._reader = None
        super().__init__()
        self.reuse(trReader,aHeader)

    def reuse(self,trReader,aHeader):
        self._isHeader = (Type.getClass(trReader) == com_sdtk_table_TableHeaderRowReaderI)
        self._header = aHeader
        self._reader = trReader
        self._index = -1
        self._started = False
        self._value = None

    def hasNext(self):
        return self._reader.hasNext()

    def next(self):
        if self._reader.hasNext():
            _hx_local_0 = self
            _hx_local_1 = _hx_local_0._index
            _hx_local_0._index = (_hx_local_1 + 1)
            _hx_local_1
            if self._isHeader:
                self._name = self._reader.peek()
                _this = self._header
                x = self._name
                _this.append(x)
            else:
                self._name = python_internal_ArrayImpl._get(self._header, self._index)
            return self._reader.next()
        else:
            return None

    def dispose(self):
        self._reader = None
        self._header = None


class com_sdtk_table_TableRowWriter(com_sdtk_table_AbstractTableRowWriter):

    def __init__(self,tdInfo,writer,sHeader):
        super().__init__(tdInfo,writer,sHeader)

    def write(self,data,name,index):
        self._writer.writeCell(False,data,name,index)


class com_sdtk_table_TableWriter(com_sdtk_table_DataTableWriter):

    def __init__(self,tdInfo,oElement = None):
        self._rowName = None
        self._row = None
        self._info = None
        self._rowCache = haxe_ds_StringMap()
        self._globalCache = haxe_ds_StringMap()
        self._done = False
        self._header = list()
        super().__init__()
        self._info = tdInfo
        self._header = list()
        self._row = -1
        self._rowName = None

    def start(self):
        self.tableStart()

    def tableStart(self):
        pass

    def tableEnd(self):
        pass

    def tableRowStart(self,header,index,name):
        pass

    def tableRowEndI(self,header):
        pass

    def writeCell(self,header,data,name,index):
        pass

    def tableRowEnd(self):
        if (self._row > 1):
            self.tableRowEndI(False)
        elif (self._row == 0):
            self.tableRowEndI(True)

    def writeStartI(self,name,index,rowWriter):
        if (not self._done):
            self.tableRowEnd()
            self.tableRowStart((index == 0),index,name)
            self._row = index
            self._rowName = name
            index1 = index
            if (index1 == 0):
                rowWriter = com_sdtk_table_TableHeaderRowWriter(self._info,self,self._header)
            elif (index1 == 1):
                rowWriter = com_sdtk_table_TableFirstRowWriter(self._info,self,self._header)
            elif (index1 == 2):
                rowWriter = com_sdtk_table_TableRowWriter(self._info,self,self._header)
            elif (rowWriter is None):
                rowWriter = com_sdtk_table_TableRowWriter(self._info,self,self._header)
            else:
                rw = rowWriter
                rw.reuse(self._info,self,self._header)
            return rowWriter
        else:
            return None

    def disposeI(self):
        pass

    def dispose(self):
        if (not self._done):
            self.tableRowEnd()
            self.tableEnd()
            self.disposeI()
            self._header = None
            self._info = None
            self._row = -1
            self._rowName = None
            self._globalCache = None
            self._rowCache = None
            self._done = True

    @staticmethod
    def createStandardTableWriterForElement(oElement):
        return com_sdtk_table_TableWriterElement(com_sdtk_table_StandardTableInfo.instance,oElement)

    @staticmethod
    def createStandardTableWriterForWriter(wWriter):
        return com_sdtk_table_TableWriterString(com_sdtk_table_StandardTableInfo.instance,wWriter)


class com_sdtk_table_TableWriterString(com_sdtk_table_TableWriter):

    def __init__(self,tdInfo,writer):
        self._writer = None
        super().__init__(tdInfo)
        self._writer = writer

    def tableStart(self):
        if (not self._done):
            self._info.FormatTableStart(self._writer)

    def tableEnd(self):
        if (not self._done):
            self._info.FormatTableEnd(self._writer)

    def tableRowStart(self,header,index,name):
        if (not self._done):
            self._info.FormatRowStart(self._writer,header,index,name,self._rowCache,self._globalCache)

    def tableRowEndI(self,header):
        if (not self._done):
            self._info.FormatRowEnd(self._writer,header)
            self._rowCache = haxe_ds_StringMap()

    def disposeI(self):
        self._writer.dispose()
        self._writer = None

    def writeCell(self,header,data,name,index):
        if (not self._done):
            self._info.FormatCell(self._writer,header,index,name,self._row,self._rowName,data,self._rowCache,self._globalCache)

    def writeHeaderFirst(self):
        return True


class com_sdtk_table_TableWriterElement(com_sdtk_table_TableWriter):

    def __init__(self,tdInfo,oElement = None):
        self._tableElement = None
        self._element = None
        super().__init__(tdInfo)
        self._element = oElement

    def tableStart(self):
        pass

    def tableRowStart(self,header,index,name):
        oRow = None

    def writeHeader(self):
        self.tableRowStart(True,0,"")
        return com_sdtk_table_TableHeaderRowWriter(self._info,self,self._header)

    def disposeI(self):
        if (len(self._header) > 0):
            dtrwWriter = self.writeHeader()
            try:
                i = 0
                _g = 0
                _g1 = self._header
                while (_g < len(_g1)):
                    cell = (_g1[_g] if _g >= 0 and _g < len(_g1) else None)
                    _g = (_g + 1)
                    tmp = i
                    i = (i + 1)
                    dtrwWriter.write(cell,cell,tmp)
            except BaseException as _g:
                None
            dtrwWriter.dispose()
        self._element = None

    def writeCell(self,header,data,name,index):
        pass


class com_sdtk_table_TallyInfo:

    def __init__(self):
        self._entries = 0
        self._size = 0
        self._count = 0

    def add(self,iCount,iSize):
        _hx_local_0 = self
        _hx_local_1 = _hx_local_0._count
        _hx_local_0._count = (_hx_local_1 + iCount)
        _hx_local_0._count
        _hx_local_2 = self
        _hx_local_3 = _hx_local_2._size
        _hx_local_2._size = (_hx_local_3 + iSize)
        _hx_local_2._size
        _hx_local_4 = self
        _hx_local_5 = _hx_local_4._entries
        _hx_local_4._entries = (_hx_local_5 + 1)
        _hx_local_5

    def getNumberOfEntries(self):
        return self._entries

    def getFileSize(self):
        return self._size

    def getFileCount(self):
        return self._count

    def getFreeSpace(self):
        return -1


class com_sdtk_table_TeXInfo:

    def __init__(self):
        pass

    def fileStart(self):
        return "\\begin{tabular}"

    def fileEnd(self):
        return "\\end{tabular}"

    def delimiter(self):
        return "&"

    def rowDelimiter(self):
        return "\\\\\\hline"

    def boolStart(self):
        return ""

    def boolEnd(self):
        return ""

    def stringStart(self):
        return "\\makecell{"

    def stringEnd(self):
        return "}"

    def intStart(self):
        return ""

    def intEnd(self):
        return ""

    def floatStart(self):
        return ""

    def floatEnd(self):
        return ""

    def replacements(self):
        return ["\\\\", "\\", "\\\n", "\n", "\\\t", "\t", "\\\r", "\r"]

    def replacementIndicator(self):
        return "\\"

    def widthMinimum(self):
        return -1

    def widthMaximum(self):
        return -1


class com_sdtk_table_Tests:

    @staticmethod
    def runTests(recordPass,verbose):
        results = ""
        results = com_sdtk_table_Tests.addResult(results,com_sdtk_table_Tests.testCSVToPSV(recordPass,verbose))
        results = com_sdtk_table_Tests.addResult(results,com_sdtk_table_Tests.testExcludeColumns(recordPass,verbose))
        results = com_sdtk_table_Tests.addResult(results,com_sdtk_table_Tests.testExcludeRows(recordPass,verbose))
        results = com_sdtk_table_Tests.addResult(results,com_sdtk_table_Tests.testIncludeColumns(recordPass,verbose))
        results = com_sdtk_table_Tests.addResult(results,com_sdtk_table_Tests.testIncludeRows(recordPass,verbose))
        results = com_sdtk_table_Tests.addResult(results,com_sdtk_table_Tests.testOrderBy(recordPass,verbose))
        return results

    @staticmethod
    def addResult(sum,test):
        if (test is None):
            return sum
        else:
            return ((("null" if sum is None else sum) + ("null" if test is None else test)) + "\n")

    @staticmethod
    def compareResults(recordPass,verbose,sTest,sExpected,sGot):
        sGot = StringTools.trim(sGot)
        sExpected = StringTools.trim(sExpected)
        if (sGot != sExpected):
            if verbose:
                return ((((((((((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sEXPECTED)) + ":\n") + ("null" if sExpected is None else sExpected)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sGOT)) + ":\n") + ("null" if sGot is None else sGot))
            else:
                return ((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED))
        elif recordPass:
            if verbose:
                return ((((((((((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sPASSED)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sEXPECTED)) + ":\n") + ("null" if sExpected is None else sExpected)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sGOT)) + ":\n") + ("null" if sGot is None else sGot))
            else:
                return ((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sPASSED))
        else:
            return None

    @staticmethod
    def testCSVToPSV(recordPass,verbose):
        sTest = "testCSVToPSV"
        sPSV = StringTools.replace(com_sdtk_table_Tests.sCSV,",","|")
        sbBuffer = StringBuf()
        try:
            com_sdtk_table_Converter.convertWithOptions(com_sdtk_table_Tests.sCSV,com_sdtk_table_Format.CSV,sbBuffer,com_sdtk_table_Format.PSV,None,None,None,None,None,False,False,None,None)
            return com_sdtk_table_Tests.compareResults(recordPass,verbose,sTest,sPSV,StringTools.replace(sbBuffer.b.getvalue(),"\"",""))
        except BaseException as _g:
            None
            msg = haxe_Exception.caught(_g).unwrap()
            if verbose:
                return ((((((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sEXCEPTION)) + ":\n") + Std.string(msg))
            else:
                return ((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED))

    @staticmethod
    def testExcludeColumns(recordPass,verbose):
        sTest = "testExcludeColumns"
        sExcluded = "A,C\n5,7\n1,3\n8,5"
        sbBuffer = StringBuf()
        try:
            com_sdtk_table_Converter.convertWithOptions(com_sdtk_table_Tests.sCSV,com_sdtk_table_Format.CSV,sbBuffer,com_sdtk_table_Format.CSV,"B",None,None,None,None,False,False,None,None)
            return com_sdtk_table_Tests.compareResults(recordPass,verbose,sTest,sExcluded,StringTools.replace(sbBuffer.b.getvalue(),"\"",""))
        except BaseException as _g:
            None
            msg = haxe_Exception.caught(_g).unwrap()
            if verbose:
                return ((((((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sEXCEPTION)) + ":\n") + Std.string(msg))
            else:
                return ((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED))

    @staticmethod
    def testExcludeRows(recordPass,verbose):
        sTest = "testExcludeRows"
        sExcluded = "A,B,C\n1,2,3\n8,1,5"
        sbBuffer = StringBuf()
        try:
            com_sdtk_table_Converter.convertWithOptions(com_sdtk_table_Tests.sCSV,com_sdtk_table_Format.CSV,sbBuffer,com_sdtk_table_Format.CSV,None,None,"#2",None,None,False,False,None,None)
            return com_sdtk_table_Tests.compareResults(recordPass,verbose,sTest,sExcluded,StringTools.replace(sbBuffer.b.getvalue(),"\"",""))
        except BaseException as _g:
            None
            msg = haxe_Exception.caught(_g).unwrap()
            if verbose:
                return ((((((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sEXCEPTION)) + ":\n") + Std.string(msg))
            else:
                return ((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED))

    @staticmethod
    def testIncludeColumns(recordPass,verbose):
        sTest = "testIncludeColumns"
        sIncluded = "B\n6\n2\n1"
        sbBuffer = StringBuf()
        try:
            com_sdtk_table_Converter.convertWithOptions(com_sdtk_table_Tests.sCSV,com_sdtk_table_Format.CSV,sbBuffer,com_sdtk_table_Format.CSV,None,"B",None,None,None,False,False,None,None)
            return com_sdtk_table_Tests.compareResults(recordPass,verbose,sTest,sIncluded,StringTools.replace(sbBuffer.b.getvalue(),"\"",""))
        except BaseException as _g:
            None
            msg = haxe_Exception.caught(_g).unwrap()
            if verbose:
                return ((((((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sEXCEPTION)) + ":\n") + Std.string(msg))
            else:
                return ((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED))

    @staticmethod
    def testIncludeRows(recordPass,verbose):
        sTest = "testIncludeRows"
        sExcluded = "5,6,7"
        sbBuffer = StringBuf()
        try:
            com_sdtk_table_Converter.convertWithOptions(com_sdtk_table_Tests.sCSV,com_sdtk_table_Format.CSV,sbBuffer,com_sdtk_table_Format.CSV,None,None,None,"#2",None,False,False,None,None)
            return com_sdtk_table_Tests.compareResults(recordPass,verbose,sTest,sExcluded,StringTools.replace(sbBuffer.b.getvalue(),"\"",""))
        except BaseException as _g:
            None
            msg = haxe_Exception.caught(_g).unwrap()
            if verbose:
                return ((((((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sEXCEPTION)) + ":\n") + Std.string(msg))
            else:
                return ((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED))

    @staticmethod
    def testOrderBy(recordPass,verbose):
        sTest = "testOrderBy"
        sOrdered = "A,B,C\n1,2,3\n8,1,5\n5,6,7"
        sbBuffer = StringBuf()
        try:
            com_sdtk_table_Converter.convertWithOptions(com_sdtk_table_Tests.sCSV,com_sdtk_table_Format.CSV,sbBuffer,com_sdtk_table_Format.CSV,None,None,None,None,"C",False,False,None,None)
            return com_sdtk_table_Tests.compareResults(recordPass,verbose,sTest,sOrdered,StringTools.replace(sbBuffer.b.getvalue(),"\"",""))
        except BaseException as _g:
            None
            msg = haxe_Exception.caught(_g).unwrap()
            if verbose:
                return ((((((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED)) + "\n") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sEXCEPTION)) + ":\n") + Std.string(msg))
            else:
                return ((("null" if sTest is None else sTest) + ": ") + HxOverrides.stringOrNull(com_sdtk_table_Tests.sFAILED))


class haxe_IMap:
    _hx_class_name = "haxe.IMap"
    __slots__ = ()
haxe_IMap._hx_class = haxe_IMap


class haxe_Exception(Exception):
    _hx_class_name = "haxe.Exception"
    __slots__ = ("_hx___nativeStack", "_hx___skipStack", "_hx___nativeException", "_hx___previousException")
    _hx_fields = ["__nativeStack", "__skipStack", "__nativeException", "__previousException"]
    _hx_methods = ["unwrap", "toString", "get_message", "get_native"]
    _hx_statics = ["caught", "thrown"]
    _hx_interfaces = []
    _hx_super = Exception


    def __init__(self,message,previous = None,native = None):
        self._hx___previousException = None
        self._hx___nativeException = None
        self._hx___nativeStack = None
        self._hx___skipStack = 0
        super().__init__(message)
        self._hx___previousException = previous
        if ((native is not None) and Std.isOfType(native,BaseException)):
            self._hx___nativeException = native
            self._hx___nativeStack = haxe_NativeStackTrace.exceptionStack()
        else:
            self._hx___nativeException = self
            infos = python_lib_Traceback.extract_stack()
            if (len(infos) != 0):
                infos.pop()
            infos.reverse()
            self._hx___nativeStack = infos

    def unwrap(self):
        return self._hx___nativeException

    def toString(self):
        return self.get_message()

    def get_message(self):
        return str(self)

    def get_native(self):
        return self._hx___nativeException

    @staticmethod
    def caught(value):
        if Std.isOfType(value,haxe_Exception):
            return value
        elif Std.isOfType(value,BaseException):
            return haxe_Exception(str(value),None,value)
        else:
            return haxe_ValueException(value,None,value)

    @staticmethod
    def thrown(value):
        if Std.isOfType(value,haxe_Exception):
            return value.get_native()
        elif Std.isOfType(value,BaseException):
            return value
        else:
            e = haxe_ValueException(value)
            e._hx___skipStack = (e._hx___skipStack + 1)
            return e

haxe_Exception._hx_class = haxe_Exception


class haxe_NativeStackTrace:
    _hx_class_name = "haxe.NativeStackTrace"
    __slots__ = ()
    _hx_statics = ["saveStack", "exceptionStack"]

    @staticmethod
    def saveStack(exception):
        pass

    @staticmethod
    def exceptionStack():
        exc = python_lib_Sys.exc_info()
        if (exc[2] is not None):
            infos = python_lib_Traceback.extract_tb(exc[2])
            infos.reverse()
            return infos
        else:
            return []
haxe_NativeStackTrace._hx_class = haxe_NativeStackTrace


class haxe_ValueException(haxe_Exception):
    _hx_class_name = "haxe.ValueException"
    __slots__ = ("value",)
    _hx_fields = ["value"]
    _hx_methods = ["unwrap"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_Exception


    def __init__(self,value,previous = None,native = None):
        self.value = None
        super().__init__(Std.string(value),previous,native)
        self.value = value

    def unwrap(self):
        return self.value

haxe_ValueException._hx_class = haxe_ValueException


class haxe_ds_StringMap:
    _hx_class_name = "haxe.ds.StringMap"
    __slots__ = ("h",)
    _hx_fields = ["h"]
    _hx_methods = ["keys"]
    _hx_interfaces = [haxe_IMap]

    def __init__(self):
        self.h = dict()

    def keys(self):
        return python_HaxeIterator(iter(self.h.keys()))

haxe_ds_StringMap._hx_class = haxe_ds_StringMap


class haxe_exceptions_PosException(haxe_Exception):
    _hx_class_name = "haxe.exceptions.PosException"
    __slots__ = ("posInfos",)
    _hx_fields = ["posInfos"]
    _hx_methods = ["toString"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_Exception


    def __init__(self,message,previous = None,pos = None):
        self.posInfos = None
        super().__init__(message,previous)
        if (pos is None):
            self.posInfos = _hx_AnonObject({'fileName': "(unknown)", 'lineNumber': 0, 'className': "(unknown)", 'methodName': "(unknown)"})
        else:
            self.posInfos = pos

    def toString(self):
        return ((((((((("" + HxOverrides.stringOrNull(super().toString())) + " in ") + HxOverrides.stringOrNull(self.posInfos.className)) + ".") + HxOverrides.stringOrNull(self.posInfos.methodName)) + " at ") + HxOverrides.stringOrNull(self.posInfos.fileName)) + ":") + Std.string(self.posInfos.lineNumber))

haxe_exceptions_PosException._hx_class = haxe_exceptions_PosException


class haxe_exceptions_NotImplementedException(haxe_exceptions_PosException):
    _hx_class_name = "haxe.exceptions.NotImplementedException"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_exceptions_PosException


    def __init__(self,message = None,previous = None,pos = None):
        if (message is None):
            message = "Not implemented"
        super().__init__(message,previous,pos)
haxe_exceptions_NotImplementedException._hx_class = haxe_exceptions_NotImplementedException


class haxe_format_JsonPrinter:
    _hx_class_name = "haxe.format.JsonPrinter"
    __slots__ = ("buf", "replacer", "indent", "pretty", "nind")
    _hx_fields = ["buf", "replacer", "indent", "pretty", "nind"]
    _hx_methods = ["write", "classString", "fieldsString", "quote"]
    _hx_statics = ["print"]

    def __init__(self,replacer,space):
        self.replacer = replacer
        self.indent = space
        self.pretty = (space is not None)
        self.nind = 0
        self.buf = StringBuf()

    def write(self,k,v):
        if (self.replacer is not None):
            v = self.replacer(k,v)
        _g = Type.typeof(v)
        tmp = _g.index
        if (tmp == 0):
            self.buf.b.write("null")
        elif (tmp == 1):
            _this = self.buf
            s = Std.string(v)
            _this.b.write(s)
        elif (tmp == 2):
            f = v
            v1 = (Std.string(v) if ((((f != Math.POSITIVE_INFINITY) and ((f != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(f)))) else "null")
            _this = self.buf
            s = Std.string(v1)
            _this.b.write(s)
        elif (tmp == 3):
            _this = self.buf
            s = Std.string(v)
            _this.b.write(s)
        elif (tmp == 4):
            self.fieldsString(v,python_Boot.fields(v))
        elif (tmp == 5):
            self.buf.b.write("\"<fun>\"")
        elif (tmp == 6):
            c = _g.params[0]
            if (c == str):
                self.quote(v)
            elif (c == list):
                v1 = v
                _this = self.buf
                s = "".join(map(chr,[91]))
                _this.b.write(s)
                _hx_len = len(v1)
                last = (_hx_len - 1)
                _g1 = 0
                _g2 = _hx_len
                while (_g1 < _g2):
                    i = _g1
                    _g1 = (_g1 + 1)
                    if (i > 0):
                        _this = self.buf
                        s = "".join(map(chr,[44]))
                        _this.b.write(s)
                    else:
                        _hx_local_0 = self
                        _hx_local_1 = _hx_local_0.nind
                        _hx_local_0.nind = (_hx_local_1 + 1)
                        _hx_local_1
                    if self.pretty:
                        _this1 = self.buf
                        s1 = "".join(map(chr,[10]))
                        _this1.b.write(s1)
                    if self.pretty:
                        v2 = StringTools.lpad("",self.indent,(self.nind * len(self.indent)))
                        _this2 = self.buf
                        s2 = Std.string(v2)
                        _this2.b.write(s2)
                    self.write(i,(v1[i] if i >= 0 and i < len(v1) else None))
                    if (i == last):
                        _hx_local_2 = self
                        _hx_local_3 = _hx_local_2.nind
                        _hx_local_2.nind = (_hx_local_3 - 1)
                        _hx_local_3
                        if self.pretty:
                            _this3 = self.buf
                            s3 = "".join(map(chr,[10]))
                            _this3.b.write(s3)
                        if self.pretty:
                            v3 = StringTools.lpad("",self.indent,(self.nind * len(self.indent)))
                            _this4 = self.buf
                            s4 = Std.string(v3)
                            _this4.b.write(s4)
                _this = self.buf
                s = "".join(map(chr,[93]))
                _this.b.write(s)
            elif (c == haxe_ds_StringMap):
                v1 = v
                o = _hx_AnonObject({})
                k = v1.keys()
                while k.hasNext():
                    k1 = k.next()
                    value = v1.h.get(k1,None)
                    setattr(o,(("_hx_" + k1) if ((k1 in python_Boot.keywords)) else (("_hx_" + k1) if (((((len(k1) > 2) and ((ord(k1[0]) == 95))) and ((ord(k1[1]) == 95))) and ((ord(k1[(len(k1) - 1)]) != 95)))) else k1)),value)
                v1 = o
                self.fieldsString(v1,python_Boot.fields(v1))
            elif (c == Date):
                v1 = v
                self.quote(v1.toString())
            else:
                self.classString(v)
        elif (tmp == 7):
            _g1 = _g.params[0]
            i = v.index
            _this = self.buf
            s = Std.string(i)
            _this.b.write(s)
        elif (tmp == 8):
            self.buf.b.write("\"???\"")
        else:
            pass

    def classString(self,v):
        self.fieldsString(v,python_Boot.getInstanceFields(Type.getClass(v)))

    def fieldsString(self,v,fields):
        _this = self.buf
        s = "".join(map(chr,[123]))
        _this.b.write(s)
        _hx_len = len(fields)
        last = (_hx_len - 1)
        first = True
        _g = 0
        _g1 = _hx_len
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            f = (fields[i] if i >= 0 and i < len(fields) else None)
            value = Reflect.field(v,f)
            if Reflect.isFunction(value):
                continue
            if first:
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.nind
                _hx_local_0.nind = (_hx_local_1 + 1)
                _hx_local_1
                first = False
            else:
                _this = self.buf
                s = "".join(map(chr,[44]))
                _this.b.write(s)
            if self.pretty:
                _this1 = self.buf
                s1 = "".join(map(chr,[10]))
                _this1.b.write(s1)
            if self.pretty:
                v1 = StringTools.lpad("",self.indent,(self.nind * len(self.indent)))
                _this2 = self.buf
                s2 = Std.string(v1)
                _this2.b.write(s2)
            self.quote(f)
            _this3 = self.buf
            s3 = "".join(map(chr,[58]))
            _this3.b.write(s3)
            if self.pretty:
                _this4 = self.buf
                s4 = "".join(map(chr,[32]))
                _this4.b.write(s4)
            self.write(f,value)
            if (i == last):
                _hx_local_2 = self
                _hx_local_3 = _hx_local_2.nind
                _hx_local_2.nind = (_hx_local_3 - 1)
                _hx_local_3
                if self.pretty:
                    _this5 = self.buf
                    s5 = "".join(map(chr,[10]))
                    _this5.b.write(s5)
                if self.pretty:
                    v2 = StringTools.lpad("",self.indent,(self.nind * len(self.indent)))
                    _this6 = self.buf
                    s6 = Std.string(v2)
                    _this6.b.write(s6)
        _this = self.buf
        s = "".join(map(chr,[125]))
        _this.b.write(s)

    def quote(self,s):
        _this = self.buf
        s1 = "".join(map(chr,[34]))
        _this.b.write(s1)
        i = 0
        length = len(s)
        while (i < length):
            index = i
            i = (i + 1)
            c = ord(s[index])
            c1 = c
            if (c1 == 8):
                self.buf.b.write("\\b")
            elif (c1 == 9):
                self.buf.b.write("\\t")
            elif (c1 == 10):
                self.buf.b.write("\\n")
            elif (c1 == 12):
                self.buf.b.write("\\f")
            elif (c1 == 13):
                self.buf.b.write("\\r")
            elif (c1 == 34):
                self.buf.b.write("\\\"")
            elif (c1 == 92):
                self.buf.b.write("\\\\")
            else:
                _this = self.buf
                s1 = "".join(map(chr,[c]))
                _this.b.write(s1)
        _this = self.buf
        s = "".join(map(chr,[34]))
        _this.b.write(s)

    @staticmethod
    def print(o,replacer = None,space = None):
        printer = haxe_format_JsonPrinter(replacer,space)
        printer.write("",o)
        return printer.buf.b.getvalue()

haxe_format_JsonPrinter._hx_class = haxe_format_JsonPrinter


class haxe_io_Bytes:
    _hx_class_name = "haxe.io.Bytes"
    __slots__ = ("length", "b")
    _hx_fields = ["length", "b"]
    _hx_methods = ["blit", "getString", "toString"]
    _hx_statics = ["alloc", "ofString", "ofData"]

    def __init__(self,length,b):
        self.length = length
        self.b = b

    def blit(self,pos,src,srcpos,_hx_len):
        if (((((pos < 0) or ((srcpos < 0))) or ((_hx_len < 0))) or (((pos + _hx_len) > self.length))) or (((srcpos + _hx_len) > src.length))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        self.b[pos:pos+_hx_len] = src.b[srcpos:srcpos+_hx_len]

    def getString(self,pos,_hx_len,encoding = None):
        tmp = (encoding is None)
        if (((pos < 0) or ((_hx_len < 0))) or (((pos + _hx_len) > self.length))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        return self.b[pos:pos+_hx_len].decode('UTF-8','replace')

    def toString(self):
        return self.getString(0,self.length)

    @staticmethod
    def alloc(length):
        return haxe_io_Bytes(length,bytearray(length))

    @staticmethod
    def ofString(s,encoding = None):
        b = bytearray(s,"UTF-8")
        return haxe_io_Bytes(len(b),b)

    @staticmethod
    def ofData(b):
        return haxe_io_Bytes(len(b),b)

haxe_io_Bytes._hx_class = haxe_io_Bytes


class haxe_io_BytesBuffer:
    _hx_class_name = "haxe.io.BytesBuffer"
    __slots__ = ("b",)
    _hx_fields = ["b"]
    _hx_methods = ["getBytes"]

    def __init__(self):
        self.b = bytearray()

    def getBytes(self):
        _hx_bytes = haxe_io_Bytes(len(self.b),self.b)
        self.b = None
        return _hx_bytes

haxe_io_BytesBuffer._hx_class = haxe_io_BytesBuffer

class haxe_io_Encoding(Enum):
    __slots__ = ()
    _hx_class_name = "haxe.io.Encoding"
    _hx_constructs = ["UTF8", "RawNative"]
haxe_io_Encoding.UTF8 = haxe_io_Encoding("UTF8", 0, ())
haxe_io_Encoding.RawNative = haxe_io_Encoding("RawNative", 1, ())
haxe_io_Encoding._hx_class = haxe_io_Encoding


class haxe_io_Eof:
    _hx_class_name = "haxe.io.Eof"
    __slots__ = ()
    _hx_methods = ["toString"]

    def __init__(self):
        pass

    def toString(self):
        return "Eof"

haxe_io_Eof._hx_class = haxe_io_Eof

class haxe_io_Error(Enum):
    __slots__ = ()
    _hx_class_name = "haxe.io.Error"
    _hx_constructs = ["Blocked", "Overflow", "OutsideBounds", "Custom"]

    @staticmethod
    def Custom(e):
        return haxe_io_Error("Custom", 3, (e,))
haxe_io_Error.Blocked = haxe_io_Error("Blocked", 0, ())
haxe_io_Error.Overflow = haxe_io_Error("Overflow", 1, ())
haxe_io_Error.OutsideBounds = haxe_io_Error("OutsideBounds", 2, ())
haxe_io_Error._hx_class = haxe_io_Error


class haxe_io_Input:
    _hx_class_name = "haxe.io.Input"
    __slots__ = ("bigEndian",)
    _hx_fields = ["bigEndian"]
    _hx_methods = ["readByte", "readBytes", "close", "set_bigEndian", "readFullBytes", "readLine", "readString"]

    def readByte(self):
        raise haxe_exceptions_NotImplementedException(None,None,_hx_AnonObject({'fileName': "haxe/io/Input.hx", 'lineNumber': 53, 'className': "haxe.io.Input", 'methodName': "readByte"}))

    def readBytes(self,s,pos,_hx_len):
        k = _hx_len
        b = s.b
        if (((pos < 0) or ((_hx_len < 0))) or (((pos + _hx_len) > s.length))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        try:
            while (k > 0):
                b[pos] = self.readByte()
                pos = (pos + 1)
                k = (k - 1)
        except BaseException as _g:
            None
            if (not Std.isOfType(haxe_Exception.caught(_g).unwrap(),haxe_io_Eof)):
                raise _g
        return (_hx_len - k)

    def close(self):
        pass

    def set_bigEndian(self,b):
        self.bigEndian = b
        return b

    def readFullBytes(self,s,pos,_hx_len):
        while (_hx_len > 0):
            k = self.readBytes(s,pos,_hx_len)
            if (k == 0):
                raise haxe_Exception.thrown(haxe_io_Error.Blocked)
            pos = (pos + k)
            _hx_len = (_hx_len - k)

    def readLine(self):
        buf = haxe_io_BytesBuffer()
        last = None
        s = None
        try:
            while True:
                last = self.readByte()
                if (not ((last != 10))):
                    break
                buf.b.append(last)
            s = buf.getBytes().toString()
            if (HxString.charCodeAt(s,(len(s) - 1)) == 13):
                s = HxString.substr(s,0,-1)
        except BaseException as _g:
            None
            _g1 = haxe_Exception.caught(_g).unwrap()
            if Std.isOfType(_g1,haxe_io_Eof):
                e = _g1
                s = buf.getBytes().toString()
                if (len(s) == 0):
                    raise haxe_Exception.thrown(e)
            else:
                raise _g
        return s

    def readString(self,_hx_len,encoding = None):
        b = haxe_io_Bytes.alloc(_hx_len)
        self.readFullBytes(b,0,_hx_len)
        return b.getString(0,_hx_len,encoding)

haxe_io_Input._hx_class = haxe_io_Input


class haxe_io_Output:
    _hx_class_name = "haxe.io.Output"
    __slots__ = ("bigEndian",)
    _hx_fields = ["bigEndian"]
    _hx_methods = ["writeByte", "writeBytes", "flush", "close", "set_bigEndian", "writeFullBytes", "writeString"]

    def writeByte(self,c):
        raise haxe_exceptions_NotImplementedException(None,None,_hx_AnonObject({'fileName': "haxe/io/Output.hx", 'lineNumber': 47, 'className': "haxe.io.Output", 'methodName': "writeByte"}))

    def writeBytes(self,s,pos,_hx_len):
        if (((pos < 0) or ((_hx_len < 0))) or (((pos + _hx_len) > s.length))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        b = s.b
        k = _hx_len
        while (k > 0):
            self.writeByte(b[pos])
            pos = (pos + 1)
            k = (k - 1)
        return _hx_len

    def flush(self):
        pass

    def close(self):
        pass

    def set_bigEndian(self,b):
        self.bigEndian = b
        return b

    def writeFullBytes(self,s,pos,_hx_len):
        while (_hx_len > 0):
            k = self.writeBytes(s,pos,_hx_len)
            pos = (pos + k)
            _hx_len = (_hx_len - k)

    def writeString(self,s,encoding = None):
        b = haxe_io_Bytes.ofString(s,encoding)
        self.writeFullBytes(b,0,b.length)

haxe_io_Output._hx_class = haxe_io_Output


class haxe_io_Path:
    _hx_class_name = "haxe.io.Path"
    __slots__ = ("dir", "file", "ext", "backslash")
    _hx_fields = ["dir", "file", "ext", "backslash"]
    _hx_methods = ["toString"]

    def __init__(self,path):
        self.backslash = None
        self.ext = None
        self.file = None
        self.dir = None
        path1 = path
        _hx_local_0 = len(path1)
        if (_hx_local_0 == 1):
            if (path1 == "."):
                self.dir = path
                self.file = ""
                return
        elif (_hx_local_0 == 2):
            if (path1 == ".."):
                self.dir = path
                self.file = ""
                return
        else:
            pass
        startIndex = None
        c1 = None
        if (startIndex is None):
            c1 = path.rfind("/", 0, len(path))
        else:
            i = path.rfind("/", 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len("/"))) if ((i == -1)) else (i + 1))
            check = path.find("/", startLeft, len(path))
            c1 = (check if (((check > i) and ((check <= startIndex)))) else i)
        startIndex = None
        c2 = None
        if (startIndex is None):
            c2 = path.rfind("\\", 0, len(path))
        else:
            i = path.rfind("\\", 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len("\\"))) if ((i == -1)) else (i + 1))
            check = path.find("\\", startLeft, len(path))
            c2 = (check if (((check > i) and ((check <= startIndex)))) else i)
        if (c1 < c2):
            self.dir = HxString.substr(path,0,c2)
            path = HxString.substr(path,(c2 + 1),None)
            self.backslash = True
        elif (c2 < c1):
            self.dir = HxString.substr(path,0,c1)
            path = HxString.substr(path,(c1 + 1),None)
        else:
            self.dir = None
        startIndex = None
        cp = None
        if (startIndex is None):
            cp = path.rfind(".", 0, len(path))
        else:
            i = path.rfind(".", 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len("."))) if ((i == -1)) else (i + 1))
            check = path.find(".", startLeft, len(path))
            cp = (check if (((check > i) and ((check <= startIndex)))) else i)
        if (cp != -1):
            self.ext = HxString.substr(path,(cp + 1),None)
            self.file = HxString.substr(path,0,cp)
        else:
            self.ext = None
            self.file = path

    def toString(self):
        return ((HxOverrides.stringOrNull((("" if ((self.dir is None)) else (HxOverrides.stringOrNull(self.dir) + HxOverrides.stringOrNull((("\\" if (self.backslash) else "/"))))))) + HxOverrides.stringOrNull(self.file)) + HxOverrides.stringOrNull((("" if ((self.ext is None)) else ("." + HxOverrides.stringOrNull(self.ext))))))

haxe_io_Path._hx_class = haxe_io_Path


class haxe_iterators_ArrayIterator:
    _hx_class_name = "haxe.iterators.ArrayIterator"
    __slots__ = ("array", "current")
    _hx_fields = ["array", "current"]
    _hx_methods = ["hasNext", "next"]

    def __init__(self,array):
        self.current = 0
        self.array = array

    def hasNext(self):
        return (self.current < len(self.array))

    def next(self):
        def _hx_local_3():
            def _hx_local_2():
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.current
                _hx_local_0.current = (_hx_local_1 + 1)
                return _hx_local_1
            return python_internal_ArrayImpl._get(self.array, _hx_local_2())
        return _hx_local_3()

haxe_iterators_ArrayIterator._hx_class = haxe_iterators_ArrayIterator


class haxe_iterators_ArrayKeyValueIterator:
    _hx_class_name = "haxe.iterators.ArrayKeyValueIterator"
    __slots__ = ("current", "array")
    _hx_fields = ["current", "array"]
    _hx_methods = ["hasNext", "next"]

    def __init__(self,array):
        self.current = 0
        self.array = array

    def hasNext(self):
        return (self.current < len(self.array))

    def next(self):
        def _hx_local_3():
            def _hx_local_2():
                _hx_local_0 = self
                _hx_local_1 = _hx_local_0.current
                _hx_local_0.current = (_hx_local_1 + 1)
                return _hx_local_1
            return _hx_AnonObject({'value': python_internal_ArrayImpl._get(self.array, self.current), 'key': _hx_local_2()})
        return _hx_local_3()

haxe_iterators_ArrayKeyValueIterator._hx_class = haxe_iterators_ArrayKeyValueIterator


class python_Boot:
    _hx_class_name = "python.Boot"
    __slots__ = ()
    _hx_statics = ["keywords", "toString1", "fields", "simpleField", "hasField", "field", "getInstanceFields", "getSuperClass", "getClassFields", "prefixLength", "unhandleKeywords"]

    @staticmethod
    def toString1(o,s):
        if (o is None):
            return "null"
        if isinstance(o,str):
            return o
        if (s is None):
            s = ""
        if (len(s) >= 5):
            return "<...>"
        if isinstance(o,bool):
            if o:
                return "true"
            else:
                return "false"
        if (isinstance(o,int) and (not isinstance(o,bool))):
            return str(o)
        if isinstance(o,float):
            try:
                if (o == int(o)):
                    return str(Math.floor((o + 0.5)))
                else:
                    return str(o)
            except BaseException as _g:
                None
                return str(o)
        if isinstance(o,list):
            o1 = o
            l = len(o1)
            st = "["
            s = (("null" if s is None else s) + "\t")
            _g = 0
            _g1 = l
            while (_g < _g1):
                i = _g
                _g = (_g + 1)
                prefix = ""
                if (i > 0):
                    prefix = ","
                st = (("null" if st is None else st) + HxOverrides.stringOrNull(((("null" if prefix is None else prefix) + HxOverrides.stringOrNull(python_Boot.toString1((o1[i] if i >= 0 and i < len(o1) else None),s))))))
            st = (("null" if st is None else st) + "]")
            return st
        try:
            if hasattr(o,"toString"):
                return o.toString()
        except BaseException as _g:
            None
        if hasattr(o,"__class__"):
            if isinstance(o,_hx_AnonObject):
                toStr = None
                try:
                    fields = python_Boot.fields(o)
                    _g = []
                    _g1 = 0
                    while (_g1 < len(fields)):
                        f = (fields[_g1] if _g1 >= 0 and _g1 < len(fields) else None)
                        _g1 = (_g1 + 1)
                        x = ((("" + ("null" if f is None else f)) + " : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.simpleField(o,f),(("null" if s is None else s) + "\t"))))
                        _g.append(x)
                    fieldsStr = _g
                    toStr = (("{ " + HxOverrides.stringOrNull(", ".join([x1 for x1 in fieldsStr]))) + " }")
                except BaseException as _g:
                    None
                    return "{ ... }"
                if (toStr is None):
                    return "{ ... }"
                else:
                    return toStr
            if isinstance(o,Enum):
                o1 = o
                l = len(o1.params)
                hasParams = (l > 0)
                if hasParams:
                    paramsStr = ""
                    _g = 0
                    _g1 = l
                    while (_g < _g1):
                        i = _g
                        _g = (_g + 1)
                        prefix = ""
                        if (i > 0):
                            prefix = ","
                        paramsStr = (("null" if paramsStr is None else paramsStr) + HxOverrides.stringOrNull(((("null" if prefix is None else prefix) + HxOverrides.stringOrNull(python_Boot.toString1(o1.params[i],s))))))
                    return (((HxOverrides.stringOrNull(o1.tag) + "(") + ("null" if paramsStr is None else paramsStr)) + ")")
                else:
                    return o1.tag
            if hasattr(o,"_hx_class_name"):
                if (o.__class__.__name__ != "type"):
                    fields = python_Boot.getInstanceFields(o)
                    _g = []
                    _g1 = 0
                    while (_g1 < len(fields)):
                        f = (fields[_g1] if _g1 >= 0 and _g1 < len(fields) else None)
                        _g1 = (_g1 + 1)
                        x = ((("" + ("null" if f is None else f)) + " : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.simpleField(o,f),(("null" if s is None else s) + "\t"))))
                        _g.append(x)
                    fieldsStr = _g
                    toStr = (((HxOverrides.stringOrNull(o._hx_class_name) + "( ") + HxOverrides.stringOrNull(", ".join([x1 for x1 in fieldsStr]))) + " )")
                    return toStr
                else:
                    fields = python_Boot.getClassFields(o)
                    _g = []
                    _g1 = 0
                    while (_g1 < len(fields)):
                        f = (fields[_g1] if _g1 >= 0 and _g1 < len(fields) else None)
                        _g1 = (_g1 + 1)
                        x = ((("" + ("null" if f is None else f)) + " : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.simpleField(o,f),(("null" if s is None else s) + "\t"))))
                        _g.append(x)
                    fieldsStr = _g
                    toStr = (((("#" + HxOverrides.stringOrNull(o._hx_class_name)) + "( ") + HxOverrides.stringOrNull(", ".join([x1 for x1 in fieldsStr]))) + " )")
                    return toStr
            if ((type(o) == type) and (o == str)):
                return "#String"
            if ((type(o) == type) and (o == list)):
                return "#Array"
            if callable(o):
                return "function"
            try:
                if hasattr(o,"__repr__"):
                    return o.__repr__()
            except BaseException as _g:
                None
            if hasattr(o,"__str__"):
                return o.__str__([])
            if hasattr(o,"__name__"):
                return o.__name__
            return "???"
        else:
            return str(o)

    @staticmethod
    def fields(o):
        a = []
        if (o is not None):
            if hasattr(o,"_hx_fields"):
                fields = o._hx_fields
                if (fields is not None):
                    return list(fields)
            if isinstance(o,_hx_AnonObject):
                d = o.__dict__
                keys = d.keys()
                handler = python_Boot.unhandleKeywords
                for k in keys:
                    if (k != '_hx_disable_getattr'):
                        a.append(handler(k))
            elif hasattr(o,"__dict__"):
                d = o.__dict__
                keys1 = d.keys()
                for k in keys1:
                    a.append(k)
        return a

    @staticmethod
    def simpleField(o,field):
        if (field is None):
            return None
        field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
        if hasattr(o,field1):
            return getattr(o,field1)
        else:
            return None

    @staticmethod
    def hasField(o,field):
        if isinstance(o,_hx_AnonObject):
            return o._hx_hasattr(field)
        return hasattr(o,(("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field)))

    @staticmethod
    def field(o,field):
        if (field is None):
            return None
        if isinstance(o,str):
            field1 = field
            _hx_local_0 = len(field1)
            if (_hx_local_0 == 10):
                if (field1 == "charCodeAt"):
                    return python_internal_MethodClosure(o,HxString.charCodeAt)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 11):
                if (field1 == "lastIndexOf"):
                    return python_internal_MethodClosure(o,HxString.lastIndexOf)
                elif (field1 == "toLowerCase"):
                    return python_internal_MethodClosure(o,HxString.toLowerCase)
                elif (field1 == "toUpperCase"):
                    return python_internal_MethodClosure(o,HxString.toUpperCase)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 9):
                if (field1 == "substring"):
                    return python_internal_MethodClosure(o,HxString.substring)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 5):
                if (field1 == "split"):
                    return python_internal_MethodClosure(o,HxString.split)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 7):
                if (field1 == "indexOf"):
                    return python_internal_MethodClosure(o,HxString.indexOf)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 8):
                if (field1 == "toString"):
                    return python_internal_MethodClosure(o,HxString.toString)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_0 == 6):
                if (field1 == "charAt"):
                    return python_internal_MethodClosure(o,HxString.charAt)
                elif (field1 == "length"):
                    return len(o)
                elif (field1 == "substr"):
                    return python_internal_MethodClosure(o,HxString.substr)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            else:
                field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                if hasattr(o,field1):
                    return getattr(o,field1)
                else:
                    return None
        elif isinstance(o,list):
            field1 = field
            _hx_local_1 = len(field1)
            if (_hx_local_1 == 11):
                if (field1 == "lastIndexOf"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.lastIndexOf)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 4):
                if (field1 == "copy"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.copy)
                elif (field1 == "join"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.join)
                elif (field1 == "push"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.push)
                elif (field1 == "sort"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.sort)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 5):
                if (field1 == "shift"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.shift)
                elif (field1 == "slice"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.slice)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 7):
                if (field1 == "indexOf"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.indexOf)
                elif (field1 == "reverse"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.reverse)
                elif (field1 == "unshift"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.unshift)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 3):
                if (field1 == "map"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.map)
                elif (field1 == "pop"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.pop)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 8):
                if (field1 == "contains"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.contains)
                elif (field1 == "iterator"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.iterator)
                elif (field1 == "toString"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.toString)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 16):
                if (field1 == "keyValueIterator"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.keyValueIterator)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            elif (_hx_local_1 == 6):
                if (field1 == "concat"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.concat)
                elif (field1 == "filter"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.filter)
                elif (field1 == "insert"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.insert)
                elif (field1 == "length"):
                    return len(o)
                elif (field1 == "remove"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.remove)
                elif (field1 == "splice"):
                    return python_internal_MethodClosure(o,python_internal_ArrayImpl.splice)
                else:
                    field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                    if hasattr(o,field1):
                        return getattr(o,field1)
                    else:
                        return None
            else:
                field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
                if hasattr(o,field1):
                    return getattr(o,field1)
                else:
                    return None
        else:
            field1 = (("_hx_" + field) if ((field in python_Boot.keywords)) else (("_hx_" + field) if (((((len(field) > 2) and ((ord(field[0]) == 95))) and ((ord(field[1]) == 95))) and ((ord(field[(len(field) - 1)]) != 95)))) else field))
            if hasattr(o,field1):
                return getattr(o,field1)
            else:
                return None

    @staticmethod
    def getInstanceFields(c):
        f = (list(c._hx_fields) if (hasattr(c,"_hx_fields")) else [])
        if hasattr(c,"_hx_methods"):
            f = (f + c._hx_methods)
        sc = python_Boot.getSuperClass(c)
        if (sc is None):
            return f
        else:
            scArr = python_Boot.getInstanceFields(sc)
            scMap = set(scArr)
            _g = 0
            while (_g < len(f)):
                f1 = (f[_g] if _g >= 0 and _g < len(f) else None)
                _g = (_g + 1)
                if (not (f1 in scMap)):
                    scArr.append(f1)
            return scArr

    @staticmethod
    def getSuperClass(c):
        if (c is None):
            return None
        try:
            if hasattr(c,"_hx_super"):
                return c._hx_super
            return None
        except BaseException as _g:
            None
        return None

    @staticmethod
    def getClassFields(c):
        if hasattr(c,"_hx_statics"):
            x = c._hx_statics
            return list(x)
        else:
            return []

    @staticmethod
    def unhandleKeywords(name):
        if (HxString.substr(name,0,python_Boot.prefixLength) == "_hx_"):
            real = HxString.substr(name,python_Boot.prefixLength,None)
            if (real in python_Boot.keywords):
                return real
        return name
python_Boot._hx_class = python_Boot


class python_HaxeIterator:
    _hx_class_name = "python.HaxeIterator"
    __slots__ = ("it", "x", "has", "checked")
    _hx_fields = ["it", "x", "has", "checked"]
    _hx_methods = ["next", "hasNext"]

    def __init__(self,it):
        self.checked = False
        self.has = False
        self.x = None
        self.it = it

    def next(self):
        if (not self.checked):
            self.hasNext()
        self.checked = False
        return self.x

    def hasNext(self):
        if (not self.checked):
            try:
                self.x = self.it.__next__()
                self.has = True
            except BaseException as _g:
                None
                if Std.isOfType(haxe_Exception.caught(_g).unwrap(),StopIteration):
                    self.has = False
                    self.x = None
                else:
                    raise _g
            self.checked = True
        return self.has

python_HaxeIterator._hx_class = python_HaxeIterator


class python__KwArgs_KwArgs_Impl_:
    _hx_class_name = "python._KwArgs.KwArgs_Impl_"
    __slots__ = ()
    _hx_statics = ["fromT"]

    @staticmethod
    def fromT(d):
        this1 = python_Lib.anonAsDict(d)
        return this1
python__KwArgs_KwArgs_Impl_._hx_class = python__KwArgs_KwArgs_Impl_


class python_Lib:
    _hx_class_name = "python.Lib"
    __slots__ = ()
    _hx_statics = ["lineEnd", "printString", "dictToAnon", "anonToDict", "anonAsDict"]

    @staticmethod
    def printString(_hx_str):
        encoding = "utf-8"
        if (encoding is None):
            encoding = "utf-8"
        python_lib_Sys.stdout.buffer.write(_hx_str.encode(encoding, "strict"))
        python_lib_Sys.stdout.flush()

    @staticmethod
    def dictToAnon(v):
        return _hx_AnonObject(v.copy())

    @staticmethod
    def anonToDict(o):
        if isinstance(o,_hx_AnonObject):
            return o.__dict__.copy()
        else:
            return None

    @staticmethod
    def anonAsDict(o):
        if isinstance(o,_hx_AnonObject):
            return o.__dict__
        else:
            return None
python_Lib._hx_class = python_Lib


class python_internal_ArrayImpl:
    _hx_class_name = "python.internal.ArrayImpl"
    __slots__ = ()
    _hx_statics = ["get_length", "concat", "copy", "iterator", "keyValueIterator", "indexOf", "lastIndexOf", "join", "toString", "pop", "push", "unshift", "remove", "contains", "shift", "slice", "sort", "splice", "map", "filter", "insert", "reverse", "_get", "_set"]

    @staticmethod
    def get_length(x):
        return len(x)

    @staticmethod
    def concat(a1,a2):
        return (a1 + a2)

    @staticmethod
    def copy(x):
        return list(x)

    @staticmethod
    def iterator(x):
        return python_HaxeIterator(x.__iter__())

    @staticmethod
    def keyValueIterator(x):
        return haxe_iterators_ArrayKeyValueIterator(x)

    @staticmethod
    def indexOf(a,x,fromIndex = None):
        _hx_len = len(a)
        l = (0 if ((fromIndex is None)) else ((_hx_len + fromIndex) if ((fromIndex < 0)) else fromIndex))
        if (l < 0):
            l = 0
        _g = l
        _g1 = _hx_len
        while (_g < _g1):
            i = _g
            _g = (_g + 1)
            if HxOverrides.eq(a[i],x):
                return i
        return -1

    @staticmethod
    def lastIndexOf(a,x,fromIndex = None):
        _hx_len = len(a)
        l = (_hx_len if ((fromIndex is None)) else (((_hx_len + fromIndex) + 1) if ((fromIndex < 0)) else (fromIndex + 1)))
        if (l > _hx_len):
            l = _hx_len
        while True:
            l = (l - 1)
            tmp = l
            if (not ((tmp > -1))):
                break
            if HxOverrides.eq(a[l],x):
                return l
        return -1

    @staticmethod
    def join(x,sep):
        return sep.join([python_Boot.toString1(x1,'') for x1 in x])

    @staticmethod
    def toString(x):
        return (("[" + HxOverrides.stringOrNull(",".join([python_Boot.toString1(x1,'') for x1 in x]))) + "]")

    @staticmethod
    def pop(x):
        if (len(x) == 0):
            return None
        else:
            return x.pop()

    @staticmethod
    def push(x,e):
        x.append(e)
        return len(x)

    @staticmethod
    def unshift(x,e):
        x.insert(0, e)

    @staticmethod
    def remove(x,e):
        try:
            x.remove(e)
            return True
        except BaseException as _g:
            None
            return False

    @staticmethod
    def contains(x,e):
        return (e in x)

    @staticmethod
    def shift(x):
        if (len(x) == 0):
            return None
        return x.pop(0)

    @staticmethod
    def slice(x,pos,end = None):
        return x[pos:end]

    @staticmethod
    def sort(x,f):
        x.sort(key= python_lib_Functools.cmp_to_key(f))

    @staticmethod
    def splice(x,pos,_hx_len):
        if (pos < 0):
            pos = (len(x) + pos)
        if (pos < 0):
            pos = 0
        res = x[pos:(pos + _hx_len)]
        del x[pos:(pos + _hx_len)]
        return res

    @staticmethod
    def map(x,f):
        return list(map(f,x))

    @staticmethod
    def filter(x,f):
        return list(filter(f,x))

    @staticmethod
    def insert(a,pos,x):
        a.insert(pos, x)

    @staticmethod
    def reverse(a):
        a.reverse()

    @staticmethod
    def _get(x,idx):
        if ((idx > -1) and ((idx < len(x)))):
            return x[idx]
        else:
            return None

    @staticmethod
    def _set(x,idx,v):
        l = len(x)
        while (l < idx):
            x.append(None)
            l = (l + 1)
        if (l == idx):
            x.append(v)
        else:
            x[idx] = v
        return v
python_internal_ArrayImpl._hx_class = python_internal_ArrayImpl


class HxOverrides:
    _hx_class_name = "HxOverrides"
    __slots__ = ()
    _hx_statics = ["iterator", "eq", "stringOrNull", "length", "modf", "mod", "arrayGet", "mapKwArgs"]

    @staticmethod
    def iterator(x):
        if isinstance(x,list):
            return haxe_iterators_ArrayIterator(x)
        return x.iterator()

    @staticmethod
    def eq(a,b):
        if (isinstance(a,list) or isinstance(b,list)):
            return a is b
        return (a == b)

    @staticmethod
    def stringOrNull(s):
        if (s is None):
            return "null"
        else:
            return s

    @staticmethod
    def length(x):
        if isinstance(x,str):
            return len(x)
        elif isinstance(x,list):
            return len(x)
        return x.length

    @staticmethod
    def modf(a,b):
        if (b == 0.0):
            return float('nan')
        elif (a < 0):
            if (b < 0):
                return -(-a % (-b))
            else:
                return -(-a % b)
        elif (b < 0):
            return a % (-b)
        else:
            return a % b

    @staticmethod
    def mod(a,b):
        if (a < 0):
            if (b < 0):
                return -(-a % (-b))
            else:
                return -(-a % b)
        elif (b < 0):
            return a % (-b)
        else:
            return a % b

    @staticmethod
    def arrayGet(a,i):
        if isinstance(a,list):
            x = a
            if ((i > -1) and ((i < len(x)))):
                return x[i]
            else:
                return None
        else:
            return a[i]

    @staticmethod
    def mapKwArgs(a,v):
        a1 = _hx_AnonObject(python_Lib.anonToDict(a))
        k = python_HaxeIterator(iter(v.keys()))
        while k.hasNext():
            k1 = k.next()
            val = v.get(k1)
            if a1._hx_hasattr(k1):
                x = getattr(a1,k1)
                setattr(a1,val,x)
                delattr(a1,k1)
        return a1
HxOverrides._hx_class = HxOverrides


class python_internal_MethodClosure:
    _hx_class_name = "python.internal.MethodClosure"
    __slots__ = ("obj", "func")
    _hx_fields = ["obj", "func"]
    _hx_methods = ["__call__"]

    def __init__(self,obj,func):
        self.obj = obj
        self.func = func

    def __call__(self,*args):
        return self.func(self.obj,*args)

python_internal_MethodClosure._hx_class = python_internal_MethodClosure


class HxString:
    _hx_class_name = "HxString"
    __slots__ = ()
    _hx_statics = ["split", "charCodeAt", "charAt", "lastIndexOf", "toUpperCase", "toLowerCase", "indexOf", "indexOfImpl", "toString", "get_length", "substring", "substr"]

    @staticmethod
    def split(s,d):
        if (d == ""):
            return list(s)
        else:
            return s.split(d)

    @staticmethod
    def charCodeAt(s,index):
        if ((((s is None) or ((len(s) == 0))) or ((index < 0))) or ((index >= len(s)))):
            return None
        else:
            return ord(s[index])

    @staticmethod
    def charAt(s,index):
        if ((index < 0) or ((index >= len(s)))):
            return ""
        else:
            return s[index]

    @staticmethod
    def lastIndexOf(s,_hx_str,startIndex = None):
        if (startIndex is None):
            return s.rfind(_hx_str, 0, len(s))
        elif (_hx_str == ""):
            length = len(s)
            if (startIndex < 0):
                startIndex = (length + startIndex)
                if (startIndex < 0):
                    startIndex = 0
            if (startIndex > length):
                return length
            else:
                return startIndex
        else:
            i = s.rfind(_hx_str, 0, (startIndex + 1))
            startLeft = (max(0,((startIndex + 1) - len(_hx_str))) if ((i == -1)) else (i + 1))
            check = s.find(_hx_str, startLeft, len(s))
            if ((check > i) and ((check <= startIndex))):
                return check
            else:
                return i

    @staticmethod
    def toUpperCase(s):
        return s.upper()

    @staticmethod
    def toLowerCase(s):
        return s.lower()

    @staticmethod
    def indexOf(s,_hx_str,startIndex = None):
        if (startIndex is None):
            return s.find(_hx_str)
        else:
            return HxString.indexOfImpl(s,_hx_str,startIndex)

    @staticmethod
    def indexOfImpl(s,_hx_str,startIndex):
        if (_hx_str == ""):
            length = len(s)
            if (startIndex < 0):
                startIndex = (length + startIndex)
                if (startIndex < 0):
                    startIndex = 0
            if (startIndex > length):
                return length
            else:
                return startIndex
        return s.find(_hx_str, startIndex)

    @staticmethod
    def toString(s):
        return s

    @staticmethod
    def get_length(s):
        return len(s)

    @staticmethod
    def substring(s,startIndex,endIndex = None):
        if (startIndex < 0):
            startIndex = 0
        if (endIndex is None):
            return s[startIndex:]
        else:
            if (endIndex < 0):
                endIndex = 0
            if (endIndex < startIndex):
                return s[endIndex:startIndex]
            else:
                return s[startIndex:endIndex]

    @staticmethod
    def substr(s,startIndex,_hx_len = None):
        if (_hx_len is None):
            return s[startIndex:]
        else:
            if (_hx_len == 0):
                return ""
            if (startIndex < 0):
                startIndex = (len(s) + startIndex)
                if (startIndex < 0):
                    startIndex = 0
            return s[startIndex:(startIndex + _hx_len)]
HxString._hx_class = HxString


class python_io_NativeInput(haxe_io_Input):
    _hx_class_name = "python.io.NativeInput"
    __slots__ = ("stream", "wasEof")
    _hx_fields = ["stream", "wasEof"]
    _hx_methods = ["close", "throwEof", "readinto", "readBytes"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_io_Input


    def __init__(self,s):
        self.wasEof = None
        self.stream = s
        self.set_bigEndian(False)
        self.wasEof = False
        if (not self.stream.readable()):
            raise haxe_Exception.thrown("Write-only stream")

    def close(self):
        self.stream.close()

    def throwEof(self):
        self.wasEof = True
        raise haxe_Exception.thrown(haxe_io_Eof())

    def readinto(self,b):
        raise haxe_Exception.thrown("abstract method, should be overridden")

    def readBytes(self,s,pos,_hx_len):
        if (((pos < 0) or ((_hx_len < 0))) or (((pos + _hx_len) > s.length))):
            raise haxe_Exception.thrown(haxe_io_Error.OutsideBounds)
        ba = bytearray(_hx_len)
        ret = self.readinto(ba)
        if (ret == 0):
            self.throwEof()
        s.blit(pos,haxe_io_Bytes.ofData(ba),0,_hx_len)
        return ret

python_io_NativeInput._hx_class = python_io_NativeInput


class python_io_IInput:
    _hx_class_name = "python.io.IInput"
    __slots__ = ("bigEndian",)
    _hx_fields = ["bigEndian"]
    _hx_methods = ["set_bigEndian", "readByte", "readBytes", "close", "readFullBytes", "readLine", "readString"]
python_io_IInput._hx_class = python_io_IInput


class python_io_IFileInput:
    _hx_class_name = "python.io.IFileInput"
    __slots__ = ()
    _hx_interfaces = [python_io_IInput]
python_io_IFileInput._hx_class = python_io_IFileInput


class python_io_NativeOutput(haxe_io_Output):
    _hx_class_name = "python.io.NativeOutput"
    __slots__ = ("stream",)
    _hx_fields = ["stream"]
    _hx_methods = ["close", "flush"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_io_Output


    def __init__(self,stream):
        self.stream = None
        self.set_bigEndian(False)
        self.stream = stream
        if (not stream.writable()):
            raise haxe_Exception.thrown("Read only stream")

    def close(self):
        self.stream.close()

    def flush(self):
        self.stream.flush()

python_io_NativeOutput._hx_class = python_io_NativeOutput


class python_io_NativeBytesOutput(python_io_NativeOutput):
    _hx_class_name = "python.io.NativeBytesOutput"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["writeByte", "writeBytes"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = python_io_NativeOutput


    def __init__(self,stream):
        super().__init__(stream)

    def writeByte(self,c):
        self.stream.write(bytearray([c]))

    def writeBytes(self,s,pos,_hx_len):
        return self.stream.write(s.b[pos:(pos + _hx_len)])

python_io_NativeBytesOutput._hx_class = python_io_NativeBytesOutput


class python_io_IOutput:
    _hx_class_name = "python.io.IOutput"
    __slots__ = ("bigEndian",)
    _hx_fields = ["bigEndian"]
    _hx_methods = ["set_bigEndian", "writeByte", "writeBytes", "flush", "close", "writeFullBytes", "writeString"]
python_io_IOutput._hx_class = python_io_IOutput


class python_io_IFileOutput:
    _hx_class_name = "python.io.IFileOutput"
    __slots__ = ()
    _hx_interfaces = [python_io_IOutput]
python_io_IFileOutput._hx_class = python_io_IFileOutput


class python_io_FileBytesOutput(python_io_NativeBytesOutput):
    _hx_class_name = "python.io.FileBytesOutput"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = [python_io_IFileOutput]
    _hx_super = python_io_NativeBytesOutput


    def __init__(self,stream):
        super().__init__(stream)
python_io_FileBytesOutput._hx_class = python_io_FileBytesOutput


class python_io_NativeTextInput(python_io_NativeInput):
    _hx_class_name = "python.io.NativeTextInput"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["readByte", "readinto"]
    _hx_statics = []
    _hx_interfaces = [python_io_IInput]
    _hx_super = python_io_NativeInput


    def __init__(self,stream):
        super().__init__(stream)

    def readByte(self):
        ret = self.stream.buffer.read(1)
        if (len(ret) == 0):
            self.throwEof()
        return ret[0]

    def readinto(self,b):
        return self.stream.buffer.readinto(b)

python_io_NativeTextInput._hx_class = python_io_NativeTextInput


class python_io_FileTextInput(python_io_NativeTextInput):
    _hx_class_name = "python.io.FileTextInput"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = [python_io_IFileInput]
    _hx_super = python_io_NativeTextInput


    def __init__(self,stream):
        super().__init__(stream)
python_io_FileTextInput._hx_class = python_io_FileTextInput


class python_io_NativeTextOutput(python_io_NativeOutput):
    _hx_class_name = "python.io.NativeTextOutput"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = ["writeBytes", "writeByte"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = python_io_NativeOutput


    def __init__(self,stream):
        super().__init__(stream)
        if (not stream.writable()):
            raise haxe_Exception.thrown("Read only stream")

    def writeBytes(self,s,pos,_hx_len):
        return self.stream.buffer.write(s.b[pos:(pos + _hx_len)])

    def writeByte(self,c):
        self.stream.write("".join(map(chr,[c])))

python_io_NativeTextOutput._hx_class = python_io_NativeTextOutput


class python_io_FileTextOutput(python_io_NativeTextOutput):
    _hx_class_name = "python.io.FileTextOutput"
    __slots__ = ()
    _hx_fields = []
    _hx_methods = []
    _hx_statics = []
    _hx_interfaces = [python_io_IFileOutput]
    _hx_super = python_io_NativeTextOutput


    def __init__(self,stream):
        super().__init__(stream)
python_io_FileTextOutput._hx_class = python_io_FileTextOutput


class python_io_IoTools:
    _hx_class_name = "python.io.IoTools"
    __slots__ = ()
    _hx_statics = ["createFileInputFromText", "createFileOutputFromText", "createFileOutputFromBytes"]

    @staticmethod
    def createFileInputFromText(t):
        return sys_io_FileInput(python_io_FileTextInput(t))

    @staticmethod
    def createFileOutputFromText(t):
        return sys_io_FileOutput(python_io_FileTextOutput(t))

    @staticmethod
    def createFileOutputFromBytes(t):
        return sys_io_FileOutput(python_io_FileBytesOutput(t))
python_io_IoTools._hx_class = python_io_IoTools


class sys_io_File:
    _hx_class_name = "sys.io.File"
    __slots__ = ()
    _hx_statics = ["append"]

    @staticmethod
    def append(path,binary = None):
        if (binary is None):
            binary = True
        mode = ("ab" if binary else "a")
        f = python_lib_Builtins.open(path,mode,-1,None,None,(None if binary else ""))
        if binary:
            return python_io_IoTools.createFileOutputFromBytes(f)
        else:
            return python_io_IoTools.createFileOutputFromText(f)
sys_io_File._hx_class = sys_io_File


class sys_io_FileInput(haxe_io_Input):
    _hx_class_name = "sys.io.FileInput"
    __slots__ = ("impl",)
    _hx_fields = ["impl"]
    _hx_methods = ["set_bigEndian", "readByte", "readBytes", "close", "readFullBytes", "readLine", "readString"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_io_Input


    def __init__(self,impl):
        self.impl = impl

    def set_bigEndian(self,b):
        return self.impl.set_bigEndian(b)

    def readByte(self):
        return self.impl.readByte()

    def readBytes(self,s,pos,_hx_len):
        return self.impl.readBytes(s,pos,_hx_len)

    def close(self):
        self.impl.close()

    def readFullBytes(self,s,pos,_hx_len):
        self.impl.readFullBytes(s,pos,_hx_len)

    def readLine(self):
        return self.impl.readLine()

    def readString(self,_hx_len,encoding = None):
        return self.impl.readString(_hx_len)

sys_io_FileInput._hx_class = sys_io_FileInput


class sys_io_FileOutput(haxe_io_Output):
    _hx_class_name = "sys.io.FileOutput"
    __slots__ = ("impl",)
    _hx_fields = ["impl"]
    _hx_methods = ["set_bigEndian", "writeByte", "writeBytes", "flush", "close", "writeFullBytes", "writeString"]
    _hx_statics = []
    _hx_interfaces = []
    _hx_super = haxe_io_Output


    def __init__(self,impl):
        self.impl = impl

    def set_bigEndian(self,b):
        return self.impl.set_bigEndian(b)

    def writeByte(self,c):
        self.impl.writeByte(c)

    def writeBytes(self,s,pos,_hx_len):
        return self.impl.writeBytes(s,pos,_hx_len)

    def flush(self):
        self.impl.flush()

    def close(self):
        self.impl.close()

    def writeFullBytes(self,s,pos,_hx_len):
        self.impl.writeFullBytes(s,pos,_hx_len)

    def writeString(self,s,encoding = None):
        self.impl.writeString(s)

sys_io_FileOutput._hx_class = sys_io_FileOutput


class sys_io_Process:
    _hx_class_name = "sys.io.Process"
    __slots__ = ("stdout", "stderr", "stdin", "p")
    _hx_fields = ["stdout", "stderr", "stdin", "p"]
    _hx_methods = ["close"]

    def __init__(self,cmd,args = None,detached = None):
        self.stdin = None
        self.stderr = None
        self.stdout = None
        if detached:
            raise haxe_Exception.thrown("Detached process is not supported on this platform")
        args1 = (cmd if ((args is None)) else ([cmd] + args))
        o = _hx_AnonObject({'shell': (args is None), 'stdin': python_lib_Subprocess.PIPE, 'stdout': python_lib_Subprocess.PIPE, 'stderr': python_lib_Subprocess.PIPE})
        Reflect.setField(o,"bufsize",(Reflect.field(o,"bufsize") if (python_Boot.hasField(o,"bufsize")) else 0))
        Reflect.setField(o,"executable",(Reflect.field(o,"executable") if (python_Boot.hasField(o,"executable")) else None))
        Reflect.setField(o,"stdin",(Reflect.field(o,"stdin") if (python_Boot.hasField(o,"stdin")) else None))
        Reflect.setField(o,"stdout",(Reflect.field(o,"stdout") if (python_Boot.hasField(o,"stdout")) else None))
        Reflect.setField(o,"stderr",(Reflect.field(o,"stderr") if (python_Boot.hasField(o,"stderr")) else None))
        Reflect.setField(o,"preexec_fn",(Reflect.field(o,"preexec_fn") if (python_Boot.hasField(o,"preexec_fn")) else None))
        Reflect.setField(o,"close_fds",(Reflect.field(o,"close_fds") if (python_Boot.hasField(o,"close_fds")) else None))
        Reflect.setField(o,"shell",(Reflect.field(o,"shell") if (python_Boot.hasField(o,"shell")) else None))
        Reflect.setField(o,"cwd",(Reflect.field(o,"cwd") if (python_Boot.hasField(o,"cwd")) else None))
        Reflect.setField(o,"env",(Reflect.field(o,"env") if (python_Boot.hasField(o,"env")) else None))
        Reflect.setField(o,"universal_newlines",(Reflect.field(o,"universal_newlines") if (python_Boot.hasField(o,"universal_newlines")) else None))
        Reflect.setField(o,"startupinfo",(Reflect.field(o,"startupinfo") if (python_Boot.hasField(o,"startupinfo")) else None))
        Reflect.setField(o,"creationflags",(Reflect.field(o,"creationflags") if (python_Boot.hasField(o,"creationflags")) else 0))
        self.p = (python_lib_subprocess_Popen(args1,Reflect.field(o,"bufsize"),Reflect.field(o,"executable"),Reflect.field(o,"stdin"),Reflect.field(o,"stdout"),Reflect.field(o,"stderr"),Reflect.field(o,"preexec_fn"),Reflect.field(o,"close_fds"),Reflect.field(o,"shell"),Reflect.field(o,"cwd"),Reflect.field(o,"env"),Reflect.field(o,"universal_newlines"),Reflect.field(o,"startupinfo"),Reflect.field(o,"creationflags")) if ((Sys.systemName() == "Windows")) else python_lib_subprocess_Popen(args1,Reflect.field(o,"bufsize"),Reflect.field(o,"executable"),Reflect.field(o,"stdin"),Reflect.field(o,"stdout"),Reflect.field(o,"stderr"),Reflect.field(o,"preexec_fn"),Reflect.field(o,"close_fds"),Reflect.field(o,"shell"),Reflect.field(o,"cwd"),Reflect.field(o,"env"),Reflect.field(o,"universal_newlines"),Reflect.field(o,"startupinfo")))
        self.stdout = python_io_IoTools.createFileInputFromText(python_lib_io_TextIOWrapper(python_lib_io_BufferedReader(self.p.stdout)))
        self.stderr = python_io_IoTools.createFileInputFromText(python_lib_io_TextIOWrapper(python_lib_io_BufferedReader(self.p.stderr)))
        self.stdin = python_io_IoTools.createFileOutputFromText(python_lib_io_TextIOWrapper(python_lib_io_BufferedWriter(self.p.stdin)))

    def close(self):
        ver = python_lib_Sys.version_info
        if ((ver[0] > 3) or (((ver[0] == 3) and ((ver[1] >= 3))))):
            try:
                self.p.terminate()
            except BaseException as _g:
                None
                if (not Std.isOfType(haxe_Exception.caught(_g).unwrap(),ProcessLookupError)):
                    raise _g
        else:
            try:
                self.p.terminate()
            except BaseException as _g:
                None
                if (not Std.isOfType(haxe_Exception.caught(_g).unwrap(),OSError)):
                    raise _g

sys_io_Process._hx_class = sys_io_Process

Math.NEGATIVE_INFINITY = float("-inf")
Math.POSITIVE_INFINITY = float("inf")
Math.NaN = float("nan")
Math.PI = python_lib_Math.pi

DateTools.DAY_SHORT_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
DateTools.DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DateTools.MONTH_SHORT_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DateTools.MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
com_sdtk_calendar_ConsoleFormat.instance = com_sdtk_calendar_ConsoleFormat()
com_sdtk_calendar_ICS.instance = com_sdtk_calendar_ICS()
com_sdtk_calendar_TableFormat.instance = com_sdtk_calendar_TableFormat()
com_sdtk_graphs_GrapherHTMLExporter._instance = com_sdtk_graphs_GrapherHTMLExporter()
com_sdtk_graphs_GrapherSVGExporter._instance = com_sdtk_graphs_GrapherSVGExporter()
com_sdtk_graphs_GrapherTEXExporter._instance = com_sdtk_graphs_GrapherTEXExporter()
com_sdtk_std_StringReaderEachChar.instance = com_sdtk_std_StringReaderEachChar()
com_sdtk_std_StringReaderEachLine.instance = com_sdtk_std_StringReaderEachLine()
com_sdtk_std_Version._code = "0.1.5"
com_sdtk_table_Stopwatch._watches = haxe_ds_StringMap()
com_sdtk_table_Stopwatch._defaultActual = False
com_sdtk_table_Stopwatch._null = None
com_sdtk_table_DataTableRowReader._watch = com_sdtk_table_Stopwatch.getStopwatch("fromStringToType")
com_sdtk_table_CMDDirHandler.OPTION_BARE = 1
com_sdtk_table_CMDDirHandler.OPTION_FULL_PATH = 2
com_sdtk_table_CMDDirHandler.OPTION_SHORT_NAME = 4
com_sdtk_table_CMDDirHandler.OPTION_OWNER_NAME = 8
com_sdtk_table_CMDDirHandler.OPTION_TRUE_NAME = 16
com_sdtk_table_CMDDirHandler.OPTION_COMMAS = 32
com_sdtk_table_CMDDirHandler.OPTION_LOWER_CASE_NAMES = 64
com_sdtk_table_CMDDirHandler.instance = com_sdtk_table_CMDDirHandler()
com_sdtk_table_CSVInfo.instance = com_sdtk_table_CSVInfo()
com_sdtk_table_CSharpInfoArrayOfArrays.instance = com_sdtk_table_CSharpInfoArrayOfArrays()
com_sdtk_table_CSharpInfoArrayOfMaps.instance = com_sdtk_table_CSharpInfoArrayOfMaps()
com_sdtk_table_CSharpInfoMapOfArrays.instance = com_sdtk_table_CSharpInfoMapOfArrays()
com_sdtk_table_CSharpInfoMapOfMaps.instance = com_sdtk_table_CSharpInfoMapOfMaps()
com_sdtk_table_CodeRowWriter._watch = com_sdtk_table_Stopwatch.getStopwatch("CodeRowWriter")
com_sdtk_table_Converter._watch = com_sdtk_table_Stopwatch.getStopwatch("Converter")
com_sdtk_table_ConverterStageSort._watch = com_sdtk_table_Stopwatch.getStopwatch("ConverterStageSort")
com_sdtk_table_DatabaseReader._mappings = None
com_sdtk_table_DatabaseReader._finalMappings = None
com_sdtk_table_DatabaseReader._columnMappings = None
com_sdtk_table_DatabaseReader._retrievalTypes = haxe_ds_StringMap()
com_sdtk_table_DatabaseReader._retrievalPrepTypes = haxe_ds_StringMap()
com_sdtk_table_DelimitedRowReader._watch = com_sdtk_table_Stopwatch.getStopwatch("DelimitedRowReader")
com_sdtk_table_DelimitedRowWriter._watch = com_sdtk_table_Stopwatch.getStopwatch("DelimitedRowWriter")
com_sdtk_table_FileInfo.IS_DIRECTORY = 1
com_sdtk_table_FileInfo.IS_JUNCTION = 2
com_sdtk_table_FileSystemRowReader._fields = ["Drive", "Label", "Serial", "Directory", "Owner", "File", "Short", "True", "Modified", "Size", "Type"]
com_sdtk_table_HaxeInfoArrayOfArrays.instance = com_sdtk_table_HaxeInfoArrayOfArrays()
com_sdtk_table_HaxeInfoArrayOfMaps.instance = com_sdtk_table_HaxeInfoArrayOfMaps()
com_sdtk_table_HaxeInfoMapOfArrays.instance = com_sdtk_table_HaxeInfoMapOfArrays()
com_sdtk_table_HaxeInfoMapOfMaps.instance = com_sdtk_table_HaxeInfoMapOfMaps()
com_sdtk_table_INIHandler.instance = com_sdtk_table_INIHandler()
com_sdtk_table_JSONHandler.instance = com_sdtk_table_JSONHandler()
com_sdtk_table_JavaInfoArrayOfArrays.instance = com_sdtk_table_JavaInfoArrayOfArrays()
com_sdtk_table_JavaInfoArrayOfMaps.instance = com_sdtk_table_JavaInfoArrayOfMaps()
com_sdtk_table_JavaInfoArrayOfMapsLegacy.instance = com_sdtk_table_JavaInfoArrayOfMapsLegacy()
com_sdtk_table_JavaInfoMapOfArrays.instance = com_sdtk_table_JavaInfoMapOfArrays()
com_sdtk_table_JavaInfoMapOfArraysLegacy.instance = com_sdtk_table_JavaInfoMapOfArraysLegacy()
com_sdtk_table_JavaInfoMapOfMaps.instance = com_sdtk_table_JavaInfoMapOfMaps()
com_sdtk_table_JavaInfoMapOfMapsLegacy.instance = com_sdtk_table_JavaInfoMapOfMapsLegacy()
com_sdtk_table_NullRowWriter.instance = com_sdtk_table_NullRowWriter()
com_sdtk_table_PSVInfo.instance = com_sdtk_table_PSVInfo()
com_sdtk_table_PropertiesHandler.instance = com_sdtk_table_PropertiesHandler()
com_sdtk_table_PythonInfoArrayOfArrays.instance = com_sdtk_table_PythonInfoArrayOfArrays()
com_sdtk_table_PythonInfoArrayOfMaps.instance = com_sdtk_table_PythonInfoArrayOfMaps()
com_sdtk_table_PythonInfoMapOfArrays.instance = com_sdtk_table_PythonInfoMapOfArrays()
com_sdtk_table_PythonInfoMapOfMaps.instance = com_sdtk_table_PythonInfoMapOfMaps()
com_sdtk_table_RAWInfo.instance = com_sdtk_table_RAWInfo()
com_sdtk_table_SQLSelectInfo.instance = com_sdtk_table_SQLSelectInfo()
com_sdtk_table_SplunkHandler.instance = com_sdtk_table_SplunkHandler()
com_sdtk_table_StandardTableInfo.instance = com_sdtk_table_StandardTableInfo()
com_sdtk_table_TSVInfo.instance = com_sdtk_table_TSVInfo()
com_sdtk_table_TeXInfo.instance = com_sdtk_table_TeXInfo()
com_sdtk_table_Tests.sCSV = "A,B,C\n5,6,7\n1,2,3\n8,1,5"
com_sdtk_table_Tests.sPASSED = "Passed"
com_sdtk_table_Tests.sFAILED = "Failed"
com_sdtk_table_Tests.sEXPECTED = "Expected"
com_sdtk_table_Tests.sGOT = "Got"
com_sdtk_table_Tests.sEXCEPTION = "Exception"
python_Boot.keywords = set(["and", "del", "from", "not", "with", "as", "elif", "global", "or", "yield", "assert", "else", "if", "pass", "None", "break", "except", "import", "raise", "True", "class", "exec", "in", "return", "False", "continue", "finally", "is", "try", "def", "for", "lambda", "while"])
python_Boot.prefixLength = len("_hx_")
python_Lib.lineEnd = ("\r\n" if ((Sys.systemName() == "Windows")) else "\n")