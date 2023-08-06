import pandapower as pp
import random


def build_grid():
    """Create the evaluation grid for moo cohda (based on cigre topology)"""

    list_of_sgens_unscaled = [0.0, 0.0, 0.0, 0.0, 0.02, 0.02, 0.03, 0.75, 0.03, 0.552, 0.054, 0.01, 0.75]
    # list_of_sgens = [0.0, 0.0, 0.0, 0.0, 0.14, 0.14, 0.441, 0.21, 5.25, 0.21, 3.864, 0.378, 0.07, 5.25]
    list_of_sgens = [round(i * 7, 3) for i in list_of_sgens_unscaled]
    list_of_loads = [0.0, 4.845, 0.502, 0.728, 0.548, 0.077, 0.587, 0.574, 0.543, 0.33, 5.016, 0.034, 0.540]
    bc_bus_sgen = 0.441
    bc_bus_load = 0.432

    # random.seed(139233)
    # shuffle list
    random.shuffle(list_of_sgens)
    random.shuffle(list_of_loads)

    print("list of sgens: ", list_of_sgens)
    print("list of loads: ", list_of_loads)

    grid = pp.create_empty_network()

    ext = pp.create_bus(grid, name="110 kV bar", vn_kv=110, type='b', geodata=[0, 0])
    bus1 = pp.create_bus(grid, name="bus1", vn_kv=20, type='b', geodata=[0, 0])
    bus2 = pp.create_bus(grid, name="bus2", vn_kv=20, type='b', geodata=[0, -1])
    bus3 = pp.create_bus(grid, name="bus3", vn_kv=20, type='b', geodata=[0, -2])
    bus4 = pp.create_bus(grid, name="bus4", vn_kv=20, type='b', geodata=[0, -3])
    bus5 = pp.create_bus(grid, name="bus5", vn_kv=20, type='b', geodata=[0, -4])
    bus6 = pp.create_bus(grid, name="bus6", vn_kv=20, type='b', geodata=[0, -5])
    bus7 = pp.create_bus(grid, name="bus7", vn_kv=20, type='b', geodata=[0, -6])
    bus8 = pp.create_bus(grid, name="bus8", vn_kv=20, type='b', geodata=[0, -7])
    bus9 = pp.create_bus(grid, name="bus9", vn_kv=20, type='b', geodata=[0, -8])
    bus10 = pp.create_bus(grid, name="bus10", vn_kv=20, type='b', geodata=[0, -9])
    bus11 = pp.create_bus(grid, name="bus11", vn_kv=20, type='b', geodata=[0, -9])
    bus12 = pp.create_bus(grid, name="bus12", vn_kv=20, type='b', geodata=[0, -9])
    bus13 = pp.create_bus(grid, name="bus13", vn_kv=20, type='b', geodata=[0, -9])
    bus14 = pp.create_bus(grid, name="bus14", vn_kv=20, type='b', geodata=[0, -9])

    pp.create_ext_grid(grid, ext)
    pp.create_transformer(grid, name="trafo0-1", hv_bus=0, lv_bus=1, std_type="25 MVA 110/20 kV")
    pp.create_transformer(grid, name="trafo0-12", hv_bus=0, lv_bus=12, std_type="25 MVA 110/20 kV")

    pp.create_line(grid, bus1, bus2, name="line1-2", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus2, bus3, name="line2-3", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus3, bus4, name="line3-4", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus3, bus8, name="line3-8", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus4, bus5, name="line4-5", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus4, bus11, name="line4-11", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus5, bus6, name="line5-6", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus6, bus7, name="line6-7", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus7, bus8, name="line7-8", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus8, bus9, name="line8-9", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus8, bus14, name="line8-14", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus9, bus10, name="line9-10", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus10, bus11, name="line10-11", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus12, bus13, name="line12-13", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")
    pp.create_line(grid, bus13, bus14, name="line13-14", length_km=3, std_type="NA2XS2Y 1x185 RM/25 12/20 kV")

    pp.create_switch(grid, ext, bus1, "b", type="CB", closed=False)  # for external grid
    pp.create_switch(grid, ext, bus12, "b", type="CB", closed=False)
    pp.create_switch(grid, bus1, bus2, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus2, bus3, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus3, bus4, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus3, bus8, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus4, bus5, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus4, bus11, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus5, bus6, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus6, bus7, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus7, bus8, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus8, bus9, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus8, bus14, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus9, bus10, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus10, bus11, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus12, bus13, "b", type="LBS", closed=False)
    pp.create_switch(grid, bus13, bus14, "b", type="LBS", closed=False)

    pp.create_sgen(grid, bus1, p_mw=list_of_sgens[0], q_mvar=0, name='SGEN 1')
    pp.create_sgen(grid, bus2, p_mw=list_of_sgens[1], q_mvar=0, name='SGEN 2')
    pp.create_sgen(grid, bus3, p_mw=list_of_sgens[2], q_mvar=0, name='SGEN 3')
    pp.create_sgen(grid, bus4, p_mw=list_of_sgens[3], q_mvar=0, name='SGEN 4')
    pp.create_sgen(grid, bus5, p_mw=list_of_sgens[4], q_mvar=0, name='SGEN 5')
    pp.create_sgen(grid, bus6, p_mw=list_of_sgens[5], q_mvar=0, name='SGEN 6')
    pp.create_sgen(grid, bus7, p_mw=list_of_sgens[6], q_mvar=0, name='SGEN 7')
    pp.create_sgen(grid, bus8, p_mw=bc_bus_sgen, q_mvar=0, name='SGEN 8')
    pp.create_sgen(grid, bus9, p_mw=list_of_sgens[7], q_mvar=0, name='SGEN 9')
    pp.create_sgen(grid, bus10, p_mw=list_of_sgens[8], q_mvar=0, name='SGEN 10')
    pp.create_sgen(grid, bus11, p_mw=list_of_sgens[9], q_mvar=0, name='SGEN 11')
    pp.create_sgen(grid, bus12, p_mw=list_of_sgens[10], q_mvar=0, name='SGEN 12')
    pp.create_sgen(grid, bus13, p_mw=list_of_sgens[11], q_mvar=0, name='SGEN 13')
    pp.create_sgen(grid, bus14, p_mw=list_of_sgens[12], q_mvar=0, name='SGEN 14')

    pp.create_load(grid, bus1, p_mw=list_of_loads[0], q_mvar=0, name='Load 1')
    pp.create_load(grid, bus2, p_mw=list_of_loads[1], q_mvar=0, name='Load 2')
    pp.create_load(grid, bus3, p_mw=list_of_loads[2], q_mvar=0, name='Load 3')
    pp.create_load(grid, bus4, p_mw=list_of_loads[3], q_mvar=0, name='Load 4')
    pp.create_load(grid, bus5, p_mw=list_of_loads[4], q_mvar=0, name='Load 5')
    pp.create_load(grid, bus6, p_mw=list_of_loads[5], q_mvar=0, name='Load 6')
    pp.create_load(grid, bus7, p_mw=list_of_loads[6], q_mvar=0, name='Load 7')
    pp.create_load(grid, bus8, p_mw=bc_bus_load, q_mvar=0, name='Load 8')
    pp.create_load(grid, bus9, p_mw=list_of_loads[7], q_mvar=0, name='Load 9')
    pp.create_load(grid, bus10, p_mw=list_of_loads[8], q_mvar=0, name='Load 10')
    pp.create_load(grid, bus11, p_mw=list_of_loads[9], q_mvar=0, name='Load 11')
    pp.create_load(grid, bus12, p_mw=list_of_loads[10], q_mvar=0, name='Load 12')
    pp.create_load(grid, bus13, p_mw=list_of_loads[11], q_mvar=0, name='Load 13')
    pp.create_load(grid, bus14, p_mw=list_of_loads[12], q_mvar=0, name='Load 14')

    return grid
