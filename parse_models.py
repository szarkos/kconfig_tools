#!/usr/bin/python3 -u

import json
import glob
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("models", help='')
parser.add_argument("outfile", help='')
args = parser.parse_args()

ARCHS = ["x86", "arm64"]  # Just the architecture we care about

models = glob.glob(args.models + r"/*.model")

all_data = {}
for model_file in models:
    arch = model_file.split("/")[-1]
    arch = re.sub("\.model", "", arch)

    if arch not in ARCHS:
        continue

    all_data[arch] = {}
    with open(model_file, "rt") as handle:
        data = handle.read()

    for line in data.splitlines():
        if re.match(r"FILE.*\.(c|S)", line) is None:
            continue

        try:
            fname, full_conf = line.split(r" ", 1)
            full_conf = re.sub(r"_MODULE(?P<mod>(?!\w)[()\s]*)", r"\g<mod>", full_conf, flags=re.ASCII)
            full_conf = re.sub(r'"', "", full_conf)
            full_conf = full_conf.strip()

            conf_vars = re.findall(r"CONFIG_[A-Z0-9_]*", full_conf)
            if not conf_vars:
                raise
            conf_vars = list(dict.fromkeys(conf_vars))

        except Exception:
            fname = line
            full_conf = None
            conf_vars = []

        fname = fname.strip()
        fname = re.sub(r"^FILE_", "", fname)

#        print(fname, full_conf, conf_vars)
        all_data[arch][fname] = { "full_conf": full_conf, "conf_vars": conf_vars }


#main_archs = ["x86", "arm64"]
#platform = {}
#for arch in main_archs:
#    all_data[arch]["non_arch_files"] = {}
#    for other_arch in all_data:
#        if arch == other_arch:
#            continue

#        non_arch_files = { key: all_data[other_arch][key] for key in set(all_data[other_arch]) - set(all_data[arch]) }
#        all_data[arch]["non_arch_files"].update(non_arch_files)

        #  print(arch, other_arch)
        #  print(non_arch_files)

with open(args.outfile, 'wt') as handle:
    data_out = json.dumps(all_data, indent=4)
    print(data_out, file=handle, flush=True)

