from dzdy import *
from epidag import DirectedAcyclicGraph, SimulationModel

__author__ = 'TimeWz667'


def copy_agent(ag_src, dc_new, tr_ch=None):
    if not tr_ch:
        tr_ch = dc_new.Transitions
    ag_new = Agent(ag_src.Name, dc_new[ag_src.State.Name])

    if not tr_ch:
        return ag_new

    for tr, tte in ag_src.Trans.items():
        if tr.Name in tr_ch:
            continue
        ag_new.Trans[dc_new.Transitions[tr.Name]] = tte
    ag_new.Info.update(ag_src.Info)
    return ag_new


class DirectorABM:
    def __init__(self):
        self.PCores = dict()
        self.DCores = dict()
        self.MCores = dict()

    def add_pcore(self, pc):
        name = pc.Name
        if isinstance(pc, SimulationModel):
            self.PCores[name] = pc
            print('PCore {} added'.format(name))
        else:
            print('Adding failed')

    def read_pcore(self, script):
        pc = DirectedAcyclicGraph(script).get_simulation_model()
        self.add_pcore(pc)

    def load_pcore(self, path):
        with open(path, 'r') as f:
            self.read_pcore(str(f.read()))

    def restore_pcore(self, js):
        pc = SimulationModel.build_from_json(js)
        self.add_pcore(pc)

    def add_dcore(self, dc):
        if isinstance(dc, AbsBluePrint):
            self.DCores[dc.Name] = dc
            print('Dcore {} added'.format(dc.Name))
        else:
            print('Adding failed')

    def read_dcore(self, script):
        bp = build_from_script(script)
        self.add_dcore(bp)

    def load_dcore(self, path):
        with open(path, 'r') as f:
            self.read_dcore(f.read())

    def restore_dcore(self, js):
        bp = build_from_json(js)
        self.add_dcore(bp)

    def read_mcore(self, script):
        pass

    def load_mcore(self, path):
        with open(path, 'r') as f:
            self.read_mcore(f.read())

    def restore_mcore(self, js):
        pass

    def get_pcore(self, name):
        return self.PCores[name]

    def get_dcore(self, name):
        return self.DCores[name]

    def get_mcore(self, name):
        return self.MCores[name]

    def list_pcores(self):
        return list(self.PCores.keys())

    def list_dcores(self):
        return list(self.DCores.keys())

    def list_mcores(self):
        return list(self.MCores.keys())

    def generate_pc_dc(self, pc, dc, new_name=None):
        pc = self.PCores[pc].sample_core()
        dc = self.DCores[dc]
        if not dc.is_compatible(pc):
            raise ValueError('Not compatible pcore')
        return pc, dc.generate_model(pc, new_name)

    def generate_abm(self, mc, name=None):
        if not name:
            name = mc
        mc = self.MCores[mc]
        pc, dc = mc.TargetedPCore, mc.TargetedDCore
        pc, dc = self.generate_pc_dc(pc, dc, name)
        return mc.generate(name, pc, dc)

    def new_abm(self, name, tar_pcore, tar_dcore):
        bp_abm = AgentBasedModelBluePrint(name, tar_pcore, tar_dcore)
        self.MCores[name] = bp_abm
        return bp_abm

    def copy_abm(self, mod_src, tr_tte=True, pc_new=None):
        # copy model structure
        mc = mod_src.Meta.Prototype
        mod_new = self.generate_abm(mc)
        time_copy = mod_src.TimeEnd if mod_src.TimeEnd else 0
        mod_new.TimeEnd = mod_src.TimeEnd
        if pc_new:
            mod_new.PCore = pc_new
        else:
            pc_new = mod_new.PCore
        dc_new = mod_new.DCore
        trs = self.get_dcore(self.MCores[mc].TargetedDCore).Transitions
        ags_src = mod_src.Pop.Agents

        # copy agents
        if tr_tte:
            _, ds = pc_new.difference(mod_src.PCore)
            tr_ch = [k for k, v in trs.items() if v['Dist'] in ds]
            print('Changed transitions: {}'.format(', '.join(tr_ch)))
            for k, v in ags_src.items():
                mod_new.Pop.Agents[k] = copy_agent(v, dc_new, tr_ch)
        else:
            for k, v in ags_src.items():
                mod_new.Pop.Agents[k] = copy_agent(v, dc_new)

        # rebuild population and networks
        mod_new.Pop.Eve.Last = mod_src.Pop.Eve.Last

        ags_new = mod_new.Pop.Agents
        mod_new.Pop.Networks.match(mod_src.Pop.Networks, ags_new)

        # rebuild behaviours and modifiers
        for be_src, be_new in zip(mod_src.Behaviours.values(), mod_new.Behaviours.values()):
            be_new.match(be_src, ags_src, ags_new, time_copy)

        for ag in mod_new.agents:
            ag.update(time_copy)

        mod_new.Obs.TimeSeries = mod_src.Obs.TimeSeries.copy()

        return mod_new
