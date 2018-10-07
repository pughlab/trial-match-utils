import argparse

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--maf-file", type=str, required=True,
                        help="VEP annotated MAF file e.g data_mutations_extended.txt")
    parser.add_argument("-c", "--cna-file", type=str, required=True,
                        help="discrate copy number data from GISTIC2 e.g data_CNA.txt")
    parser.add_argument("-v", "--variants", type=str, required=True,
                        help="oncoKB all annotated variants e.g allAnnotatedVariants.txt")
    parser.add_argument("-o", "--output-file", type=str, required=True,
                        help="output genomic data file for trial match e.g genomic.csv")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="debug mode print to stdout")
    return parser.parse_args()

def get_cna_table(cna_file, debug=False):
    cna_dict = {}
    with open(cna_file) as f:
        header = f.readline()
        header_parts = header.strip().split("\t")
        if debug:
            print (header_parts)
            for idx, val in enumerate(header_parts):
                print (idx, val)
        for line1 in f.readlines():
            parts = line1.strip().split("\t")
            one_dic = {}
            for i, (name, val) in enumerate(zip(header_parts[1:], parts[1:])):
                one_dic[name] = val
            cna_dict[parts[0]] = one_dic
        if debug:
            print (cna_dict.keys())
    return cna_dict

def get_oncoKB_table(variant_file, debug):
    oncoKB_dict = {}
    with open(variant_file) as f:
        header = f.readline()
        if debug:
            for idx, val in enumerate(header.strip().split("\t")):
                print (idx, val)
        for line in f.readlines()[1:]:
            if debug:
                print (line)
            parts2 = line.strip().split("\t")
            key =  "%s:p.%s"%(parts2[3],parts2[4])
            oncoKB_dict[key] = {"ONCOGENICITY": parts2[6],"MUTATION_EFFECT":parts2[7]}
    if debug:
        print (oncoKB_dict.keys())
        print (oncoKB_dict.values())
    return oncoKB_dict

def prepare_genomic_data(args):
    cna_dict = get_cna_table(args.cna_file, args.debug)
    cna_lookup_dic = {"-2":"Homozygous Deletion", "-1":"Heterozygous Deletion", "0":"Neutral", "1":"Gain", "2":"High Amplification"}
    oncoKB_dict = get_oncoKB_table(args.variants, args.debug)

    with open(args.output_file,'w') as of, open(args.maf_file) as f:
        f_line = f.readline()
        header = f_line.strip().split("\t")
        if args.debug:
            for idx, val in enumerate(header):
                print(idx, val)
        of.write('SAMPLE_ID,TRUE_HUGO_SYMBOL,TRUE_PROTEIN_CHANGE,TRUE_VARIANT_CLASSIFICATION,VARIANT_CATEGORY,' +
                 'CNV_CALL,WILDTYPE,CHROMOSOME,POSITION,TRUE_CDNA_CHANGE,REFERENCE_ALLELE,TRUE_TRANSCRIPT_EXON,' +
                 'CANONICAL_STRAND,ALLELE_FRACTION,ONCOGENICITY,MUTATION_EFFECT\n')
        for line in f.readlines()[1:]:
            items = line.strip().split("\t")
            sample_id = items[15].replace("-TD","-Exome")
            if sample_id.startswith("OCT-01"):
                sample_id = sample_id.replace("_Tumour", "-555Panel")
            print (sample_id)
            # -TD becomes -Exome
            #_Tumour becomes -555Panel, but ONLY for OCT-01 samples
            if args.debug:
                print(items[41], items[40])
            try:
                fraction = int(items[41])/(int(items[40])+int(items[41]))
                if args.debug:
                    print (fraction)
            except:
                fraction = 0.0

            try:
                key = cna_dict[items[0]][sample_id]
                cna_call = cna_lookup_dic[str(key)]
                print ("cnv call: %s" %cna_call)
            except:
                cna_call = ''

            key2 = ":".join([items[0], items[36]])
            print (key2)
            try:
                oncogenicity = oncoKB_dict[key2]["ONCOGENICITY"]
            except:
                oncogenicity = "Unknown"
            try:
                mutation_effect = oncoKB_dict[key2]["MUTATION_EFFECT"]
            except:
                mutation_effect = "Unknown"
            try:
                tier = " ".join(items[93:100])
            except:
                tier = 'Unknown'
            line = ",".join([sample_id, items[0], items[36], items[8], items[9].replace("SNP","MUTATION"),
                             cna_call,'false', items[4], items[5], items[34], items[10],
                             items[38].split("/")[0], items[7], str(fraction), oncogenicity,mutation_effect])
            print (line)
            of.write("%s\n"%(line))

def main():
    args = get_options()
    if args.debug:
        print (args)
    prepare_genomic_data(args)

if __name__ == "__main__":
    main()