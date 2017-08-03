#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 10:53:03 2017

@author: jerrywzy
"""
import re
import os, subprocess
import json
import csv
import argparse
import quickRsim
import numpy as np
from rdkit.Chem import AllChem, Draw

class preLoad(object):
    """ Container of precomputed data """
    def __init__(self):
        pass

    def fasta(self, datadir, ffile="seqs.fasta"):
        (sequence, names, descriptions, osource) = readFasta(datadir, ffile)
        self.sequence = sequence
        self.names = names
        self.descriptions = descriptions
        self.osource = osource

    def fp(self, datadir, fpfile):
        data = np.load(os.path.join(datadir, fpfile))
        self.fp = data['x']
        self.fpn = data['y']
        data.close()

    def seqData(self, datadir, fl):
        with open(os.path.join(datadir, fl[0])) as f:
            self.MnxToUprot = json.load(f)
        
        with open(os.path.join(datadir, fl[1])) as f2:
            self.upclst = json.load(f2)
        
        with open(os.path.join(datadir, fl[2])) as f3:
            self.clstrep= json.load(f3)
        self.seqorg = seqOrganism(datadir, fl[3])
        self.tax = readTaxonomy(datadir, fl[4])

    def reacData(self, datadir, smf):
            smiFile = os.path.join(datadir, smf)
            self.smir = {}
            if os.path.exists(smiFile):
                self.smir = reactionSmiles(smiFile)


def sanitizeRxn(rxninfo, outrxn):
    """ It works both with the smiles string or a rxn file """
    try:
        if os.path.exists(rxninfo):
            if open(rxninfo).readline().startswith('$RXN'):
                rxn = AllChem.ReactionFromRxnFile(rxninfo)
            else:
                smarts =  open(rxninfo).readline().rstrip()
                try:
                    rxn = AllChem.ReactionFromSmarts(smarts, useSmiles=True)
                except:
                    rxn = AllChem.ReactionFromSmarts(smarts)
        smi = AllChem.ReactionToSmiles(rxn)
        with open(outrxn+'.smi', 'w') as handler:
            handler.write(smi)
        mdl = AllChem.ReactionToRxnBlock(rxn)
        with open(outrxn+'.rxn', 'w') as handler:
            handler.write(mdl)
        return smi
    except:
        return ''

def sanitizeSmarts(smarts, outrxn):
    """ It works both with the smiles string or a rxn file """
    try:
        try:
            rxn = AllChem.ReactionFromSmarts(smarts, useSmiles=True)
        except:
            rxn = AllChem.ReactionFromSmarts(smarts)
        smi = AllChem.ReactionToSmiles(rxn)
        with open(outrxn+'.smi', 'w') as handler:
            handler.write(smi)
        mdl = AllChem.ReactionToRxnBlock(rxn)
        with open(outrxn+'.rxn', 'w') as handler:
            handler.write(mdl)
        return smi
    except:
        return ''



def display_reaction(rxninfo, outfolder, outname, marvin=False):
    """ It works both with the smiles string or a rxn file """
    if marvin:
        try:
            cmd = ['molconvert', 'svg:w500', rxninfo]
            job = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = job.communicate()
            outimage = os.path.join(outfolder, outname+'.svg')
            return outimage, (600, 400)
        except:
            return '', (0,0)
    else:
        try:
            if os.path.exists(rxninfo):
                if open(rxninfo).readline().startswith('$RXN'):
                    rxn = AllChem.ReactionFromRxnFile(rxninfo)
                else:
                    smarts =  open(rxninfo).readline()
                    rxn = AllChem.ReactionFromSmarts(smarts)
                outimage = os.path.join(outfolder, outname+'.png')
                im = Draw.ReactionToImage(rxn)
                size = im.size
                im.save(outimage)
                return outimage, size
            else:
                rxn = AllChem.ReactionFromSmarts(rxninfo)
                outimage = os.path.join(outfolder, outname+'.png')
                im = Draw.ReactionToImage(rxn)
                size = im.size
                im.save(outimage)
                return outimage, size
        except:
            return '', (0,0)

def seqOrganism(datadir, fileSeqOrg):
    seqorg = {}
    for line in open(os.path.join(datadir, fileSeqOrg)):
        row = line.rstrip().split('\t')
        seqorg[ row[0] ] = (row[1], row[2])
    return seqorg

def readTaxonomy(datadir, fileLineage):
    tax = {}
    with open(os.path.join(datadir, fileLineage)) as handler:
        for row in csv.reader(handler):
            tax[row[0]] = row
    return tax

def taxDistance(tax, host, target):
    if host in tax and target in tax:
        hostLineage = set(tax[host])
        targetLineage = set(tax[target])
        distance = 1 + len(hostLineage ^ targetLineage)
        return distance
    else:
        return '-'

def readFasta(datadir, fileFasta):
    
    from Bio import SeqIO
    
    sequence = {}
    descriptions = {}
    osource = {}
    names = []
    seen = set()
    seen_add = seen.add
    
    for seq_record in SeqIO.parse(os.path.join(datadir, fileFasta), "fasta"):
        ming = seq_record.id
        idonly = re.search(r'\|(.*?)\|',ming)
        x = idonly.group(1)
        
        fulldesc = seq_record.description
        desc = fulldesc.rsplit('OS=')[0]
        shortdesc = " ".join(desc.split()[1:])
        orgsource = fulldesc.rsplit('OS=')[1]
        shortos = orgsource.rsplit('GN=')[0]
    #    o = shortos.group(1)
        if ',' in shortdesc:
            y = shortdesc.replace(",", ";")
        else:
            y = shortdesc
        
        if x not in seen:
            names.append(x)
            seen_add(x)
        myseq = seq_record.seq
        sequence[x]=(myseq)
        descriptions[x]= y
        osource[x]=shortos
    
        
#    with open('sequences.json', 'w') as f:
#        json.dump(sequence, f)
    
#    with open('descriptions.json', 'w') as f2:
#        json.dump(descriptions, f2)
    
    
    return (sequence, names, descriptions, osource)
 
def readRxnCons(consensus):
    
    f = open(consensus, 'r')
    
    MnxDir = {}
    
    for line in f:
        splitdata = line.split()
        Mnx = splitdata[1]
        dirxn = splitdata[2]
        MnxDir[Mnx] = dirxn
        
    return (MnxDir)   
    
def getMnxSim(rxnInput, datadir, outdir, drxn=0, pc=None):
    """ Commmand line arguments of quickRsim """
    args = [os.path.join(datadir,'reac_prop.tsv'), os.path.join(datadir,'mgfp.npz')] + rxnInput + ['-out', os.path.join(outdir,'results_quickRsim.txt')]
    quickRsim.run( quickRsim.arguments(args), pc )
    MnxSim = {}
    MnxDirPref = readRxnCons(os.path.join(datadir, "rxn_consensus_20160612.txt"))
    MnxDirUsed = {}
    EcNumber = {}
    
    if drxn==1:
        fileout = open(os.path.join(outdir, "results_quickRsim.txt"), 'r')
        for line in fileout:
            splitdata = line.split()
            S1 = splitdata[2]
            S2 = splitdata[3]
            SMILES = splitdata[4]
            EC = ''
            if len(splitdata) > 5:
                EC = splitdata[5]
            Mnx = splitdata[1]
            EcNumber[Mnx] = EC
            try:
                direction = MnxDirPref[Mnx] 
                if direction == '1':
                    MnxSim[Mnx]=S1
                    MnxDirUsed[Mnx]= '1'
                elif direction == '-1':
                    MnxSim[Mnx]=S2
                    MnxDirUsed[Mnx]= '-1'
                else:
                    if S1 >= S2:
                        MnxSim[Mnx]=S1
                        MnxDirUsed[Mnx]= '1'
                    elif S2 > S1:
                        MnxSim[Mnx]=S2
                        MnxDirUsed[Mnx]= '-1'
            except KeyError:
                MnxDirPref[Mnx] = "N/A"   # for missing Keys?
                if S1 >= S2:
                    MnxSim[Mnx]=S1
                else:
                    MnxSim[Mnx]=S2
        fileout.close()
            
        return (MnxSim, MnxDirPref, MnxDirUsed, SMILES, EcNumber)
        
    else:

        fileout = open(os.path.join(outdir, "results_quickRsim.txt"), 'r')
        for line in fileout:
            splitdata = line.split()
            S1 = splitdata[2]
            S2 = splitdata[3]
            SMILES = splitdata[4]
            EC = ''
            if len(splitdata) > 5:
                EC = splitdata[5]
            Mnx = splitdata[1]
            EcNumber[Mnx] = EC
            if S1 > S2:
                MnxDirUsed[Mnx]='1'
                MnxSim[Mnx]=S1
            elif S2 > S1:
                MnxDirUsed[Mnx]='-1'
                MnxSim[Mnx]=S2
            elif S2 == S1:
                MnxDirUsed[Mnx]='0'
                MnxSim[Mnx]=S2                
        fileout.close()              
        
        return (MnxSim, MnxDirPref, MnxDirUsed, SMILES, EcNumber)

def reactionSmiles(rxnSmilesFile):
    rsmi = {}
    with open(rxnSmilesFile) as handler:
        header = handler.readline()
        for line in handler:
            row = line.rstrip().split(',')
            if len(row) > 1:
                rid = row[0]
                rs1 = row[1]
                lr = rs1.split('>>')
                rs2 = lr[1]+'>>'+lr[0]
                rsmi[rid] = (rs1, rs2)
                
    return rsmi
   
def pepstats(file, outdir):
    outfile = os.path.join(outdir, "results.pepstats")
    args = ("pepstats -sequence {0} -outfile ".format(file) + outfile)
    os.system(args)
    
    f = open(outfile, "r")
    
    hydrop = {}
    weight = {}
    isoelec = {}
    polar = {}
    
    for line in f:
        if "PEPSTATS of" in line:
            splitdata = line.split()
            seq = splitdata[2]
        elif "Molecular weight = " in line:
            splitdata = line.split()
            w = splitdata[3]
            weight[seq] = w
        elif "Isoelectric Point = " in line:
            splitdata = line.split()
            i = splitdata[3]
            isoelec[seq] = i
        elif "Polar	" in line:
            splitdata = line.split()
            percent = splitdata[3]
            polar[seq] = percent
            seq
    return (hydrop, weight, isoelec, polar)

def noAmbiguousSeqs(infile, outfile):
    """ Remove ambigous amino acid codes """
    from Bio.Data.IUPACData import protein_letters_1to3, extended_protein_values
    from Bio import SeqIO
    from Bio.Seq import Seq
    from Bio.SeqRecord import SeqRecord
    from Bio.Alphabet import generic_protein

    newrecords = []
    for record in SeqIO.parse(infile, "fasta"):
        newseq = ''
        for aa in record.seq:
            if aa not in protein_letters_1to3:
                newseq += extended_protein_values[aa][0]
            else:
                newseq += aa
        newrecords.append( SeqRecord(Seq(newseq), id = record.id, description = record.description) )
    SeqIO.write(newrecords, outfile, "fasta")
    
def garnier(file, outdir):
    fixfile = file+'.fix.fasta'
    noAmbiguousSeqs(file, fixfile)
    outfile = os.path.join(outdir, "garnier.txt")
    
    args = ("garnier -sequence {0} -outfile ".format(fixfile) + outfile)
    os.system(args)
    
    f = open(outfile, "r")

    helices = {}
    sheets = {}
    turns = {}
    coils = {}
    
    for line in f:
        if "Sequence:" in line:
            splitdata = line.split()
            seq = splitdata[2]
        elif "percent:" in line:
            percents = line.split()
            h = percents[3]
            e = percents[5]
            t = percents[7]
            c = percents[9]
            helices[seq] = h
            sheets[seq] = e
            turns[seq] = t
            coils[seq] = c

    return (helices, sheets, turns, coils)
            
def doMSA(finallistfile, outdir):
    outfile = os.path.join(outdir, "sequences.score_ascii")
    outfile_html = os.path.join(outdir, "sequences.score_ascii.score_html")
    outfile_aln = os.path.join(outdir, "sequences.score_ascii.fasta_aln")
    align_html = os.path.join(outdir, "sequences_score.html")
    align_fasta = os.path.join(outdir, "sequences_aln.fasta")
    treefile = os.path.join(outdir, "sequences.dnd")
    args = ("t_coffee -in {0} -mode quickaln -output=score_ascii,fasta_aln,score_html -outfile ".format(finallistfile) +outfile+ " -newtree "+treefile)
    os.system(args)
    if os.path.exists(outfile_html):
        os.rename(outfile_html, align_html)
    if os.path.exists(outfile_aln):
        os.rename(outfile_aln, align_fasta)
    
    f = open(outfile, "r")

    cons = {}
    
    for line in f:
        if "   :  " in line:
            splitdata = line.split()
            upid = splitdata[0]
            score = splitdata[2]
            cons[upid] = score
            
    return (cons)

def read_csv(csvfile):
    rows = []
    if os.path.exists(csvfile):
        with open(csvfile) as handler:
            cv = csv.reader(handler)
            head = next(cv)
            for row in cv:
                rows.append(row)
    return head, rows

def write_csv(csvfilepath, head, rows):
    with open (csvfilepath, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(head)
        for r in rows:
            writer.writerow(r)


def sort_rows(rows, columns):
    for i in range(len(columns), 0, -1):
        key = columns[i-1]
        if key != 0:
            if key < 0:
                try:
                    rows.sort(key = lambda x: -float(x[abs(key)-1]))
                except:
                    rows.sort(key = lambda x: x[abs(key)-1], reverse=True)
            else:
                rows.sort(key = lambda x: x[key-1])
    return rows

    
def analyse(rxnInput, targ, datadir, outdir, csvfilename, pdir=0, host='83333', NoMSA=False, pc=None):
    

    datadir = os.path.join(datadir)
    outdir = os.path.join(outdir)
    
#    rxnname = os.path.splitext(rxn)[0]
#    csvname = rxnname.rsplit('/', 1)[-1]
    
    if csvfilename: 
        csvfilename = csvfilename
    else:
        csvfilename = "results_selenzy.csv"
    

    print ("Running quickRsim...")
    try:
        (MnxSim, MnxDirPref, MnxDirUsed, Smiles, EcNumber) = getMnxSim(rxnInput, datadir, outdir, pdir, pc)
    except:
        return False


    print ("Acquiring databases...")
    if pc is not None:
        sequence = pc.sequence
        names = pc.names
        descriptions = pc.descriptions
        osource = pc.osource
        seqorg = pc.seqorg
        tax = pc.tax
        MnxToUprot = pc.MnxToUprot
        upclst = pc.upclst
        clstrep = pc.clstrep
        smir = pc.smir
    else:
        (sequence, names, descriptions, osource) = readFasta(datadir, "seqs.fasta")
        seqorg = seqOrganism(datadir, "seq_org.tsv")
        tax = readTaxonomy(datadir, "org_lineage.csv")
        with open(os.path.join(datadir, 'MnxToUprot.json')) as f:
            MnxToUprot = json.load(f)
        with open (os.path.join(datadir, 'upclst.json')) as f2:
            upclst = json.load(f2)
        with open (os.path.join(datadir, 'clstrep.json')) as f3:
            clstrep= json.load(f3)
        smiFile = os.path.join(datadir, 'reac_smi.csv')
        smir = {}
        if os.path.exists(smiFile):
            smir = reactionSmiles(smiFile)


    targplus = int(targ)*3
    list_mnx = sorted(MnxSim, key=MnxSim.__getitem__, reverse=True)[:int(targplus)]  #allow user to manipulate window of initial rxn id list
    fastaFile = os.path.join(outdir, "sequences.fasta")
    f = open(fastaFile, "w")
    print ("Creating initial MNX list...")
    targets = set()
    UprotToMnx = {}
    
    # first creating fasta file, f, for further data extraction
    for x in list_mnx:
        up = MnxToUprot.get(x)  
        if up is not None:
            for y in up:
                if len(targets) >= int(targ):    # allow user to manipulate desired number of entries for resulting table
                    break
                else:
                    UprotToMnx[y] = x
                    try:
#                        cn = clustar.getClustNo(y)
#                        repid = clustar.getRepID(cn)
                        targets.add(y)
                    except KeyError:
                        pass 
  
    for t in targets:
        try: 
            seq = sequence[t]
            print ('>{0} \n{1}'.format(t, seq), file=f)
        except KeyError:
            pass

                    
    f.close()
    #analysis of FinalList of sequences
    (hydrop, weight, isoelec, polar) = pepstats(fastaFile, outdir)
    (helices, sheets, turns, coils) = garnier(fastaFile, outdir)
    if not NoMSA:
        cons = doMSA(fastaFile, outdir)
    
    print ("Acquiring sequence properties...")
    # final table, do all data and value storing before this!
    tdist = {}
    rows = []
    for y in targets:
        try:
            desc = descriptions[y] 
            org = osource[y]
            mnx = UprotToMnx[y]
            cn = upclst.get(y)
            repid = clstrep[cn]
            rxnsimpre = float(MnxSim[mnx])
            rxnsim = float("{0:.5f}".format(rxnsimpre))
            try:
                conservation = float(cons[y])
            except:
                conservation = 0.0
            try:
                ecid = EcNumber[mnx]
            except:
                ecid = ''
            try:

                h = helices[y]
                e = sheets[y]
                t = turns[y]
                c = coils[y]
            except:
                h = 0.0
                e = 0.0
                t = 0.0
                c = 0.0
            w = weight[y]
            i = isoelec[y]
            pol = polar[y]
            
            rxndirused = MnxDirUsed[mnx]
            rxndirpref = MnxDirPref[mnx]
            
            mnxSmiles = ''
            if mnx in smir:
                if rxndirused == 1:
                    mnxSmiles = smir[mnx][0]
                else:
                    mnxSmiles = smir[mnx][1]
            if org not in tdist:
                if y in seqorg:
                    tdist[org] = taxDistance(tax, host, seqorg[y][0])
                else:
                    tdist[org] = '-'
            rows.append( (y, desc, org, tdist[org], mnx, ecid, cn, repid, conservation, rxnsim, rxndirused, rxndirpref, h, e, t, c, w, i, pol, Smiles, mnxSmiles) )

       
        except KeyError:
            pass

    sortrows = sort_rows(rows, (-10, -9, 4) )


    head = ('Seq. ID','Description', 'Organism Source', 'Tax. distance', 'Rxn. ID', 'EC Number', 'Clust. No.', 'Rep. ID.', 'Consv. Score',
            'Rxn Sim.', "Direction Used", "Direction Preferred",
            '% helices', '% sheets', '% turns', '% coils', 'Mol. Weight', 'Isoelec. Point', 'Polar %','Query', 'Hit')

    write_csv(os.path.join(outdir, csvfilename), head, sortrows)

    print ("CSV file created.")
    return True
    
    
def arguments():
    parser = argparse.ArgumentParser(description='SeqFind script for Selenzy')
    parser.add_argument('rxn', 
                        help='Input reaction [default = rxn file]')
    parser.add_argument('-tar', type=float, default=20,
                        help='Number of targets to display in results [default = 20]')
    parser.add_argument('-d', type=float, default=0,
                        help='Use similiarity values for preferred reaction direction only [default=0 (OFF)]')
    parser.add_argument('datadir',
                        help='specify data directory for required databases files, please end with slash')
    parser.add_argument('outdir',
                        help='specify output directory for all output files, including final CSV file, please end with slash')
    parser.add_argument('-outfile',
                        help='specify non-default name for CSV file output')
    parser.add_argument('-NoMSA', action='store_true',
                        help='Do not compute MSA/conservation scores')
    parser.add_argument('-smarts', action='store_true',
                        help='Input is a reaction SMARTS string')
    parser.add_argument('-smartsfile', action='store_true',
                        help='Input is a reaction SMARTS file')
    parser.add_argument('-host', type=str, default='83333',
                        help='Host organism taxon id [default: E. coli]')
    arg = parser.parse_args()
    return arg

if __name__ == '__main__':
    arg = arguments()
    
    newpath = os.path.join(arg.outdir)
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    if arg.smarts is not None:
        rxnInput = ['-smarts', arg.rxn]
    elif arg.smartsfile:
        rxnInput = ['-smartsfile', arg.rxn]
    else:
        rxnInput = ['-rxn', arg.rxn]

    analyse(rxnInput, arg.tar, arg.datadir, arg.outdir, arg.outfile, arg.d, arg.host, NoMSA=arg.NoMSA)













