import logging
from typing import Any, Dict, Tuple

from midas.util.upgrade_module import UpgradeModule

LOG = logging.getLogger(__name__)


class BlackstartModule(UpgradeModule):
    """Blackstart agents upgrade module for MIDAS 1.0."""

    def __init__(self):
        super().__init__(
            module_name="blackstart",
            default_scope_name="midasmv",
            default_sim_config_name="BlackstartAgents",
            default_import_str=(
                "blackstart.blackstart_mas.mango_mosaik_api:MangoSimulator"
            ),
            default_cmd_str=("%(python)s -m market_agents.simulator %(addr)s"),  # TODO
            log=LOG,
        )

        self.models = {}
        self.port_off = 0
        self.agent_unit_model_map = {}

    def check_module_params(self, module_params: Dict[str, Any]):
        """Check the module params and provide default values."""
        module_params.setdefault("start_date", self.scenario.base.start_date)
        module_params.setdefault("module_name_unit_models", "der")
        module_params.setdefault("host", "localhost")
        module_params.setdefault("port", 5655)
        module_params.setdefault("check_inbox_interval", 0.1)
        module_params.setdefault(
            "schedule_length",
            int(
                self.scenario.base.forecast_horizon_hours
                * 3600
                / module_params["step_size"]
            ),
        )

        module_params.setdefault("optimization_weights", [1.0, 0.0])
        module_params.setdefault("max_ict_enabled_buses", 0)
        module_params.setdefault(
            "schedule_weights",
            [1 / module_params["schedule_length"]] * module_params["schedule_length"],
        )

    def check_sim_params(self, module_params: Dict[str, Any]):
        """Check the params for a certain simulator instance."""

        self.sim_params.setdefault("grid_name", self.scope_name)
        self.sim_params.setdefault("start_date", module_params["start_date"])
        self.sim_params.setdefault("host", module_params["host"])
        self.sim_params.setdefault("port", int(module_params["port"]) + self.port_off)
        self.port_off += 1
        self.sim_params.setdefault("check_inbox_interval", 0.1)
        self.sim_params.setdefault("schedule_length", module_params["schedule_length"])
        self.sim_params.setdefault(
            "optimization_weights", module_params["optimization_weights"]
        )
        self.sim_params.setdefault(
            "schedule_weights", module_params["schedule_weights"]
        )
        self.sim_params.setdefault(
            "max_ict_enabled_buses", module_params["max_ict_enabled_buses"]
        )
        self.sim_params.setdefault("holon_topology", create_default_topology())
        self.sim_params.setdefault("der_mapping", create_default_der_mapping())
        self.sim_params.setdefault("load_mapping", create_default_load_mapping())
        self.sim_params.setdefault("sgen_mapping", create_default_sgen_mapping())
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        self.sim_params.setdefault(
            "grid_load_mapping", create_default_grid_load_mapping()
        )
        self.sim_params.setdefault(
            "grid_sgen_mapping", create_default_grid_sgen_mapping()
        )
        self.sim_params.setdefault("bc_buses", [0])
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        self.sim_params.setdefault("switch_mapping", create_default_switch_mapping())
        self.sim_params.setdefault(
            "ict_node_mapping", create_default_ict_node_mapping()
        )
        self.sim_params.setdefault("bc_agent_id", "BlackstartSwitchAgent-7")

        if self.scenario.base.no_rng:
            self.sim_params["seed"] = self.scenario.create_seed()
        else:
            self.sim_params.setdefault("seed", self.scenario.create_seed())

    def start_models(self):
        """Start all models defined in the mapping of a certain simulator."""
        mod_ctr = 0
        model = "BlackstartUnitAgent"
        for _ in self.sim_params["der_mapping"]:
            mod_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)
            mod_params = {
                "check_inbox_interval": self.sim_params["check_inbox_interval"]
            }
            self.start_model(mod_key, model, mod_params)
            mod_ctr += 1

        for _ in self.sim_params["load_mapping"]:
            mod_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)
            mod_params = {
                "check_inbox_interval": self.sim_params["check_inbox_interval"]
            }
            self.start_model(mod_key, model, mod_params)
            mod_ctr += 1

        for _ in self.sim_params["sgen_mapping"]:
            mod_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)
            mod_params = {
                "check_inbox_interval": self.sim_params["check_inbox_interval"]
            }
            self.start_model(mod_key, model, mod_params)
            mod_ctr += 1

        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        for _ in self.sim_params["grid_load_mapping"]:
            mod_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)
            mod_params = {
                "check_inbox_interval": self.sim_params["check_inbox_interval"]
            }
            self.start_model(mod_key, model, mod_params)
            mod_ctr += 1

        for _ in self.sim_params["grid_sgen_mapping"]:
            mod_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)
            mod_params = {
                "check_inbox_interval": self.sim_params["check_inbox_interval"]
            }
            self.start_model(mod_key, model, mod_params)
            mod_ctr += 1
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

        model = "BlackstartSwitchAgent"
        for _ in self.sim_params["switch_mapping"]:
            mod_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)
            mod_params = {
                "check_inbox_interval": self.sim_params["check_inbox_interval"]
            }
            self.start_model(mod_key, model, mod_params)
            mod_ctr += 1

        model = "BlackstartICTNodeAgent"
        for _ in self.sim_params["ict_node_mapping"]:
            mod_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)
            mod_params = {
                "check_inbox_interval": self.sim_params["check_inbox_interval"]
            }
            self.start_model(mod_key, model, mod_params)
            mod_ctr += 1

    # def _find_der_mapping(self):
    #     mappings = self.scenario.get_shared_mappings()
    #     key = f"{self.sim_params['module_name_unit_models']}_{self.scope_name}"

    #     for name, mapping in mappings.items():
    #         if key in name and "eid_mapping" in name:
    #             return mapping

    #     return {}

    def get_unit_model(self, unit_model, bus, uidx) -> Tuple[str, str]:
        der_models = self.scenario.find_models(
            self.sim_params["module_name_unit_models"]
        )

        candidates = []
        key = f"{unit_model.lower()}_{bus}"
        for model_key in der_models:
            if key in model_key:
                candidates.append(model_key)

        if not candidates:
            LOG.error(
                "No unit model with name '%s', bus '%d', and index '%d' " "found!",
                unit_model,
                bus,
                uidx,
            )
            raise ValueError(
                "No unit model found for mapping: " f"[{unit_model}, {bus}, {uidx}]"
            )

        return candidates[uidx], der_models[candidates[uidx]].full_id

    def connect(self):
        mod_ctr = 0
        mod_ctr = self._connect_to_ders(mod_ctr)
        mod_ctr = self._connect_to_loads(mod_ctr)
        mod_ctr = self._connect_to_sgens(mod_ctr)
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        mod_ctr = self._connect_to_grid_entities(mod_ctr, "load")
        mod_ctr = self._connect_to_grid_entities(mod_ctr, "sgen")
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        self._connect_to_switches(mod_ctr)
        # mod_ctr = 0
        # ict_mappings = self.scenario.get_ict_mappings()

        # for market_agent_key, (unit_model_key, _) in self.agent_unit_model_map.items():
        #     if self.scenario.base.with_ict:
        #         # provides a list of mapping, that ict can use to see
        #         # where to connect between the entities if initial data
        #         # is needed, it can be given. if not given, it is not
        #         # needed
        #         ict_mappings.append(
        #             {
        #                 "sender": unit_model_key,
        #                 "receiver": market_agent_key,
        #                 "sender_before_ict": True,
        #                 "receiver_before_ict": False,
        #                 "attrs": [("schedule", "schedule")],
        #             }
        #         )
        #         ict_mappings.append(
        #             {
        #                 "sender": market_agent_key,
        #                 "receiver": unit_model_key,
        #                 "sender_before_ict": False,
        #                 "receiver_before_ict": True,
        #                 "attrs": [("set_q_schedule", "schedule")],
        #                 "initial_data": ["set_q_schedule"],
        #             }
        #         )
        #     else:
        #         self.connect_entities(unit_model_key, market_agent_key, ["schedule"])
        #         self.connect_entities(
        #             market_agent_key,
        #             unit_model_key,
        #             [("set_q_schedule", "schedule")],
        #             time_shifted=True,
        #             initial_data={"set_q_schedule": None},
        #         )
        #     mod_ctr += 1

    def _connect_to_ders(self, mod_ctr):
        # TODO
        model = "BlackstartUnitAgent"
        for unit_model in self.sim_params["der_mapping"].values():
            mod_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)
            unit_mod = self.get_unit_model(unit_model)
            self.connect_entities(unit_mod, mod_key, ["flexibilities"])
            self.connect_entities(
                mod_key,
                unit_mod,
                ["schedule"],
                time_shifted=True,
                initial_data={"schedule": None},
            )
            mod_ctr += 1
        return mod_ctr

    def _connect_to_loads(self, mod_ctr):
        # Define connections for load agents
        # TODO
        model = "BlackstartUnitAgent"
        for load_model in self.sim_params["load_mapping"].values():
            mod_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)

            if len(load_model) > 3:
                for load_id in load_model[3]:

                    load_mod = self.get_load_model(load_model, load_id)

                    # bus_number = household_params['household_mapping'][load.eid]['bus']
                    self.connect_entities2(load_mod, mod_key, ["p_mw"])
                    # world.connect(loads[bus_number], load_agent, 'p_mw')
            else:
                load_mod = self.get_load_model(load_model)
                self.connect_entities2(load_mod, mod_key, ["p_mw"])
            mod_ctr += 1
        return mod_ctr

    def _connect_to_sgens(self, mod_ctr):
        # Define connections for sgen agents
        # TODO
        model = "BlackstartUnitAgent"
        for sgen_model in self.sim_params["sgen_mapping"].values():
            mod_key = self.gen_mod_key(model.lower(), mod_ctr)

            if len(sgen_model) > 3:
                for sgen_id in sgen_model[3]:

                    sgen_mod = self.get_sgen_model(sgen_model, sgen_id)

                    self.connect_entities2(sgen_mod, mod_key, ["p_mw"])

            else:
                sgen_mod = self.get_sgen_model(sgen_model)
                self.connect_entities2(sgen_mod, mod_key, ["p_mw"])

            mod_ctr += 1
        return mod_ctr

    def _connect_to_switches(self, mod_ctr):
        # Define connections for switch agents

        model = "BlackstartSwitchAgent"
        for switch_cfg in self.sim_params["switch_mapping"].values():
            agent_key = self.scenario.generate_model_key(self, model.lower(), mod_ctr)
            for idx, switch in enumerate(switch_cfg["adjacent_switches"]):
                switch_key = self.get_switch_model(switch)
                switch_attr = f"switch_state_{idx}"
                self.connect_entities(switch_key, agent_key, [("closed", switch_attr)])
                self.connect_entities(
                    agent_key,
                    switch_key,
                    [(switch_attr, "closed")],
                    time_shifted=True,
                    initial_data={switch_attr: False},
                )
            mod_ctr += 1
        return mod_ctr

    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    def _connect_to_grid_entities(self, mod_ctr, mtype):
        # Define connections for grid load agents (directly connected to grid)
        assert mtype in ["load", "sgen"], "mtype must be one of (load, sgen)"
        model = "BlackstartUnitAgent"
        for load_model in self.sim_params[f"grid_{mtype}_mapping"].values():
            agent_model_key = self.scenario.generate_model_key(
                self, model.lower(), mod_ctr
            )
            entity_model_key = self.get_grid_model(load_model, mtype)
            self.connect_entities(entity_model_key, agent_model_key, ["p_mw"])
            mod_ctr += 1
        return mod_ctr


    def connect_to_db(self):
        # db_key = self.scenario.find_first_model("store", "database")[0]
        # for agent_key in self.agent_unit_model_map:
        #     self.connect_entities(
        #         agent_key, db_key, ["set_q_schedule", "reactive_power_offer"]
        #     )
        pass

    def get_grid_model(self, load_model, mtype):
        bus_number, load_id = load_model[:2]
        models = self.scenario.find_grid_entities(
            self.sim_params["grid_name"], mtype, endswith=f"_1"
        )
        if models:
            for key in models:
                # Return first match
                return key

        raise ValueError(
            f"Grid entity for {self.sim_params['grid_name']}, {mtype} "
            f"at bus {bus_number} not found!"
        )

    def get_switch_model(self, switch):
        mod_type, eidx = switch.split("-")

        models = self.scenario.find_grid_entities(
            self.sim_params["grid_name"], mod_type, eidx
        )
        if models:
            for key in models:
                # Return first match
                return key

        raise ValueError(
            f"Grid entity for {self.sim_params['grid_name']}, {mod_type} "
            f"with index {eidx} not found!"
        )

        # for key, entity in self.scenario.items():
        #     if key.startswith(f"powergrid_{self.sim_name}"):

        #         # FIXME: select the first matching model
        #         if f"{mod_type}_{eidx}" in key:
        #             return key


