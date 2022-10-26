
def getIndex(indexColumns, scope, subset):

    if(scope=='YEAR'):
        if(subset =='ALL'):
            return indexColumns.index.values.tolist(), False
        else:
            elem = indexColumns.index[indexColumns['YEAR']==str(subset)].tolist()
            if not elem:
                return elem, True
            else:
                return elem, False
