import csv
import json
from one_py_sdk.operations.spreadsheet import SpreadsheetApi
from one_py_sdk.common.library import LibraryApi
from one_py_sdk.enterprise.twin import DigitalTwinApi
from one_py_sdk.shared.helpers.datetimehelper import *
from datetime import datetime, timezone

class Exporter:
    def __init__(self, env, auth):
        self.Environment = env
        self.Authentication = auth
        self.Spreadsheet = SpreadsheetApi(env, auth)
        self.Library = LibraryApi(env, auth)
        self.DigitalTwin = DigitalTwinApi(env, auth)                                                      
    dataFieldNames = ['Worksheet Type', 'Time', 'ColumnName','ColumnId','RowNumber', 'Value', 'StringValue', 'DateEntered', 'ChangedUsing']    
    columnFieldNames =['Worksheet Type','ColumnNumber', 'Name', 'ParameterId','LocationId','LocationName','LocationType', 'LocationSubtype', 'Path', 
                     'ParameterTranslation','ColumnId', 'UnitId', 'UnitTranslation','LastPopulatedDate','DataTag', 
                     'LimitName',"LowValue", "LowOperation", "HighValue", "HighOperation", "LimitStartTime", "LimitEndTime" ]              
    def ExportWorksheet(self, filename, plantId, startDate, endDate, updatedAfter=None, wsType=None): 
        with open(filename, mode='w', newline='', encoding="utf-8") as file:        
            fieldnames = self.dataFieldNames
            worksheetWriter =csv.DictWriter(file,fieldnames=fieldnames)
            worksheetWriter.writeheader()
            if not wsType:                    
                wsTypes = range(1,5)
                for wsType in wsTypes:
                    try: 
                         self.__mapAndWriteRowsAndColumns(worksheetWriter, plantId, wsType, startDate, endDate, updatedAfter)                    
                    except:                        
                        continue                    
            else:
                self.__mapAndWriteRowsAndColumns(worksheetWriter, plantId, wsType, startDate, endDate, updatedAfter)                                           
    
    def __mapAndWriteRowsAndColumns(self, worksheetWriter, plantId, wsType, startDate, endDate, updatedAfter):
        wsVal =self.ConvertWSTypeToStringValue(wsType)                       
        try:
            ws=self.Spreadsheet.GetWorksheetDefinition(plantId, wsType)[0]                  
        except:
            return
        if not ws.columns:
            return 
        rows =self.Spreadsheet.GetRowsForTimeRange(plantId, wsType, startDate, endDate)
        try:
            rowNumbers = rows.keys()
            rowValues = rows.values()  
        except(AttributeError):
            return 
        rowDict ={}
        for num in rowNumbers:
            rowDict[num]= str(GetDateFromRowNumber(num, ws.enumWorksheet))
        
        numberMapping = {}
        for column in ws.columns:
            numberMapping[column.columnNumber] = [column.name, column.columnId]  
        for vals in rows.values():            
            for cell in vals.cells:                                                        
                if updatedAfter!=None:
                    try: 
                        dateEntered =cell.cellDatas[0].auditEvents[-1].timeStamp.jsonDateTime.value
                        dateEntered =datetime.strptime(dateEntered[:-2], '%Y-%m-%dT%H:%M:%S.%f')
                        dateEntered =dateEntered.replace(tzinfo=timezone.utc)
                        if dateEntered> updatedAfter:
                            worksheetWriter.writerow({'Worksheet Type': wsVal, 
                                                'Time': rowDict[vals.rowNumber],'ColumnName':numberMapping[cell.columnNumber][0],
                                                'ColumnId':numberMapping[cell.columnNumber][1],
                                                'Value': (cell.cellDatas[0].value.value),
                                                'RowNumber':vals.rowNumber, 
                                                'StringValue':cell.cellDatas[0].stringValue.value, 
                                                'DateEntered':cell.cellDatas[0].auditEvents[-1].timeStamp.jsonDateTime.value, 
                                                'ChangedUsing':self.EnumDataSourceToStringValue(cell.cellDatas[0].auditEvents[-1].enumDataSource)})
                    except(IndexError):                    
                        pass
                else:
                    try:
                            worksheetWriter.writerow({'Worksheet Type': wsVal,
                                                'Time': rowDict[vals.rowNumber],
                                                'ColumnName':numberMapping[cell.columnNumber][0],
                                                'ColumnId':numberMapping[cell.columnNumber][1],
                                                'Value': (cell.cellDatas[0].value.value),
                                                'RowNumber':vals.rowNumber, 
                                                'StringValue':cell.cellDatas[0].stringValue.value, 
                                                'DateEntered':cell.cellDatas[0].auditEvents[-1].timeStamp.jsonDateTime.value, 
                                                'ChangedUsing':self.EnumDataSourceToStringValue(cell.cellDatas[0].auditEvents[-1].enumDataSource)})
                    except(IndexError):                    
                        pass
                                                                    
    def ExportWorksheetByType(self, filename, plantId, startDate, endDate, wsType=4, updatedAfter=None):               
            wsVal =self.ConvertWSTypeToStringValue(wsType)  
            with open(filename, mode='w', newline='', encoding="utf-8") as file:        
                fieldnames = self.dataFieldNames
                worksheetWriter =csv.DictWriter(file,fieldnames=fieldnames)
                worksheetWriter.writeheader()                                       
                self.__mapAndWriteRowsAndColumns(worksheetWriter, plantId, wsType, startDate, endDate, updatedAfter)

    def ExportColumnDetails(self, filename, plantId, wsType =None):                    
        unitDict, paramDict,typeDict, subtypeDict = self.__mapUnitsAndParams()
        
        with open(filename, mode='w', newline='', encoding="utf-8") as file:
            fieldnames =self.columnFieldNames
            worksheetWriter =csv.DictWriter(file, fieldnames=fieldnames)
            worksheetWriter.writeheader()
            if not wsType:
                wsTypes = range(1,5)
                for wsType in wsTypes:
                    try:
                        self.__mapAndWriteColumns(plantId, wsType, unitDict, paramDict, worksheetWriter, typeDict, subtypeDict)
                    except: 
                        raise
                        continue
            else: 
                self.__mapAndWriteColumns(plantId, wsType, unitDict, paramDict, worksheetWriter, typeDict, subtypeDict)
     
    def ExportLimitColumns(self, filename, plantId, wsType =None):                    
        unitDict, paramDict,typeDict, subtypeDict = self.__mapUnitsAndParams()
        with open(filename, mode='w', newline='', encoding="utf-8") as file:
            fieldnames = self.columnFieldNames
            worksheetWriter =csv.DictWriter(file, fieldnames=fieldnames)
            worksheetWriter.writeheader()
            if not wsType:
                wsTypes = range(1,5)
                for wsType in wsTypes:
                    try:
                        self.__mapAndWriteLimitColumns(plantId, wsType, unitDict, paramDict, worksheetWriter, typeDict, subtypeDict)
                    except:                         
                        continue
            else: 
                self.__mapAndWriteLimitColumns(plantId, wsType, unitDict, paramDict, worksheetWriter, typeDict)  
    
    def __mapAndWriteLimitColumns(self, plantId, wsType, unitDict, paramDict, worksheetWriter, typeDict, subtypeDict):
        wsVal = self.ConvertWSTypeToStringValue(wsType)
        try:
            ws=self.Spreadsheet.GetWorksheetDefinition(plantId, wsType)[0]                              
        except:
            return 
        if not ws.columns:
            return 
        
        columnDict = {}
        for column in ws.columns:                    
            columnDict[column.columnNumber] = [column.name,  column.columnId, column.parameterId,  column.displayUnitId, column.lastRowNumberWithData, column.locationId, column.limits, column.dataSourceBinding]       
        limitDict ={}
        for column in columnDict.values():            
            try:
                limit = column[6][0]
                if limit.enumLimit ==5 or limit.enumLimit == 4 or limit.enumLimit == 1:
                    limitDict[column[1]]= [limit.name, limit.lowValue.value, limit.lowOperation, limit.highValue.value, limit.highOperation,  limit.timeWindow.startTime.jsonDateTime.value, limit.timeWindow.endTime.jsonDateTime.value ]
                                 
            except:
                pass
           
        twinDict =self.PathFinder(plantId, columnDict)        
        for key in columnDict.keys():                             
            try:
                try:
                    dataSourceBinding =columnDict[key][7]
                except:
                    dataSourceBinding=""
                locationSubtype = subtypeDict[twinDict[columnDict[key][5]][5]][1]
                locationType =typeDict[twinDict[columnDict[key][5]][4]][1]      
                worksheetWriter.writerow({ 'ColumnNumber': key, 
                                        'Name':columnDict[key][0], 
                                        'ColumnId': columnDict[key][1], 
                                        'Worksheet Type':wsVal,
                                        'ParameterId':columnDict[key][2],
                                        'UnitId': columnDict[key][3],
                                        'LocationName': twinDict[columnDict[key][1]][3],
                                        'LastPopulatedDate': GetDateFromRowNumber(columnDict[key][4], wsType),
                                        'UnitTranslation':unitDict[columnDict[key][3]][2],
                                        'LocationId':columnDict[key][5],
                                        'LocationType':locationType,
                                        'ParameterTranslation':paramDict[columnDict[key][2]][1], 
                                        "Path": twinDict[columnDict[key][1]][2],
                                        'LimitName' :  limitDict[columnDict[key][1]][0], 
                                        "LowValue": limitDict[columnDict[key][1]][1], 
                                        "LowOperation": self.LimitOperationToStringValue(limitDict[columnDict[key][1]][2]),
                                        "HighValue": limitDict[columnDict[key][1]][3], 
                                        "HighOperation":self.LimitOperationToStringValue(limitDict[columnDict[key][1]][4]),
                                        "LimitStartTime":limitDict[columnDict[key][1]][5],
                                        "LimitEndTime":limitDict[columnDict[key][1]][6],
                                        "LocationSubtype": locationSubtype,
                                        "DataTag":dataSourceBinding
                                                                                                                                
                                        })
            except (KeyError):
                pass
            
    def __mapAndWriteColumns(self, plantId, wsType, unitDict, paramDict, worksheetWriter, typeDict, subtypeDict):
        wsVal = self.ConvertWSTypeToStringValue(wsType)
        try:
            ws=self.Spreadsheet.GetWorksheetDefinition(plantId, wsType)[0]                              
        except:
            return 
        if not ws.columns:
            return
        
        columnDict = {}
        for column in ws.columns:                    
            columnDict[column.columnNumber] = [column.name,  column.columnId, column.parameterId,  column.displayUnitId, column.lastRowNumberWithData, column.locationId, column.limits, column.dataSourceBinding.bindingId]       
        limitDict ={}
        for column in columnDict.values():            
            try:
                limit = column[6][0]
                if limit.enumLimit ==5 or limit.enumLimit == 4 or limit.enumLimit == 1:
                    limitDict[column[1]]= [limit.name, limit.lowValue.value, limit.lowOperation, limit.highValue.value, limit.highOperation,  limit.timeWindow.startTime.jsonDateTime.value, limit.timeWindow.endTime.jsonDateTime.value ]
                                 
            except:
                pass
           
        twinDict =self.PathFinder(plantId, columnDict)        
        for key in columnDict.keys():
            locationType =typeDict[twinDict[columnDict[key][5]][4]][1]            
            try:
                dataSourceBinding =columnDict[key][7]
            except:
                dataSourceBinding=""
            try:
                locationSubtype = subtypeDict[twinDict[columnDict[key][5]][5]][1]
                worksheetWriter.writerow({ 'ColumnNumber': key, 
                                        'Name':columnDict[key][0], 
                                        'ColumnId': columnDict[key][1], 
                                        'Worksheet Type':wsVal,
                                        'ParameterId':columnDict[key][2],
                                        'UnitId': columnDict[key][3],
                                        'LocationName': twinDict[columnDict[key][1]][3],
                                        'LastPopulatedDate': GetDateFromRowNumber(columnDict[key][4], wsType),
                                        'UnitTranslation':unitDict[columnDict[key][3]][2],
                                        'LocationId':columnDict[key][5],
                                        'LocationType':locationType,
                                        'ParameterTranslation':paramDict[columnDict[key][2]][1], 
                                        "Path": twinDict[columnDict[key][1]][2],                                        
                                        'LimitName' :  limitDict[columnDict[key][1]][0], 
                                        "LowValue": limitDict[columnDict[key][1]][1], 
                                        "LowOperation": self.LimitOperationToStringValue(limitDict[columnDict[key][1]][2]),
                                        "HighValue": limitDict[columnDict[key][1]][3], 
                                        "HighOperation":self.LimitOperationToStringValue(limitDict[columnDict[key][1]][4]),
                                        "LimitStartTime":limitDict[columnDict[key][1]][5],
                                        "LimitEndTime":limitDict[columnDict[key][1]][6],
                                        "LocationSubtype": locationSubtype,
                                        "DataTag":dataSourceBinding                                                                                                                              
                                        })
            except (KeyError):
                locationSubtype = subtypeDict[twinDict[columnDict[key][5]][5]][1]
                worksheetWriter.writerow({ 'ColumnNumber': key, 
                                            'Name':columnDict[key][0], 
                                            'ColumnId': columnDict[key][1], 
                                            'Worksheet Type':wsVal,
                                            'ParameterId':columnDict[key][2],
                                            'UnitId': columnDict[key][3],
                                            'LocationName': twinDict[columnDict[key][1]][3],                                            
                                            'LastPopulatedDate': GetDateFromRowNumber(columnDict[key][4], wsType),
                                            'UnitTranslation':unitDict[columnDict[key][3]][2],
                                            'LocationId':columnDict[key][5],
                                            'LocationType':locationType,
                                            'ParameterTranslation':paramDict[columnDict[key][2]][1], 
                                            "Path": twinDict[columnDict[key][1]][2],
                                            "LocationSubtype": locationSubtype,
                                            "DataTag":dataSourceBinding     
                                            })
                
    def __mapUnitsAndParams(self):
        units = self.Library.GetUnits()  
        parameters = self.Library.GetParameters()       
        i18N = self.Library.Geti18nKeys("AQI_FOUNDATION_LIBRARY")[0].get("AQI_FOUNDATION_LIBRARY")
        i18NUnits= i18N.get("UnitType").get("LONG")
        i18NParams= i18N.get("Parameter").get("LONG")  
        i18NSubtypes= i18N.get("DigitalTwinSubType")   
        paramDict = {}
        for param in parameters:
            try:
                paramDict[param.IntId]= [param.i18nKey, i18NParams[param.i18nKey]]
            except: 
                paramDict[param.IntId]= [param.i18nKey, None]                     
        unitDict = {}
        for unit in units:
            try:
                unitDict[unit.IntId]= [unit.i18nKey, unit.unitName, i18NUnits[unit.i18nKey]]
            except:
                unitDict[unit.IntId]= [unit.i18nKey, unit.unitName, None]
        twinTypes = self.DigitalTwin.GetDigitalTwinTypes()
        typeDict ={}
        for twinType in twinTypes:
            typeDict[twinType.id]=[twinType.i18NKeyName, twinType.description.value]
        twinSubtypes = self.DigitalTwin.GetDigitalTwinSubtypes()
        subTypeDict ={}
        for subtype in twinSubtypes:
            try:
                subTypeDict[subtype.id]=[subtype.i18NKeyName, i18NSubtypes[subtype.i18NKeyName] ]
            except(KeyError):
                subTypeDict[subtype.id]=[subtype.i18NKeyName, subtype.i18NKeyName]
        
        return unitDict, paramDict, typeDict, subTypeDict
    
    def ExportColumnDetailsByType(self, filename, plantId, wsType=4):         
        unitDict, paramDict,typeDict, subtypeDict = self.__mapUnitsAndParams()
        with open(filename, mode='w', newline='', encoding="utf-8") as file:
            fieldnames =self.columnFieldNames
            worksheetWriter =csv.DictWriter(file, fieldnames=fieldnames)
            worksheetWriter.writeheader()
            self.__mapAndWriteColumns(plantId, wsType, unitDict, paramDict, worksheetWriter, typeDict, subtypeDict)
                             
    def PathFinder(self, plantId, columnDict):        
        twins = self.DigitalTwin.GetDescendantsByType(plantId, "ae018857-5f27-4fe4-8117-d0cbaecb9c1e", False)
        twins.MergeFrom(self.DigitalTwin.GetDescendantsByRefByCategory(plantId, 2,False))
        twins= twins.items      
        twinDict ={}
        for twin in twins:
            twinDict[twin.twinReferenceId.value]=[twin.parentTwinReferenceId.value, twin.name.value, None, None, twin.twinTypeId, twin.twinSubTypeId.value]                
        for key in columnDict.keys():
            twinId=columnDict[key][1]
            path =[]
            pathString=""
            while (twinId!=plantId):             
                path.append(twinDict[twinId][1])
                twinId =twinDict[twinId][0]                                
            path.append(twinDict[twinId][1])
            twinDict[columnDict[key][1]][3]=path[1]
            while (path):
                pathString= f'{pathString}/{path.pop()}'
            twinDict[columnDict[key][1]][2]=pathString
        return twinDict
    
    def ConvertWSTypeToStringValue(self, wsType):
        if wsType ==1:
            return "Fifteen Minute"
        elif wsType ==2:
            return "Hourly"   
        elif wsType ==3:
            return "Four Hour"                                  
        elif wsType ==4:
            return "Daily"            
        else: 
             return print("Enter valid worksheet type value (1= Fifteen minute, 2=Hourly, 3=FourHour, 4=Daily)") 
           
    def LimitOperationToStringValue(self, limitOperation):
        if limitOperation ==1:
            return ">"
        elif limitOperation ==2:
            return ">="   
        elif limitOperation ==3:
            return "<"                                  
        elif limitOperation ==4:
            return "=<"       
        elif limitOperation ==0:
            return "Unknown"            
        else: 
             return print(f"{limitOperation}Enter valid limit Operation value (1 is >, 2  is ≥  , 3 is < , 4 is ≤)")      
   
    def EnumDataSourceToStringValue(self, enumDataSource):
        if enumDataSource ==1:
            return "MOBILE"
        elif enumDataSource ==2:
            return "COMPUTATION"   
        elif enumDataSource ==3:
            return "WEBAPP"                                  
        elif enumDataSource ==4:
            return "INSTRUMENT"       
        elif enumDataSource ==0:
            return "UNKNOWN"            
        elif enumDataSource ==5:
            return "IMPORT"
        elif enumDataSource ==6:
            return "SPREADSHEETDEF"
        elif enumDataSource ==7:
            return "CONNECT"   
        else: 
             return print(f"{enumDataSource}Enter valid enumDataSource (valid values are 0-7))")      
   
          
            
        