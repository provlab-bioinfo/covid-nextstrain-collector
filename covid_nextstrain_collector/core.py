import pandas as pd, os, shutil, re, os
import covid_nextstrain_collector.searchTools as st
from pathlib import Path
from alive_progress import alive_bar
import datetime

def collateCOVIDdata(seqData: pd.DataFrame, patientData: pd.DataFrame, matchCol:str = None):
    """Collates COVID sequencing data and metadata. Will drop duplicate samples based on the matchCol.
    :param seqData: DataFrame containing sequencing data
    :param patientData: DataFrame containing sample metadata
    :param matchCol: The column to match the data on
    :return: A collated DataFrame
    """    
    accessions = seqData[matchCol].values.tolist()
    metadata = patientData[patientData[matchCol].isin(accessions)]
    seqData.drop_duplicates(subset=[matchCol], inplace=True)
    metadata.drop_duplicates(subset=[matchCol], inplace=True)
    seqData = seqData.merge(metadata, on = matchCol)
    return seqData

def getPatientMetadata(patientDataDir:str, cols: dict, verbose = True):
    """Retrieves patient metadata 
    :param patientDataDir: Path to the customer tab data
    :param cols: Columns to capture & rename
    :param renameCols: Mapper to rename columns
    :param verbose: Be chatty
    :return: DataFrame with combined and subsetted data
    """    
    if verbose: print("\nRetrieving patient metadata...")
    if not os.path.isdir(patientDataDir): raise FileNotFoundError(f"Directory does not exist: {patientDataDir}")

    patientDataFiles = st.generateFlatFileDB(dir = patientDataDir)
    patientDataFiles = st.searchFlatFileDB(patientDataFiles, searchTerms="lab_covid19_cust_tab_output")  
    
    metadata = []
    for file in patientDataFiles:
        if verbose: print(f"   Reading: {Path(file).stem}")
        metadata.append(st.importToDataFrame(file, index_col=False, low_memory=True, encoding_errors='replace', 
                                             dtype="str", on_bad_lines='skip',
                                             usecols = lambda col: col in list(cols.values()) + list(cols.keys())))

    if verbose: print(f"Collating patient metadata...")
    metadata = pd.concat(metadata, ignore_index=True)
    metadata = metadata.rename(columns = cols)
    metadata = metadata[metadata.columns.intersection(list(cols.values()))]

    if 'age' in metadata.columns:
        bins = [0,20,40,60,80,100,1000]
        labels = ['0-20','20-40','40-60','60-80','80-100','100+']
        metadata['age'] = pd.to_numeric(metadata['age'],errors='coerce')
        metadata['age'] = pd.cut(metadata['age'], bins=bins, labels=labels, right=False)

    return metadata

def getSeqData(seqDataPath:str, dbPath: str, cols: dict, verbose = True):
    """Retrieves BNexport files. 
    :param seqDataPath: Path to the BNexport directory. Can be any format of: .tsv, .csv, or .xlsx.
    :param dbPath: Path to flat file database
    :param cols: Columns to capture & rename
    :param verbose: Be chatty
    :return: DataFrame with sequencing data
    """    
    if verbose: print(f"\nRetrieving sequencing data...")
    if not os.path.isdir(seqDataPath): raise FileNotFoundError(f"Directory does not exist: {seqDataPath}")
    
    seqDataFiles = st.generateFlatFileDB(seqDataPath)  
    
    seqData = []
    for file in seqDataFiles:
        if verbose: print(f"   Reading: {Path(file).stem}")
        seqData.append(st.importToDataFrame(file, index_col=False, low_memory=True, encoding_errors='replace', 
                                             dtype="str", on_bad_lines='skip',
                                             usecols = lambda col: col in list(cols.values()) + list(cols.keys())))
        
    if verbose: print(f"Collating sequencing metadata...")
    seqData = pd.concat(seqData, ignore_index=True)

    seqData = addFASTApaths(seqData, dbPath)    
    seqData = seqData.rename(columns = cols)
    seqData = seqData[seqData.columns.intersection(list(cols.values()))]

    return seqData

def addFASTApaths(seqData:pd.DataFrame, dbPath:str, verbose = True):
    """Adds FASTA paths to seqData
    :param seqData: DataFrame of sequencing data. Must have column named 'fasta'.
    :param dbPath: Path to flat file database
    :param verbose: Be chatty, defaults to True
    :return: seqData with additional paths to all FASTA files in column 'fastaPath'
    """    
    if verbose: print(f"\nRetrieving FASTA files...")
    if "fasta" not in seqData.columns: raise KeyError("Column 'fasta' does not exist in the seqData.")
    # dbPath = st.generateFlatFileDB(dbPath, outFile="./db.txt")
    fastas = st.searchFlatFileDB(dbPath, includeTerms = seqData["fasta"].values.tolist())
    fastas = pd.DataFrame(fastas, columns =['fastaPath'])
    fastas['fasta'] = fastas['fastaPath'].transform(lambda path: os.path.basename(path))
    weights = fastas['fasta'].transform(lambda path: 1000000000 if bool(re.search('consensus', path)) else 1)
    fastas = fastas.groupby('fasta').sample(weights = weights.tolist()).reset_index()
    seqData = seqData.merge(fastas,how="right",on="fasta")
    # seqData = seqData[seqData["fastaPath"].apply(os.path.isfile)]
    return seqData

