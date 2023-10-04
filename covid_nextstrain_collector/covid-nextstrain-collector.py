import os, argparse, json
import covid_nextstrain_collector.config as cfg
import covid_nextstrain_collector.core as core

seqDataPath = "\\\\healthy.bewell.ca\\Apps\\APL_Genomics\\apps\\development\\nextstrain\\ncov\\BNexport"
patientDataDir = "\\\\healthy.bewell.ca\\FHE\\PRL\Groups\\ProvincialSurveillance\\COVID-19"
routineSeqDB = "\\\\healthy.bewell.ca\\Apps\\APL\\Genomics_DEV\\projects\\data_management\\flatFileDBs\\routineSeqDB_2023-09-07_fasta_windows_path.txt"

output = os.path.join("\\\\healthy.bewell.ca\\Apps\\APL_Genomics\\apps\\development\\nextstrain\\ncov\\DB\\", str(date.today().strftime("%y%m%d"))+"_ncov")
os.mkdir(output)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    parser.add_argument('-o', '--output')
    
    args = parser.parse_args()

    config = {}

    if args.config:
        try:
            config = cfg.load_config(args.config, dry_run=args.dry_run)
        except json.decoder.JSONDecodeError as e:
            # If we fail to load the config file, we continue on with the
            # last valid config that was loaded.
            exit(-1)
    
    core.generateCOVIDdatabase(seqDataPath = config["seqDataPath"],
                      patientDataDir = config["patientDataDir"],
                      dbPath = config["routineSeqDB"],
                      output = args.output)
