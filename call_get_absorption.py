import nHDeabsorb.get_absorption as get_absorption
#import src.nHDeabsorb.get_absorption as get_absorption


get_absorption.make_absorption_table(fn_sed_data="src/nHDeabsorb/sample_sed.dat", absorption_model="phabs", nh=0.157, fn_out="absorption.csv")
absorb = get_absorption.xspec_absorption_component(ebin_min=[0.3, 0.4, 0.5], ebin_max=[0.5, 0.6, 0.7], absorption_model="tbabs_abund_wilm", nh=0.157)


