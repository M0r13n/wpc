from wpc.bar import print_progress_bar_in_background_thread
from wpc.scan import guess_interface, scan, analyze, load_ouis

DURATION = 20
OUTFILE = "/tmp/dump.out"

if __name__ == "__main__":
    i = guess_interface()
    print("Found interface", i)
    t1 = print_progress_bar_in_background_thread(DURATION)

    sp = scan(i, OUTFILE, DURATION)

    t1.join(DURATION)

    ouis = load_ouis("./oui.txt")
    analyze(OUTFILE, ouis)
