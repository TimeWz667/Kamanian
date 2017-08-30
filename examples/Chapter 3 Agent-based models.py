from dzdy import *


__author__ = 'TimeWz667'

ctrl = DirectorDCPC()
ctrl.load_pc('scripts/pSIR.txt')
ctrl.load_dc('scripts/SIR_BN.txt')


pc = ctrl.get_pc('pSIR').sample_core()
dc = ctrl.get_dc('SIR_BN').generate_model(pc)

abm = AgentBasedModel('', dc, pc)
print(abm)

abm.Pop.add_network('N1', get_network('BA', {'m': 2}))
abm.Pop.add_network('N2', get_network('BA', {'m': 2}))

install_behaviour(abm, 'Net', 'NetShock', {'s_src': 'Inf', 't_tar': 'Infect', 'net': 'N1'})
abm.add_obs_be('Net')
abm.add_obs_st('Inf')
simulate(abm, {'Sus': 50, 'Inf': 50}, fr=0, to=10)
print(abm.output())