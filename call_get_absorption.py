import nHDeabsorb.get_absorption as get_absorption


get_absorption.make_absorption_table(fn_sed_data="src/nHDeabsorb/sample_sed.dat", absorption_model="phabs", nh=0.157, fn_out="absorption.csv")
