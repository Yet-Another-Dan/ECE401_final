import m5
from m5.objects import *
from gem5.resources.resource import obtain_resource
import os

# obtain_resource("getting-started-benchmark-suite")


class L1D(Cache):
    size = '8kB'
    assoc = 4
    tag_latency = 3
    data_latency = 3
    response_latency = 3
    mshrs = 16
    tgts_per_mshr = 20

class L1I(L1D):
    size = '8kB'
    assoc = 4
    tag_latency = 3
    data_latency = 3
    response_latency = 3
    mshrs = 16
    tgts_per_mshr = 20

class L2(Cache):
    size = '2MB'
    assoc = 16
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

def init_system(system,args):
    system.clk_domain = SrcClockDomain(clock='4GHz', voltage_domain=VoltageDomain())
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange ('16GiB')]
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR4_2400_8x8()
    system.mem_ctrl.dram.range = root.system.mem_ranges[0]

#    system.cpu = RiscvO3CPU()
#   system.cpu = RiscVMinorCPU()
    system.cpu = cpu_types[args.cpu]()
    system.cpu.branchPred = bpred_types[args.bpred]()
    if args.cpu == "o3":
        system.cpu.issueWidth = args.width


    system.membus = SystemXBar()

    system.cpu.createInterruptController()
    system.cpu.addTwoLevelCacheHierarchy(L1I(), L1D(), L2())
    system.cpu.connectBus(system.membus)
    system.mem_ctrl.port = system.membus.mem_side_ports
    system.system_port = system.membus.cpu_side_ports

def init_process(root,args):
    # print(os.getcwd())
    exe_path = 'tests/custom/' + args.bin
    root.system.workload = SEWorkload.init_compatible(exe_path)
    process = Process()
    process.executable = exe_path
    process.cwd = os.getcwd()
    process.cmd = [exe_path,"hello world", 1]
    root.system.cpu.workload = process
    root.system.cpu.createThreads()


import argparse
if __name__ == "__m5_main__":

    cpu_types = {
            "minor":RiscvMinorCPU,
            "o3":RiscvO3CPU,
        }

    bpred_types = {
            "local":LocalBP,
            "bimode":BiModeBP,
            "tournament":TournamentBP,
            "tage":TAGE,
        }
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cpu",
        type=str,
        choices=list(cpu_types.keys()),
        default="minor",
        help="CPU model to use",
    )

    parser.add_argument(
        "--bpred",
        type=str,
        choices=list(bpred_types.keys()),
        default="local",
        help="bpred model to use",
    )

    parser.add_argument(
        "--width",
        type=int,
        default = 1,
        help = "Issue width of OoO processor",
    )

    parser.add_argument(
        "--bin",
        type=str,
        default="matrix-multiply",
        help = "binary to run in gem5/tests/custom",
    )
    args = parser.parse_args()
    root = Root()
    root.full_system = False
    root.system = System()
    init_system(root.system,args)
    init_process(root,args)
    m5.instantiate()
    exit_event = m5.simulate()
    print(f'{exit_event.getCause()} ({exit_event.getCode()}) @ {m5.curTick()}')

