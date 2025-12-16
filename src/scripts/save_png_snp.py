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

    png_name = f"{filename}.png"
    snp_name = f"{filename}.s1p"

    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource(RESOURCE)
    instrument.write(':INST VNA')
    print("Waiting 90 seconds before saving files...")
    time.sleep(10)

    print("Saving PNG screenshot...")
    instrument.write(f':MMEM:STOR PNG, "{png_name}"')

    print("Saving Touchstone S1P file...")
    instrument.write(f':MMEM:STOR SNP, "{snp_name}"')

    print("Files saved successfully.")
    instrument.close()

if __name__ == "__main__":
    main()