# def _create_default_mapping():
#     unit_map = [["PV", 2, 0], ["PV", 3, 0], ["PV", 2, 1], ["PV", 3, 1]]
#     return unit_map


def create_default_topology():
    topo = (
        {
            "agent8": [
                "BlackstartSwitchAgent-6",
                "BlackstartSwitchAgent-7",
                "BlackstartSwitchAgent-8",
            ],
            "agent3": ["BlackstartUnitAgent-2", "BlackstartUnitAgent-3"],
            "agent1": ["BlackstartUnitAgent-1", "BlackstartUnitAgent-5"],
            "agent2": ["BlackstartUnitAgent-0", "BlackstartUnitAgent-4"],
        },
    )
    return topo


def create_default_der_mapping():
    der_map = {}
    return der_map


#### SET TO EMPTY DICT######
def create_default_load_mapping():
    load_map = {}
    return load_map


def create_default_sgen_mapping():
    sgen_map = {}
    return sgen_map


"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


def create_default_grid_load_mapping():
    grid_load_map = {}
    return grid_load_map


def create_default_grid_sgen_mapping():
    grid_sgen_map = {}
    return grid_sgen_map


"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"


def create_default_switch_mapping():
    switch_map = {
        "BlackstartSwitchAgent-6": {
            "own_bus": 1,
            "adjacent_switches": {"switch-0": {"other_bus": 2, "access": True}},
            "assigned_speaker": "BlackstartUnitAgent-2",
        },
        "BlackstartSwitchAgent-7": {
            "own_bus": 2,
            "adjacent_switches": {
                "switch-0": {"other_bus": 1, "access": False},
                "switch-1": {"other_bus": 3, "access": True},
            },
            "assigned_speaker": "BlackstartUnitAgent-0",
        },
        "BlackstartSwitchAgent-8": {
            "own_bus": 3,
            "adjacent_switches": {"switch-1": {"other_bus": 2, "access": False}},
            "assigned_speaker": "BlackstartUnitAgent-1",
        },
    }
    return switch_map


def create_default_ict_node_mapping():
    ict_node_map = {}
    return ict_node_map
