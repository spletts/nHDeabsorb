"""Get table of absorption values from nHDeabsorb"""


from nHDeabsorb import get_absorption
import pkg_resources


# Another option: get the absorption values as table, using table which contains energies
fn_spec = pkg_resources.resource_filename('nHDeabsorb', 'sample_data/sed.dat')
absorb_for_spec = get_absorption.make_absorption_table(fn_sed_data=fn_spec,
                                                    absorption_model='tbabs_abund_wilm',
                                                    nh=0.15,
                                                    calc_avg_using_endpoints=False,
                                                    fn_out='absorption_values.csv')
