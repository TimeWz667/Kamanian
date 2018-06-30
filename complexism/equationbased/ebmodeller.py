from complexism.mcore import AbsBlueprintMCore
from copy import deepcopy
from epidag.factory import get_workshop

__author__ = 'TimeWz667'


class BlueprintODEEBM(AbsBlueprintMCore):
    def __init__(self, name):
        AbsBlueprintMCore.__init__(self, name)
        self.DT = 0.1
        self.ObsDT = 1
        self.ODE = None
        self.Measurements = list()
        self.ObsStocks = list()

    def set_fn_ode(self, fn):
        self.ODE = fn

    def add_fn_measure(self, mea):
        pass

    def


    def get_parameter_hierarchy(self, **kwargs):
        pass

    def generate(self, name, **kwargs):
        pass

    def to_json(self):
        pass

    def clone(self, mod_src, **kwargs):
        pass

    def from_json(self, js):
        pass


class BlueprintCoreODE(AbsBlueprintMCore):
    def __init__(self, name, tar_pc, tar_dc):
        AbsBlueprintMCore.__init__(self, name, {'dt': 1, 'fdt': 0.1}, pc=tar_pc, dc=tar_dc)
        self.Behaviours = list()
        self.Obs_s_t_b = list(), list(), list()

    def add_behaviour(self, be_name, be_type, **kwargs):
        if be_name in self.Behaviours:
            return
        self.Behaviours.append({'Name': be_name,
                                'Type': be_type,
                                'Args': dict(kwargs)})

    def set_observations(self, states=None, transitions=None, behaviours=None):
        s, t, b = self.Obs_s_t_b
        s = states if states else s
        t = transitions if transitions else t
        b = behaviours if behaviours else b
        self.Obs_s_t_b = s, t, b

    def generate(self, name, logger=None, **kwargs):
        pc, dc = kwargs['pc'], kwargs['dc'],
        meta = MetaCoreEBM(self.TargetedPCore, self.TargetedDCore, self.Name)
        mc = CoreODE(dc)
        mod = ODEModel(name, mc, pc=pc, meta=meta, **self.Arguments)

        ws = get_workshop('EBM_BE')
        resources = {
            'states': list(dc.States.keys()),
            'transitions': list(dc.Transitions.keys())
        }
        resources.update(pc.Locus)
        # lock
        ws.renew_resources(resources)

        for be in self.Behaviours:
            mod.ODE.add_behaviour(ws.create(be, logger=logger))

        ws.clear_resources()
        # release
        sts, trs, bes = self.Obs_s_t_b
        if sts:
            for st in sts:
                mod.add_obs_state(st)
        if trs:
            for tr in trs:
                mod.add_obs_transition(tr)
        if bes:
            for be in bes:
                mod.add_obs_behaviour(be)
        return mod

    def clone(self, mod_src, **kwargs):
        # copy model structure
        dc_new = kwargs['dc'] if 'dc' in kwargs else mod_src.DCore
        pc_new = kwargs['pc'] if 'pc' in kwargs else mod_src.DCore

        mod_new = mod_src.clone(dc=dc_new, pc=pc_new)
        mod_new.Obs.TimeSeries = mod_src.Obs.TimeSeries.copy()

        return mod_new

    def to_json(self):
        js = dict()
        js['Name'] = self.Name
        js['Arguments'] = self.Arguments
        js['Type'] = 'CoreODE'
        js['TargetedPCore'] = self.TargetedPCore
        js['TargetedDCore'] = self.TargetedDCore
        js['Behaviours'] = self.Behaviours
        js['Observation'] = {k: v for k, v in zip(['State', 'Transition', 'Behaviour'], self.Obs_s_t_b)}

        return js

    @staticmethod
    def from_json(js):
        bp = BlueprintCoreODE(js['Name'], js['TargetedPCore'], js['TargetedDCore'])
        for k, v in js['Arguments']:
            bp.set_arguments(k, v)
        bp.Behaviours = deepcopy(js['Behaviours'])
        obs = js['Observation']
        bp.set_observations(obs['State'], obs['Transition'], obs['Behaviour'])
        return bp
