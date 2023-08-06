#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Date: 2022/7/20
# @Author: 2022 PCL
import os
import sys
from loguru import logger

from pcl_pangu.context import check_context
from pcl_pangu.model.launcher_torch import launch
from pcl_pangu.model.evolution.config_evolution import DISTRUBUTED_CONFIG, model_config_gpu


def train(config):
    print('----------------------------- training config -----------------------------')
    print("> Base Model: [evolution]")
    print("> Model Size: [{}]".format(config.model))
    print("> data_path: {}".format(config.data_path))
    print("> global batch_size: {}".format(config.batch_size))
    print("> save to path: {}".format(config.save))
    print('------------------------------ end of config -----------------------------')

    if check_context()=='pytorch':
        script_args = config._get_training_script_args()
        py_script = '/panguAlpha_pytorch/pretrain_evolution.py'
        run_pt(script_args, py_script)

    else:
        print("ERROR: wrong backend.")
        return 1

def fine_tune(config):
    print('--------------------------- finetune config -----------------------------')
    print("> Base Model: [evolution]")
    print("> Model Size: [{}]".format(config.model))
    print("> data_path: {}".format(config.data_path))
    print("> global batch_size: {}".format(config.batch_size))
    print("> save to path: {}".format(config.save))
    print('---------------------------- end of config -------------------------------')

    if check_context()=='pytorch':
        script_args = config._get_training_script_args()
        py_script = '/panguAlpha_pytorch/pretrain_evolution.py'
        run_pt(script_args, py_script)

    else:
        print("ERROR: wrong backend.")
        return 1

def inference(config,top_k=1,top_p=0.9,input=None,input_file=None,output_file=None,
              generate_max_tokens=128,oneCardInference=True):
    assert generate_max_tokens > 0 and generate_max_tokens<=800, "> generate_max_tokens always in (0, 800]"
    print('--------------------------- inference config --------------------------')
    print("> Base Model: [evolution]")
    print("> Model Size: [{}]".format(config.model))
    print("> global batch_size: {}".format(config.batch_size))
    print("> generate_max_tokens length: {}".format(generate_max_tokens))
    print('---------------------------- end of config ----------------------------')

    if check_context()=='pytorch':
        from .config_evolution import DEFAULT_CONFIG
        DEFAULT_CONFIG['finetune'] = True
        config.batch_size = 1
        script_args = config._get_training_script_args(oneCardInference=oneCardInference)
        py_script = '/panguAlpha_pytorch/tools/generate_samples_epangu.py'
        script_args.append('--top-k={}'.format(top_k))
        script_args.append('--top-p={}'.format(top_p))
        if input is not None:
            script_args.append('--sample-input={}'.format(input.encode('utf-8').hex()))
        if input_file is not None:
            script_args.append('--sample-input-file={}'.format(input_file))
        if output_file is not None:
            script_args.append('--sample-output-file={}'.format(output_file))
        if generate_max_tokens is not None:
            script_args.append('--generate_max_tokens={}'.format(generate_max_tokens))

        script_args.append('--isEvolution=True')
        run_pt(script_args, py_script)

    else:
        print("ERROR: wrong backend.")
        return 1


def run_pt(script_args, py_script, **kwargs):
    current_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(current_dir + '/panguAlpha_pytorch')

    py_script = current_dir + py_script
    logger.info("> Running {} with args: {}".format(py_script, script_args))

    launch(training_script=py_script,
           training_script_args=script_args,
           **DISTRUBUTED_CONFIG,
           **kwargs)
    return 0


if __name__ == '__main__':
    config = model_config_gpu()
    inference(config)
