""" Example python script to generate a YAML config file which can be used to run a training with nanotron. Refer to "examples" section in the `/README.md` for more information."""
import math
import os

from nanotron.config import (
    CheckpointsArgs,
    Config,
    DataArgs,
    GeneralArgs,
    LoggingArgs,
    LRSchedulerArgs,
    MambaConfig,
    MambaInit,
    ModelArgs,
    NanotronExperimentLoggerArgs,
    OptimizerArgs,
    ParallelismArgs,
    PretrainDatasetsArgs,
    TensorboardLoggerConfig,
    TokenizerArgs,
    TokensArgs,
    WandbLoggerConfig,
)
from nanotron.logging import human_format

ssm_cfg_dtype = "bfloat16"
ssm_cfg = {
    "d_state": 16,
    "d_conv": 4,
    "expand": 2,
    "dt_rank": "auto",
    "dt_min": 0.001,
    "dt_max": 0.1,
    "dt_init": "random",
    "dt_scale": 1.0,
    "dt_init_floor": 1e-4,
    "conv_bias": True,
    "bias": False,
    "use_fast_path": True,
}
# https://huggingface.co/state-spaces/mamba-790m/blob/main/config.json
model_config = MambaConfig(
    d_model=1536,
    num_hidden_layers=48,
    vocab_size=50277,
    ssm_cfg=ssm_cfg,
    rms_norm=True,
    fused_add_norm=True,
    residual_in_fp32=True,
    pad_vocab_size_multiple=8,
    # Custom
    dtype=ssm_cfg_dtype,
    rms_norm_eps=1e-5,
)

# NOTE: vocab_size is normally round up to the nearest multiple of 10. But here, we don't really care
tie_embedding = model_config.vocab_size * model_config.d_model  # model_config.vocab_size * model_config.d_model
expand = 2 if ("expand" not in ssm_cfg) else ssm_cfg["expand"]
ngroups = 1 if ("ngroups" not in ssm_cfg) else ssm_cfg["ngroups"]
d_state = 16 if ("d_state" not in ssm_cfg) else ssm_cfg["d_state"]
d_conv = 4 if ("d_conv" not in ssm_cfg) else ssm_cfg["d_conv"]
dt_rank = (
    math.ceil(model_config.d_model / 16)
    if ("dt_rank" not in ssm_cfg or ssm_cfg["dt_rank"] == "auto")
    else ssm_cfg["dt_rank"]
)

d_inner = int(expand * model_config.d_model)
in_proj = model_config.d_model * d_inner * 2

# conv1d.weight = out_channels * (in_channels // groups) * kernel_size
# conv1d.bias = out_channels
conv1d = d_inner * int(d_inner / d_inner) * d_conv + d_inner
# linear.weight = out_features * in_features
in_proj = model_config.d_model * d_inner * 2 + 0
x_proj = d_inner * (dt_rank + d_state * 2) + 0
out_proj = d_inner * model_config.d_model + 0
dt_proj = dt_rank * d_inner + d_inner
A_log = d_inner * d_state
D = d_inner
norm = model_config.d_model
norm_f = model_config.d_model

num_params = human_format(
    (
        tie_embedding
        + model_config.num_hidden_layers * (A_log + D + in_proj + conv1d + x_proj + dt_proj + out_proj + norm + norm_f)
    )
).replace(".", "p")

print(f"Model has {num_params} parameters")

seed = 42

general = GeneralArgs(project="test", run="mamba", seed=seed)

checkpoints_path = os.path.dirname(os.path.dirname(__file__)) + "/checkpoints"
os.makedirs(checkpoints_path, exist_ok=True)
checkpoints = CheckpointsArgs(checkpoints_path=checkpoints_path, checkpoint_interval=10)

model = ModelArgs(
    init_method=MambaInit(initializer_range=0.02, rescale_prenorm_residual=True, n_residuals_per_layer=1),
    model_config=model_config,
)

tokenizer = TokenizerArgs("gpt2")

optimizer = OptimizerArgs(
    zero_stage=0,
    weight_decay=0.01,
    clip_grad=1.0,
    accumulate_grad_in_fp32=False,  # NOTE(fmom): because we are using PP=TP=DP=1
    adam_eps=1e-08,
    adam_beta1=0.9,
    adam_beta2=0.95,
    torch_adam_is_fused=True,
    learning_rate_scheduler=LRSchedulerArgs(
        learning_rate=3e-4, lr_warmup_steps=10, lr_warmup_style="linear", lr_decay_style="cosine", min_decay_lr=1e-5
    ),
)

parallelism = ParallelismArgs(
    dp=2,
    pp=2,
    tp=2,
    pp_engine="1f1b",
    tp_mode="ALL_REDUCE",
    tp_linear_async_communication=False,
)

tokens = TokensArgs(sequence_length=2048, train_steps=100, micro_batch_size=2, batch_accumulation_per_replica=1)

data = DataArgs(
    dataset=PretrainDatasetsArgs(
        hf_dataset_or_datasets={"roneneldan/TinyStories": 1.0},
        hf_dataset_config_name=None,
        hf_dataset_splits="train",
        dataset_processing_num_proc_per_process=24,
        dataset_overwrite_cache=False,
        text_column_name="text",
    ),
    seed=seed,
)

logging = LoggingArgs(
    log_level="info",
    log_level_replica="info",
    iteration_step_info_interval=1,
)

experiment_logger = NanotronExperimentLoggerArgs(
    tensorboard_logger=TensorboardLoggerConfig(tensorboard_dir="/fsx/ferdinandmom/logs/tb_logs/"),
    wandb_logger=WandbLoggerConfig(wandb_project="test", wandb_entity="bouteille"),
)

config = Config(
    general=general,
    checkpoints=checkpoints,
    parallelism=parallelism,
    model=model,
    tokenizer=tokenizer,
    optimizer=optimizer,
    logging=logging,
    tokens=tokens,
    data=data,
    experiment_logger=experiment_logger,
    profiler=None,
)

if __name__ == "__main__":
    dir = os.path.dirname(__file__)

    # Save config as YAML file
    config.save_as_yaml(f"{dir}/config_mamba.yaml")

    # You can now train a model with this config using `/run_train.py`
