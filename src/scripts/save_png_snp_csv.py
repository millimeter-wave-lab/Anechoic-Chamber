import pyvisa
import time
import sys

SIGLENT_IP = "10.17.90.141"
RESOURCE = f"TCPIP0::{SIGLENT_IP}::INSTR"

def main():
    if len(sys.argv) != 2:
        print("Usage: python save_png_snp.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    vna_png_name = f"VNA {filename}.png"
    vna_snp_name = f"VNA {filename}.s1p"

    sa_png_name = f"SA {filename}.png"
    sa_csv_name = f"SA {filename}.csv"


    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource(RESOURCE)

    instrument.write(':INST VNA')

    print("Waiting 90 seconds before saving files...")
    time.sleep(90)

    print("Saving PNG screenshot...")
    instrument.write(f':MMEM:STOR PNG, "{vna_png_name}"')

    print("Saving Touchstone S1P file...")
    instrument.write(f':MMEM:STOR SNP, "{vna_snp_name}"')

    time.sleep(5)

    instrument.write(':INST SA')
    time.sleep(10)

    print("Saving PNG screenshot...")
    instrument.write(f':MMEM:STOR PNG, "{sa_png_name}"')

    print("Saving CSV file...")
    instrument.write(f':MMEM:STOR CSV, "{sa_csv_name}"')

    print("Files saved successfully.")
    instrument.close()

if __name__ == "__main__":
    main()
