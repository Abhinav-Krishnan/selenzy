# Selenzyme - Enzyme Selection Tool

## How to Install

Recommended installation method for the updated version of Selenzyme to get both the command line and web applications is to first clone this repository: [Files to install updated Selenzyme. (github.com)](https://github.com/Abhinav-Krishnan/selenzyme)

Follow the instructions on this page by running the `start_server.sh` script in the cloned directory. This will build a docker container and install all the required dependencies for the updated version of Selenzyme within this container. The script will also download the datafiles required by Selenzyme.

## How to Use

#### Command Line

The command line version of the tool is run using the Selenzy.py program. The usage instructions for this program can be viewed by running `python Selenzy.py -h` or `python Selenzy.py --help`. This will display the follwing message showing the structure of the command to run Selenzy.py with an input reaction, as well as a description of all the arguments in this command:

```
usage: Selenzy.py [-h] [-tar TAR] [-d D] [-outfile OUTFILE] [-NoMSA] [-smarts]
                  [-smartsfile] [-theia] [-host HOST]
                  rxn datadir outdir

SeqFind script for Selenzy

positional arguments:
  rxn               Input reaction [default = rxn file]
  datadir           specify data directory for required databases files, please end   
                    with slash
  outdir            specify output directory for all output files, including final  
                    CSV file, please end with slash

options:
  -h, --help        show this help message and exit
  -tar TAR          Number of targets to display in results [default = 20]
  -d D              Use similiarity values for preferred reaction direction only
                    [default=0 (OFF)]
  -outfile OUTFILE  specify non-default name for CSV file output
  -NoMSA            Do not compute MSA/conservation scores
  -smarts           Input is a reaction SMARTS string
  -smartsfile       Input is a reaction SMARTS file
  -theia            Enable additional scoring based on Theia EC Number predictions
```

Example command:

```sh
python Selenzy.py "O=C([O-])CCC(=O)C(=O)[O-].NC(CC(=O)[O-])C(=O)O>>O=C([O-])CC(=O)C(=O)[O-].NC(CCC(=O)[O-])C(=O)O" dataDirectory outputDirectory -outfile OutputFilename.csv -tar 500 -theia
```

#### Web Application

The docker container built by `start_server.sh` will run the web application version of the tool when it is started. When this is started up, it can be accessed locally at [http://localhost:5000](http://localhost:5000). Specific instructions for using this version of Selenzyme can be seen on the web page when launched.


### Usage Warning

The `-theia` input flag on the command line version and the "Enable Theia..." checkbox on the web application are not recommended to be used when input reactions are known or suspected to be in EC Class 7. The accuracy improvements seen in Selenzyme's results when using these options was not observed for this particular EC Class during testing.