def writeSequences(outFile: str, seqData: pd.DataFrame, stripMetadata = True, verbose = True) -> None:
    """Writes a list of FASTA files to a single file. 
    :param outFile: The path to the output file. Will overwrite or be created if it doesn't exist.
    :param keys: The dataframe representing samples. Must have column 'Key' and 'fastaPath'
    :param stripMetadata: Remove metadata from header?, defaults to True
    :param verbose: Print progress messages?, defaults to True
    :return: Nothing
    """
    print("\nGenerating sequences.fasta...")
    with alive_bar(total = len(seqData), title="Writing FASTAs...", unknown="dots_waves", disable = not verbose) as bar:
        with open(outFile,'wb') as out:
            for rowIdx in seqData.index:
                row = seqData.loc[rowIdx]
                try:
                    with open(row['fastaPath'],"rb") as f:
                        if stripMetadata:
                            header = f.readline()
                            header = row['strain']
                            out.write(str.encode(">" + header + "\n"))
                        shutil.copyfileobj(f, out)
                except FileNotFoundError:
                    pass
                bar()

def renameAndSubsetDF(df:pd.DataFrame, cols: dict):
    """Renames columns in a DataFrame and discards columns not in the list
    :param seqDataPath: Path to the BioNumerics Export file
    :param patientDataDir: Path to the customer tab data
    :param output: The output CSV
    """    
    df = df.rename(columns = cols)
    df = df[df.columns.intersection(list(cols.values()))]
    return df

def year_fraction(date):
    try:
        start = datetime.date(int(date.year), 1, 1).toordinal()
        year_length = datetime.date(date.year+1, 1, 1).toordinal() - start
        date = date.year + float(date.toordinal() - start) / year_length
    except:
        pass
    
    return date

def year_fraction(date):
    try:
        start = datetime.date(int(date.year), 1, 1).toordinal()
        year_length = datetime.date(date.year+1, 1, 1).toordinal() - start
        return date.year + float(date.toordinal() - start) / year_length
    except:
        return date

def convertDecimalDates(df: pd.DataFrame):
    dateCols = [col for col in df.columns if 'date' in col.lower()]
    for col in dateCols:
        # df[col] = pd.to_datetime(df[col],errors='coerce',dayfirst=False).dt.strftime('%Y-%m-%d')
        df[col] = pd.to_datetime(df[col],errors='coerce',dayfirst=False)
        df[col] = df[col].apply(lambda x: year_fraction(x))
    return df

def convertDates(df: pd.DataFrame):
    dateCols = [col for col in df.columns if 'date' in col.lower()]
    for col in dateCols:
        df[col] = pd.to_datetime(df[col],errors='coerce',dayfirst=False).dt.strftime('%Y-%m-%d')
    return df

def generateCOVIDdatabase(seqDataPath:str, patientDataDir: str, dbPath: str, captureCols: dict, output:str, verbose: bool = True):
    """Generates a collated COVID database. Includes all sequencing data, as well as metadata for patient age, gender and region.
    :param seqDataPath: Path to the BioNumerics Export file
    :param patientDataDir: Path to the customer tab data
    :param output: The output CSV
    """    
    seqData = getSeqData(seqDataPath = seqDataPath,    
                         dbPath = dbPath, 
                         cols = captureCols,                
                         verbose = verbose)

    patientData = getPatientMetadata(patientDataDir = patientDataDir,
                                     cols = captureCols, 
                                     verbose = verbose)

    Path(output).mkdir(parents=True, exist_ok=True)
    mdataOut = os.path.join(output,"metadata.tsv")
    mdata = collateCOVIDdata(seqData = seqData, patientData = patientData, matchCol = "accession")
    mdata = convertDates(mdata)
    print("\nGenerating metadata.tsv...")
    mdata.to_csv(mdataOut, sep="\t", index=False)
    seqsOut = os.path.join(output,"sequences.fasta")
    writeSequences(seqData = mdata, outFile = seqsOut)

    print(f"\nAuspice output generated!\n"
          f"-------------------------\n"
          f"Found {len(seqData)} sequences\n"
          f"Found {len(patientData)} patient metadata entries\n"
          f"Matched {len(mdata)} sequences to metadata\n"
          f"-------------------------\n"
          f"Saved to:\n"
          f"Sequences: {seqsOut}\n"
          f"Metadata: {mdataOut}\n")