from dsframework.base.trainer.pl_wrapper import *
from pl_wrapper.network_module import generatedProjectNameNetworkModule

##
# @file
# @brief config.py, holds all configurations in dictionary format.

## ModelCheckpoint - pytorch lightning auto save callback.
checkpoint_callback = ModelCheckpoint(
    save_top_k=2,
    save_last=False,
    monitor="val_loss",
    mode="min",
    filename="my-chkpnt-{epoch:02d}-{val_loss:.2f}",
)

## EarlyStopping - pytorch lightning early stopping callback.
early_stopping_callback = EarlyStopping(
    monitor='val_loss',
    patience=10,  # number of val checks with no improvement
    mode='max'
)

## Configurations, can add or remove parameters with two exception: metrics and the trainer_config is the exact parameters
## the pytorch lightning trainer class accepts, it is used: pl.Trainer(**config['trainer_config'])
config = {
    'general_config': {
        'learning_rate': 1e-3,
        'loss_function': F.cross_entropy,
        'batch_size_train': 32,
        'batch_size_eval': 32,
        'num_classes': None,
        'num_classes_confusion_matrix': 10,
        'num_workers': 1,
        'seed': 42,
        'nnetwork': generatedProjectNameNetworkModule.nnetwork,
        'save_model': True,
        'model_name': 'my_model.ckpt',
        'save_dataset': True
    },
    'trainer_config': {  # training_config is dedicated to pytorch lighting trainer module and uses its exact params.
        'max_epochs': 1,
        'accelerator': None,  # 'cpu', 'gpu', 'tpu', 'ipu', 'auto', None
        'devices': None,  # number of accelerators: -1-all, 1, 3, 4...8, None, [1, 3]-gpu ids, None
        'strategy': None,  # 'dp', 'ddp', 'ddp2', 'ddp_spawn'
        'num_processes': None,  # number of cpus
        'enable_checkpointing': True,
        'default_root_dir': './',  # root dir to save checkpoints
        'callbacks': [checkpoint_callback],
        'enable_progress_bar': True  # PRD - for production change to False
    },
    'metrics': {  # works with pytorch lightning and will calculate and return the specified metrics.
        'precision': True,
        'accuracy': True,
        'recall': True,
        'f1': True,
        'confusion_matrix': True
    },
    'eval_output': {
        'bucket_path': ''
    }
}

