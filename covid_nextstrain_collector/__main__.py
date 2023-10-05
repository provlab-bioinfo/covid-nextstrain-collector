import argparse, json
import covid_nextstrain_collector.config as cfg
import covid_nextstrain_collector.core as core

def main():
    parser = argparse.ArgumentParser(description ='A collector for SARS-CoV-2 sample data for visualization in Nextstrain. '
                                     'This generates the sequences.fasta and metadata.tsv necessary for generating the Nextstrain instance. '
                                     'See https://github.com/provlab-bioinfo/covid-nextstrain-collector or the Paradigm SOP for more details.')
    parser.add_argument('-c', '--config',type=str, help='Path to the config file. It should have the format:\n'
                        '{\n'
                        '\t"seqDataPath": "/path/to/BNexport",\n'
                        '\t"patientDataDir": "/path/to/metadata",\n'
                        '\t"routineSeqDB": "/path/to/database"\n'
                        '}')
    parser.add_argument('-o', '--output',type=str, help='Path to the output folder')    
    args = parser.parse_args()

    config = {}
    if args.config:
        try:
            config = cfg.load_config(args.config)
        except json.decoder.JSONDecodeError as e:
            exit(-1)
    
    core.generateCOVIDdatabase(seqDataPath = config["seqDataPath"],
                      patientDataDir = config["patientDataDir"],
                      dbPath = config["routineSeqDB"],
                      output = args.output)