# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 00:25:36 2021

@author: VezoR
"""

import psycopg2
from datetime import datetime, date
import dateutil.relativedelta
import xgboost as xgb

#split the intake to list:
def splitter(intake):
    idtake = str(intake)
    idtake = idtake.replace('[', '')
    idtake = idtake.replace(']', '')
    idtake = idtake.replace('(', '')
    idtake = idtake.replace(')', '')
    idtake = idtake.replace(',', '')
    return list(idtake.split())

class Converter(object):
    #convert url to domen names:
    def convert(url):
        converted = url.replace('https://', '')
        converted = converted.replace('http://', '')
        converted = converted.replace('/', '')
        converted = converted.replace('.', ' ')
        converted = converted.replace('www', '')
        converted = converted.split()
        domen1 = str(converted[1])
        domen2 = str(converted[0])
        return domen1, domen2
        
class Loader(object):        
    
    def load_to_DB(wordscount, pagescount, numoptim, popularind, advind, attendance, domen1, domen2):
        '''

        Parameters
        ----------
        wordscount : int
            count of words
        pagescount : int
            count of pages
        numoptim : fload
            number of optimization of the site
        popularind : float
            index or pupulation of the site
        advind : float
            index of adverts of the site
        attendance : list
            attendance of the site since 6 month
        domen1 : string
            level 1 of site domen 
        domen2 : string
            level 2 of site domen

        Returns
        -------
        None.

        '''
        date = datetime.now()
        date_ = date.date()
    
        conn = psycopg2.connect(dbname='AttendancePredictor', user='postgres', 
                                password='PostgreSQL000.', host='localhost')
        cursor = conn.cursor()
        
        #reques of parser table to insert:
        cursor.execute('INSERT INTO parser (wordscount, pagescount, numoptim, popularind, advind, dateframe)' \
                       'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;', 
                       [wordscount, pagescount, numoptim, popularind, advind, date_])
        cursor.execute('SELECT last_value(id) OVER (ORDER BY parser.id) FROM parser')
        idfrom  = list(cursor.fetchall())
        idtake = idfrom[len(idfrom)-1]
        id_ = int(''.join(map(str, idtake)))
        cursor.execute('INSERT INTO resource (parse, domen1, domen2, dateframe, attendance)' \
                       'VALUES (%s, %s, %s, %s, %s) RETURNING id;', 
                       [id_, domen1, domen2, date_, attendance])
        
        conn.commit()
        cursor.close()
        
    def unload_from_DB(domen1, domen2):
        '''
        
        Parameters
        ----------
        domen1 : string
            level 1 of site domen 
        domen2 : string
            level 2 of site domen

        Returns
        -------
        wordscount : int
            count of words
        pagescount : int
            count of pages
        numoptim : fload
            number of optimization of the site
        popularind : float
            index or pupulation of the site
        advind : float
            index of adverts of the site
        attendance : list
            attendance of the site since 6 month

        '''
        
        #setting the interval of unloading data:
        date = datetime.now()
        date_ = date.date()
        datedelta = date_ - dateutil.relativedelta.relativedelta(months=1)
        conn = psycopg2.connect(dbname='AttendancePredictor', user='postgres', 
                                password='PostgreSQL000.', host='localhost')
        cursor = conn.cursor()
        
        #request of getting id from last:
        cursor.execute('SELECT parse, attendance FROM resource WHERE domen1 = %s and domen2 = %s' \
                       'and dateframe >= %s and id=(SELECT max(id) FRoM resource)',
                       [domen1, domen2, datedelta])
        split = splitter(cursor.fetchall())
        
        #request of getting returned values:
        cursor.execute('SELECT wordscount, pagescount, numoptim, popularind, advind ' \
                       'FROM parser WHERE id = %s',
                       [split[0]])
        outtake = splitter(cursor.fetchall())
        
        conn.commit()
        cursor.close()
        
        #retaking of:
        wordscount = int(outtake[0])
        pagescount = int(outtake[1])
        numoptim = float(outtake[2])
        popularind = float(outtake[3])
        advind =  float(outtake[4])
        attend = split[1:7]
        attendance = [int(a) for a in attend]
        return wordscount, pagescount, numoptim, popularind, advind, attendance

    def load_model (weights, accuracy):
        '''

        Parameters
        ----------
        weights : list of floats
            weights of the model
        accuracy : float
            accuracy of the model

        Returns
        -------
        None.

        '''
        conn = psycopg2.connect(dbname='AttendancePredictor', user='postgres', 
                                password='PostgreSQL000.', host='localhost')
        cursor = conn.cursor()
        
        #request of model data to insert:
        cursor.execute('INSERT INTO model (weights, accuracy)' \
                               'VALUES (%s, %s) RETURNING id;', 
                               [weights, accuracy])
        conn.commit()
        cursor.close()        
        
    def unload_model (best_accuracy, accuracy):
        '''
        
        Parameters
        ----------
        best_accuracy : bool
            the best accuracy of model
            
        accuracy : float
            (optional) desired accuracy of the model

        Returns
        -------
        weights : list of floats
            weights of the model

        '''
        conn = psycopg2.connect(dbname='AttendancePredictor', user='postgres', 
                                password='PostgreSQL000.', host='localhost')
        cursor = conn.cursor()
        
        #request of model data to select:
        if best_accuracy:
            cursor.execute('SELECT weights, accuracy FROM model ' \
                           'WHERE accuracy=(SELECT max(accuracy) FROM model)')
        else:
            cursor.execute('SELECT weights, accuracy FROM model ' \
                           'WHERE accuracy = %s',
                           [accuracy])
        
        weights_ = splitter(cursor.fetchall())
        weights = [float(a) for a in weights_]
        conn.commit()
        cursor.close()
        return weights

class Model(object):
    
    def train_at_DB(num, params):
        pass
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

