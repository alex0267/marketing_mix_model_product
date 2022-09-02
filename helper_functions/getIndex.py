
def getIndex(indexColumns, scope, index):

    if(scope=='YEAR'):
        if(index =='ALL'):
            return indexColumns.index.values.tolist()
        else:
            return indexColumns.index[indexColumns['YEAR']=='Y2'].tolist()
