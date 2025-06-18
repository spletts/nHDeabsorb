"""Get array of absorption values from nHDeabsorb"""


from nHDeabsorb import get_absorption


# One option: get the absorption values as array, using array of energies
absorb = get_absorption.xspec_absorption_component(ebin_min=[0.4, 0.5],
                                                ebin_max=[0.5, 0.6],
                                                absorption_model='tbabs_abund_wilm',
                                                calc_avg_using_endpoints=False,
                                                nh=0.15)
