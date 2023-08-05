from pathlib import Path
import sys
import tempfile
import re

from optilog.blackbox import SystemBlackBox, ExecutionConstraints
from optilog.running import ParsingInfo
from optilog.solvers.sat.utils.loaders import GeneralParser

def matching_output(path):
    r = re.compile(r"__@MATCH#@REGEX#__")
    match = None
    with open(path, 'r') as f:
        for line in f:
            content = r.match(line)
            if content:
                match = content.group(1)
    
    return match

if __name__ == '__main__':

    CWD = Path(__file__).parent
    SOLVER=f"{CWD}/algo.py"
    RUNSOLVER="__@RUNSOLVER#@PATH#__"
    MEM_LIMIT="__@MEM#@LIMIT#__"
    WALL_LIMIT="__@WALL#@LIMIT#__"
    CPU_LIMIT="__@CPU#@LIMIT#__"
    RUN_OBJ="__@RUN#@OBJ#__"
    CONFIGURATOR_NAME="__@CONFIGURATOR#@NAME#__"
    COST_MAX="__@COST#@MAX#__"

    args = sys.argv
    if CONFIGURATOR_NAME == "smac":
        INSTANCE = sys.argv[1]
        INSTANCE_SPECIFICS = sys.argv[2]
        CUTOFF = sys.argv[3]
        RUNLEN = sys.argv[4]
        SEED = sys.argv[5]
        args = args[6:]
    elif CONFIGURATOR_NAME == "gga":
        INSTANCE = sys.argv[1]
        CUTOFF = sys.argv[2]
        SEED = sys.argv[3]
        args = args[4:]
    
    print(f"INSTANCE: {INSTANCE}, SEED: {SEED}", flush=True)
    print(f"PARAMETERS: {args}", flush=True)

    dir = tempfile.mkdtemp()
    tmp_work_dir = Path(dir)
    solver_file = tmp_work_dir / "solver.txt"
    time_file = tmp_work_dir / "time.txt"

    print(f'Temporary output directory: {tmp_work_dir}', flush=True)

    parsing_info = ParsingInfo()

    parsing_info.add_filter('max_cpu_time', '^Maximum CPU time exceeded:(.)')
    parsing_info.add_filter('max_wall_time', '^Maximum wall clock time exceeded:(.)')
    parsing_info.add_filter('max_mem', '^Maximum VSize exceeded: (\d+)', cast_to=int)
    parsing_info.add_filter('cpu_time', '^CPU time \(s\): (\d+\.\d+)', cast_to=float)
    parsing_info.add_filter('usr_time', '^CPU user time \(s\): (\d+\.\d+)', cast_to=float)
    
    parsing_info.add_filter('solver_status', '^Child status: (\d+)', cast_to=int)

    class ACSystemBlackBox(SystemBlackBox):
        def _get_runsolver_extra_args(self):
            return ["--watcher-data", time_file, "--solver-data", solver_file]
            
    bb = ACSystemBlackBox(
        arguments=[
            sys.executable, SOLVER,
            '--instance', SystemBlackBox.Instance,
            '--seed', SystemBlackBox.Seed,
        ] + args,
        parsing_info=parsing_info,
        runsolver=RUNSOLVER,
    )

    def parse_or_none(x):
        if x == "None": return None
        return int(x)

    bb.run(
        INSTANCE,
        SEED,
        constraints=ExecutionConstraints(
            memory=f"{MEM_LIMIT}M",
            wall_time=parse_or_none(WALL_LIMIT),
            cpu_time=parse_or_none(CPU_LIMIT)
        )
    )
    exit_code = bb.returncode
    print('Runsolver DONE', exit_code, flush=True)

    parser = GeneralParser(parsing_info)
    with open(time_file, 'r') as f:
        for line in f:
            # print(line, end='', flush=True)
            parser.process_line(line)
    parsed = parser.parsed

    if exit_code == 1:
        status = "ABORT"
        quality = 0
    else:
        quality = parsed['usr_time'] # we are trying to optimize the runtime.
        if RUN_OBJ == "quality":
            quality = matching_output(solver_file)
    
        if parsed['max_mem'] is not None:
            status = "MEMOUT"
        elif (parsed['max_cpu_time'] is not None or parsed['max_wall_time'] is not None) and (RUN_OBJ == "runtime" or quality is None):
            status = "TIMEOUT"
            if CONFIGURATOR_NAME == "smac":
                status = 99999999
        elif (RUN_OBJ == "runtime" and parsed['solver_status'] == 0) or (RUN_OBJ == "quality" and quality is not None):
            status = "SUCCESS"
        else:
            # Otherwise crash
            status = "CRASHED"
            with open(solver_file, 'r') as fin:
                print(fin.read(), end="", flush=True)

    if CONFIGURATOR_NAME == "smac":
        results = f"{status}, {parsed['cpu_time']}, {RUNLEN}, {quality}, {SEED}, {INSTANCE_SPECIFICS}"
        print(f"Result of this algorithm run: {results}", flush=True)
    elif CONFIGURATOR_NAME == "gga":
        if status == "ABORT":
            print(f"GGA {status}", flush=True) 
        elif status == "SUCCESS":
            print(f"GGA {status} {quality}", flush=True)
        else:
            print(f"GGA {status} {COST_MAX}", flush=True)

    sys.exit(parsed['solver_status'])
