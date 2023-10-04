import pandas as pd, timeit, os, shutil, sys, re, os, searchTools as st
from pathlib import Path
from datetime import datetime, date
from alive_progress import alive_bar

os.chdir(os.path.dirname(__file__))

def collateCOVIDdata(seqData: pd.DataFrame, patientData: pd.DataFrame, matchCol:str = None):
    """Collates COVID sequencing data and metadata. Will drop duplicate samples based on the matchCol.
    :param seqData: DataFrame containing sequencing data
    :param patientData: DataFrame containing sample metadata
    :param matchCol: The column to match the data on
    :return: A collated DataFrame
    """    
    # Subset the metadata
    accessions = seqData[matchCol].values.tolist()
    metadata = patientData[patientData[matchCol].isin(accessions)]
    seqData.drop_duplicates(subset=[matchCol], inplace=True)
    metadata.drop_duplicates(subset=[matchCol], inplace=True)

    # Align the metadata
    seqData = seqData.merge(metadata, on = matchCol)

    return seqData

def getPatientMetadata(patientDataDir:str, captureCols:str, renameCols:dict = None, verbose = True):
    """Retrieves patient metadata 
    :param patientDataDir: Path to the customer tab data
    :param regex: The regex to select files for
    :param captureCols: Columns to capture for the customer tab data
    :param renameCols: Mapper to rename columns
    :return: DataFrame with combined and subsetted data
    """    
    if verbose: print("\nRetrieving patient metadata...")
    patientDataFiles = st.generateFlatFileDB(dir = patientDataDir)
    patientDataFiles = st.searchFlatFileDB(patientDataFiles, searchTerms="lab_covid19_cust_tab_output")  
    
    metadata = []
    for file in patientDataFiles:
        if verbose: print(f"   Reading: {Path(file).stem}")
        metadata.append(st.importToDataFrame(file, index_col=False, low_memory=True, encoding_errors='replace', dtype="str", usecols=captureCols))

    if verbose: print(f"Collating patient metadata...")
    metadata = pd.concat(metadata, ignore_index=True)
    if renameCols is not None: metadata.rename(columns=renameCols, inplace=True)
    return metadata

def getSeqData(seqDataPath:str, onlyQCpass:bool = True, verbose = True):
    """Retrieves BNexport files. 
    :param seqDataPath: Path to the BNexport directory. Can be any format of: .tsv, .csv, or .xlsx.
    :param onlyQCpass: Subset to only QC passing samples. Column 'qc_pass' must exist.
    :param verbose: Be chatty
    :return: DataFrame with sequencing data
    """    
    if verbose: print(f"\nRetrieving sequencing data...")
    seqDataFiles = st.generateFlatFileDB(seqDataPath)  
    
    seqData = []
    for file in seqDataFiles:
        if verbose: print(f"   Reading: {Path(file).stem}")
        seqData.append(st.importToDataFrame(file, index_col=False, low_memory=True, encoding_errors='replace', dtype="str"))
        
    if verbose: print(f"Collating sequencing metadata...")
    seqData = pd.concat(seqData, ignore_index=True)
    if "qc_pass" in seqData.columns and onlyQCpass: seqData = seqData.loc[(seqData["qc_pass"] == "PASS") | (seqData["qc_pass"] == "TRUE")]
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
                with open(row['fastaPath'],"rb") as f:
                    if stripMetadata:
                        header = f.readline()
                        header = row['Key']
                        out.write(str.encode(">" + header + "\n"))
                    shutil.copyfileobj(f, out)
                bar()

def generateCOVIDdatabase(seqDataPath:str, patientDataDir: str, dbPath: str, output:str, verbose: bool = True):
    """Generates a collated COVID database. Includes all sequencing data, as well as metadata for patient age, gender and region.
    :param seqDataPath: Path to the BioNumerics Export file
    :param patientDataDir: Path to the customer tab data
    :param output: The output CSV
    """    
    seqData = getSeqData(seqDataPath = seqDataPath,
                         verbose = verbose).sample(1000)

    fastaData = addFASTApaths(seqData = seqData, 
                            dbPath = dbPath, 
                            verbose = verbose)

    patientData = getPatientMetadata(patientDataDir = patientDataDir,
                                     captureCols = ["SPEC_NUMBER_LN1","SPEC_PAT_NUM_AGE","PATIENT_GENDER","REGION_SUM"],
                                     renameCols = {"SPEC_NUMBER_LN1": "accession_number"},
                                     verbose = verbose)

    mdataOut = os.path.join(output,"metadata.tsv")
    mdata = collateCOVIDdata(seqData = fastaData, patientData = patientData, matchCol = "accession_number")
    print("\nGenerating metadata.tsv...")
    mdata.to_csv(mdataOut, sep="\t", index=False)

    seqsOut = os.path.join(output,"sequences.fasta")
    writeSequences(seqData = mdata, outFile = seqsOut)

    print(f"\nAuspice output generated!\n"
          f"-------------------------\n"
          f"Found {len(seqData)} sequences\n"
          f"Matched {len(fastaData)} FASTAs files\n"
          f"Found {len(patientData)} patient metadata entries\n"
          f"Matched {len(mdata)} sequences to metadata\n"
          f"-------------------------\n"
          f"Saved to:\n"
          f"Sequences: {seqsOut}\n"
          f"Metadata: {mdataOut}\n")

seqDataPath = "\\\\healthy.bewell.ca\\Apps\\APL_Genomics\\apps\\development\\nextstrain\\ncov\\BNexport"
patientDataDir = "\\\\healthy.bewell.ca\\FHE\\PRL\Groups\\ProvincialSurveillance\\COVID-19"
routineSeqDB = "\\\\healthy.bewell.ca\\Apps\\APL\\Genomics_DEV\\projects\\data_management\\flatFileDBs\\routineSeqDB_2023-09-07_fasta_windows_path.txt"

output = os.path.join("\\\\healthy.bewell.ca\\Apps\\APL_Genomics\\apps\\development\\nextstrain\\ncov\\DB\\", str(date.today().strftime("%y%m%d"))+"_ncov")
os.mkdir(output)

generateCOVIDdatabase(seqDataPath = seqDataPath,
                      patientDataDir = patientDataDir,
                      dbPath = routineSeqDB,
                      output = output)