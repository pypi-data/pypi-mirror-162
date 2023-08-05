import pandas
import pytz
import csv

from re import match
from loguru import logger
from tzlocal import get_localzone
from datetime import datetime
from pathlib import Path


class UtilsProperty():
    def _getDataTypes(properties:dict) -> dict:
        """
        Sorts the property types and returns a dictionary of those properties 
        that are not of type STRING.
        """ 

        logger.debug(properties)
        propertyTypes = {'Boolean': [], 'Numeric': [], 'DateTime': [], 'String': [], 'Unknown': []}
        if 'dataType' not in properties[0]:
            return propertyTypes

        for property in properties:
            if property['dataType'] in ['DATE_TIME', 'DATE_TIME_OFFSET']:
                propertyTypes['DateTime'].append(property['name'])
            elif property['dataType'] == 'BOOLEAN':
                propertyTypes['Boolean'].append(property['name'])
            elif property['dataType'] in ['INT', 'LONG', 'DECIMAL']:
                propertyTypes['Numeric'].append(property['name'])
                
            elif property['dataType'] == 'STRING':
                propertyTypes['String'].append(property['name'])
            else: 
                propertyTypes['Unknown'].append(property['name'])
        return propertyTypes

    def _getArrays(properties:dict) -> list:
        """ Lists properties that are arrays (isArray) """

        p = [property['name'] for property in properties if property['isArray'] == True]
        return p

    def _getNullables(properties:dict) -> list:
        """ Lists properties that are nullable """

        p = [property['name'] for property in properties if property['nullable'] == True]
        return p

    def _getReferences(properties:dict) -> list:
        """ Lists properties that are nullable """

        p = [property['name'] for property in properties if property['type'] == 'reference']
        return p

    def _transformBool(value:str):
        trueValues = ['ja', 'Ja', 'yes', 'Yes', 'True', 'true', 1]
        falseValues = ['nein', 'Nein', 'no', 'No', 'false','False',0]
        if value in trueValues:
            return True
        elif value in falseValues:
            return False
        return None

    def _isInt(n:str):
        return bool(match(r'-?\d+$', n))

    def _isFloat(n:str) -> bool:
        return bool(match(r'-?\d+(\.\d+)$', n))

    def _transformNumeric(value:str):
        if UtilsProperty._isInt(value):
            return int(value)
        elif UtilsProperty._isFloat(value):
            return float(value)
        else:
            logger.warning(f"'{value}' is not of numeric data type!")

    def _checkIsList(pythonList:str) -> bool:
        if pythonList[0] != '[':
            return False
        elif pythonList[-1] != ']':
            return False
        else:
            return True

    def _transformList(pythonList:str, propertyType:str) -> list:
        """ Transforms a String into a Python list"""
        if not UtilsProperty._checkIsList(pythonList):
            #logger.warning(f"Value '{pythonList}' is not array type, try to transform...")
            pythonList = '[' + pythonList + ']'

        pythonList = pythonList[1:-1].split(',')
        pythonList = [element.strip() for element in pythonList]

        _pythonList = []
        for element in pythonList:
            if propertyType == 'Numeric':
                _pythonList.append(UtilsProperty._transformNumeric(element))
            elif propertyType == 'Boolean':
                _pythonList.append(UtilsProperty._transformBool(element))
            else:
                _pythonList.append(str(element))

        return _pythonList

