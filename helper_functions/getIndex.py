
def getIndex(indexColumns, scope, subset):

    if(scope=='YEAR'):
        if(subset =='ALL'):
            return indexColumns.index.values.tolist()
        else:
            return indexColumns.index[indexColumns['YEAR']==subset].tolist()
