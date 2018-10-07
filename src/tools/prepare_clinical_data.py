import datetime
import argparse

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sample-file", type=str, required=True,
                        help="cbioportal clinical sample file e.g data_clinical_samples.txt")
    parser.add_argument("-p", "--patient-file", type=str, required=True,
                        help="cbioportal clinical patient file e.g data_clinical_patients.txt")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="output clinical file for trial match e.g clinical.csv")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="debug mode print to stdout")
    return parser.parse_args()

def prepare_sample_data(args):
    p_dic = {}
    with open(args.patient_file) as pf:
        for line in pf.readlines()[5:]:
            items = line.strip().split("\t")
            if args.debug:
                for idx, val in enumerate(items):
                    print (idx, val)
            email = 'NA'
            full_name = "NA"
            if items[1] and items[1] != "NA":
                email = items[2]
                full_name = items[1]
            p_dic[items[0]] = dict(
                ORD_PHYSICIAN_NAME = full_name,
                ORD_PHYSICIAN_EMAIL = email,
                AGE=items[3],
                BIRTH_DATE = (datetime.date.today()-datetime.timedelta(days=int(items[3])*365)).strftime("%Y-%m-%d")
                            if items[3] != 'NA' else "NA",
                GENDER=items[4],
                ETHNICITY = items[5],
                ER_STATUS = items[9],
                PR_STATUS = items[10],
                HER2_STATUS = items[11],
                CENTRE = items[17],
                VITAL_STATUS = items[18]
            )
    if args.debug:
        print (p_dic)

    with open(args.out_file, 'w') as of, open(args.sample_file) as sf:
        if args.debug:
            for line in sf.readlines()[4:5]:
                parts = line.strip().split("\t")
                for idx, val in enumerate(parts):
                    print (idx, val)
        of.write('SAMPLE_ID,ORD_PHYSICIAN_NAME,ORD_PHYSICIAN_EMAIL,ONCOTREE_PRIMARY_DIAGNOSIS_NAME,CANCER_TYPE,REPORT_DATE,' +
                    'BIRTH_DATE,AGE,GENDER,ETHNICITY,VITAL_STATUS,ER_STATUS,PR_STATUS,HER2_STATUS,CENTRE,PATIENT_ID,DFCI_MRN\n')
        count = 1
        for line1 in sf.readlines()[5:]:
            items1 = line1.strip().split("\t")
            if args.debug:
                print (items1)
                for idx, val in enumerate(parts):
                    print (idx, val)
            if items1[6] and items1[6] != "NA": #11/7/2017
                d_parts = items1[6].split("/")
                REPORT_DATE = "%s-%s-%s"%(d_parts[-1],d_parts[0],d_parts[1])
            else:
                REPORT_DATE = datetime.date.today().strftime("%Y-%m-%d")

            sample_items = [items1[1],p_dic[items1[0]]['ORD_PHYSICIAN_NAME'], p_dic[items1[0]]['ORD_PHYSICIAN_EMAIL'],items1[2],items1[3],REPORT_DATE,
            p_dic[items1[0]]['BIRTH_DATE'],p_dic[items1[0]]['AGE'],p_dic[items1[0]]['GENDER'],p_dic[items1[0]]['ETHNICITY'],
            p_dic[items1[0]]['VITAL_STATUS'],p_dic[items1[0]]['ER_STATUS'],p_dic[items1[0]]['PR_STATUS'],p_dic[items1[0]]['HER2_STATUS'],
            p_dic[items1[0]]['CENTRE'],items1[0],str(count)]
            if args.debug:
                print (len(sample_items))
            new_line = ",".join(sample_items)
            if args.debug:
                print (new_line)
            of.write("%s\n"%(new_line))
            count += 1

def main():
    args = get_options()
    if args.debug:
        print (args)
    prepare_sample_data(args)

if __name__ == "__main__":
    main()