class FileUtils(UtilsProperty):

    def _createItems(content:list, dataType:dict, isArray:list, nullable:list, referenceMapping=None, type=None):
        
        def _createItem():
            if i == 0: return
            if len(row) < 1: return
            else:
                if type == None:
                    item = {}
                if type == 'timeSeries':
                    item = {'resolution': {}}
                for j, field in enumerate(row):
                    if not field:
                        if header[j] in nullable:
                            continue
                        elif header[j] not in nullable and len(field) > 0:
                            logger.warning(f"Line {i}, field '{header[j]}': Value missing for non nullable property.")
                            return
                        else:
                            pass
                    else:
                        if referenceMapping != None and header[j] in referenceMapping:
                            parentHeader = header[j].split('.')[0]
                            if parentHeader in isArray:
                                nameList = UtilsProperty._transformList(field, 'String')
                                try:
                                    idList = [referenceMapping[header[j]][item] for item in nameList]
                                except KeyError as key:
                                    logger.warning(f"Line {i}, field '{header[j]}': {key} is not a valid reference.")
                                    return
                                item.setdefault(parentHeader, idList)
                            else:
                                try:
                                    item.setdefault(parentHeader, referenceMapping[header[j]][field])
                                except KeyError as key:
                                    logger.warning(f"Line {i}, field '{header[j]}': {key} is not a valid reference.")
                                    return
                        else:
                            if header[j] in dataType['Boolean']:
                                if header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(field, 'Boolean'))
                                else: 
                                    item.setdefault(header[j], UtilsProperty._transformBool(field))
                            elif header[j] in dataType['Numeric']:
                                if header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(field,'Numeric'))
                                else:
                                    item.setdefault(header[j], UtilsProperty._transformNumeric(field))
                            elif header[j] in dataType['DateTime']:
                                if header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(field, 'DateTime'))
                                else:
                                    #item.setdefault(header[j], FileUtils._convertTimestamp(field, timeZone, FileUtils._dateFormat(field)))
                                    item.setdefault(header[j], field)
                            else:
                                if type == 'timeSeries' and header[j] == 'timeUnit':
                                    item['resolution'].setdefault('timeUnit', field)
                                elif type == 'timeSeries' and header[j] == 'factor':
                                    item['resolution'].setdefault('factor', field)
                                elif header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(field, 'String'))
                                else:
                                    item.setdefault(header[j], field)
                return item
                    
        itemList = []
        header = content[0]
        for i, row in enumerate(content):
            item = _createItem()
            if item != None:           
                itemList.append(item)

        return itemList          

 

    def _createInstanceItems(content:list, dataType:dict, isArray:list, nullable:list, idMapping:dict=None, 
        transpose:bool=False) -> list:

        if transpose == True:
            content = list(map(list, zip(*content)))

        for column in content:
            if column[0] in ['unit', 'timeUnit', 'factor']:
                del column

        itemList = []
        header = content[0]
        for i, row in enumerate(content):
            itemOkay = True # is changed to false, if certain criteria are not met -> warning message, next item
            if i == 0: continue
            if len(row) < 1: continue
            else:
                if idMapping != None:
                    try:
                        groupInventoryItemId = idMapping[content[i][0]]
                    except:
                        logger.warning(f"ImportKeyProperty '{content[i][0]}' not found.")
                        continue
                else:
                    groupInventoryItemId = content[i][0]
                item = {'sys_groupInventoryItemId':groupInventoryItemId}
                for j, field in enumerate(row):
                    if j == 0: continue
                        
                    if not field:
                        if header[j] in nullable:
                            continue
                        elif header[j] not in nullable and len(field) > 0:
                            logger.warning(f"Value missing for non nullable {header[j]}. Item from line {i} not imported.")
                            itemOkay = False
                            break
                        else:
                            pass
                    else:
                        if header[j] in dataType['Boolean']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'Boolean'))
                            else: 
                                item.setdefault(header[j], UtilsProperty._transformBool(field))
                        elif header[j] in dataType['Numeric']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field,'Numeric'))
                            else:
                                item.setdefault(header[j], UtilsProperty._transformNumeric(field))
                        elif header[j] in dataType['DateTime']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'DateTime'))
                            else:
                                #item.setdefault(header[j], UtilsProperty._convertTimestamp(field, timeZone))
                                item.setdefault(header[j], field)
                        else:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'String'))
                            else:
                                item.setdefault(header[j], field)
                if itemOkay and len(item) > 0:
                    itemList.append(item)

        return itemList

    def _createTimeSeriesItems(content:list, dataType:dict, isArray:list, nullable:list):
        itemList = []
        header = content[0]
        for i, row in enumerate(content):
            itemOkay = True # is changed to false, if certain criteria are not met -> warning message, next item
            if i == 0: continue
            if len(row) < 1: continue
            else:
                item = {'resolution': {}}
                for j, field in enumerate(row):
                    if not field:
                        if header[j] in nullable:
                            continue
                        elif header[j] not in nullable and len(field) > 0:
                            logger.warning(f"Value missing for non nullable {header[j]}. Item from line {i} not imported.")
                            itemOkay = False
                            break
                        else:
                            pass
                    else:
                        if header[j] in dataType['Boolean']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'Boolean'))
                            else: 
                                item.setdefault(header[j], UtilsProperty._transformBool(field))
                        elif header[j] in dataType['Numeric']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field,'Numeric'))
                            else:
                                item.setdefault(header[j], UtilsProperty._transformNumeric(field))
                        elif header[j] in dataType['DateTime']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'DateTime'))
                            else:
                                #item.setdefault(header[j], UtilsProperty._convertTimestamp(field, timeZone))
                                item.setdefault(header[j], field)
                        else:
                            if header[j] == 'timeUnit':
                                item['resolution'].setdefault('timeUnit', field)
                            elif header[j] == 'factor':
                                item['resolution'].setdefault('factor', field)
                            else:
                                if header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(field, 'String'))
                                else:
                                    item.setdefault(header[j], field)
                if itemOkay and len(item) > 0:
                    itemList.append(item)

        return itemList

    def _comparePropertiesBasic(properties:list, header:list) -> None:
        """ Compares header with requested properties from a basic inventory. """

        properties = set(properties)
        header = set(header)
        return header.difference(properties)

    def _comparePropertiesTimeSeries(properties:list, header:list) -> None:
        """ Compares header with requested properties from a time series inventory. """

        properties = set(properties)
        header = set(header)
        tsProperties = set(['timeUnit', 'factor', 'unit'])
        header = header - tsProperties
        return header.difference(properties)

    def _analyzeProperties(inventoryName:str, properties:pandas.DataFrame) -> tuple:
        """ Analyzes inventory properties and returns dictionaries to each property attribute """

        #properties = properties[['name', 'dataType', 'isArray', 'nullable']].to_dict('records')
        properties = properties.to_dict('records')
        dataType = UtilsProperty._getDataTypes(properties)
        isArray = UtilsProperty._getArrays(properties)
        nullable = UtilsProperty._getNullables(properties)
        isReference = UtilsProperty._getReferences(properties)

        logger.debug(f'Data types: {dataType}')
        logger.debug(f'Array properties: {isArray}')
        logger.debug(f'Nullable properties: {nullable}')
        logger.debug(f'Reference properties: {isReference}')

        return dataType, isArray, nullable

    def _timeZone(timeZone):
        if timeZone==None: 
            localTimeZone = get_localzone().zone
            return str(pytz.timezone(localTimeZone))
        else:
            return str(pytz.timezone(timeZone))

    def _timeZoneItems(timeZone):
        if timeZone==None: 
            localTimeZone = get_localzone().zone
            return str(pytz.timezone(localTimeZone))
        else:
            return str(pytz.timezone('UTC'))

    def _convertTimestamp(timestamp, timeZone, dateTimeFormat, timeDelta):

        timestamp = datetime.strptime(timestamp, dateTimeFormat)
        if timeDelta != None:
            timestamp += timeDelta
        timestamp = pytz.timezone(timeZone).localize(timestamp).isoformat()
        return timestamp

    def _dateFormat(timestamp:str) -> str:

        # German
        if match(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%d.%m.%Y %H:%M:%S.%f'
        if match(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M:%S'
        if match(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M'
        if match(r'\d{2}.\d{2}.\d{4}', timestamp):
            return '%d.%m.%Y'

        # ISO
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%f+00:00'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S+00:00'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%fZ'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%f'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', timestamp):
            return '%Y-%m-%dT%H:%M:%SZ'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M'

        # English I
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S.%f+00:00'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S+00:00'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y-%m-%d %H:%M:%S.%f'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M'
        if match(r'\d{4}-\d{2}-\d{2}', timestamp):
           return '%Y-%m-%d'
               
        # English II
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y/%m/%d %H:%M:%S.%f'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M:%S'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M'
        if match(r'\d{4}/\d{2}/\d{2}', timestamp):
            return '%Y/%m/%d'

        # English III
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M:%S'
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M'
        if match(r'\d{1,2}/\d{1,2}/\d{4}', timestamp):
            return '%m/%d/%Y'

        return None

    def _createInstanceItemContent(content):
        itemContent = []
        for row in content:
            if row[0] not in ['unit', 'timeUnit', 'factor']:
                itemContent.append(row)

        return itemContent

    def _checkFilePath(filePath, raiseException):
        """Checks and handles the file path"""
        filePath = Path(filePath)
        if str(filePath).lower().endswith('csv'):
            if not filePath.exists():
                msg = f"File path {filePath} does not exist"
                if raiseException: raise Exception(msg)
                else:
                    logger.error(msg)
                    return 
            return [filePath]

        else:
            if not filePath.exists():
                msg = f"File path {filePath} does not exist"
                if raiseException: raise Exception(msg)
                else:
                    logger.error(msg)
                    return 
            files = [file for file in filePath.iterdir() if str(file).lower().endswith('csv')]
            msg = f"No csv files found in {filePath}"
            if len(files) == 0:
                if raiseException: raise Exception(msg)
                else:
                    logger.error(msg)
                    return
            logger.debug(f"FileUtils._checkFilePath: {files}")
            return files

    def _readCsvFile(file, delimiter) -> list:
        with open(file) as f:
            csv_file = csv.reader(f, delimiter=delimiter)
            content = [row for row in csv_file]
            logger.debug(f"CSV file '{file.name}' read.")
        return content
            
    def _checkReferences(fields:list) -> list:
        """
        Checks, if reference fields have multilevel and returns a list of one-level
        fields and error an list
        """
        references = []
        errors = []
        for field in fields:
            if field.count('.') == 0:
                continue
            elif field.count('.') == 1:
                references.append(field)
            elif field.count('.') > 1:
                errors.append(field)
            else:
                pass

        return references, errors

    def _createReferenceMapping(client, inventoryName:str, referenceFields:list, isArray:list, content:list, ) -> dict:
        """
        Creates a dictionary of mapping inventoryItemIds with the import items of reference.
        """
        references = {}
        content = pandas.DataFrame(content[1:], columns=content[0])
        for field in referenceFields:
            parentField = field.split('.')[0]
            childField = field.split('.')[1]
            sysId = False
            if childField == 'sys_inventoryItemId':
                sysId = True
            if parentField in isArray:
                listOfLists = []
                for item in content[field]:
                    if len(item) == 0:
                        continue
                    listOfLists.append(UtilsProperty._transformList(item, 'String'))
                nameList = list(set().union(*listOfLists))
            else:
                nameList = list(set(content[field]))
            
            if sysId == False:
                inventory = client.structure[inventoryName]['properties'][parentField]['inventoryName']
                df = client.items(inventory, fields=['sys_inventoryItemId', childField], where=f'{childField} in {nameList}')
                mapping = {item[1][childField]: item[1]['sys_inventoryItemId'] for item in df.iterrows()}
            else:
                mapping = {item: item for item in nameList}
            
            references.setdefault(field, mapping)

        return references