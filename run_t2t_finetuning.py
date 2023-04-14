#!/usr/bin/env python
# coding=utf-8
# Copyright The HuggingFace Team and The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Fine-tuning the library models for sequence to sequence.
"""
# You can also adapt this script on your own sequence to sequence task. Pointers for this are left as comments.

import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Optional
import random

import numpy as np
import pandas as pd

import transformers
from transformers import (
    AutoConfig,
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorWithPadding,
    DataCollatorForLanguageModeling,
    DataCollatorForSeq2Seq,
    HfArgumentParser,
    Trainer,
    TrainingArguments,
    default_data_collator,
    set_seed,
)

from transformers.trainer_utils import get_last_checkpoint
from transformers.utils import check_min_version
from transformers.utils.versions import require_version
import datasets

from data_utils import load_flores_datasets
from augmentation_utils import do_augment
from prompt_utils import prompt_monolingual, prompt_translation, prompt_bilingual

logger = logging.getLogger(__name__)

@dataclass
class ModelArguments:
    """
    Arguments pertaining to which model/config/tokenizer we are going to fine-tune from.
    """
    model_name_or_path: str = field(
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"}
    )
    config_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained config name or path if not the same as model_name"}
    )
    tokenizer_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained tokenizer name or path if not the same as model_name"}
    )
    cache_dir: Optional[str] = field(
        default=None,
        metadata={"help": "Where to store the pretrained models downloaded from huggingface.co"},
    )
    use_fast_tokenizer: bool = field(
        default=True,
        metadata={"help": "Whether to use one of the fast tokenizer (backed by the tokenizers library) or not."},
    )
    model_revision: str = field(
        default="main",
        metadata={"help": "The specific model version to use (can be a branch name, tag name or commit id)."},
    )
    use_auth_token: bool = field(
        default=False,
        metadata={
            "help": (
                "Will use the token generated when running `huggingface-cli login` (necessary to use this script "
                "with private models)."
            )
        },
    )


@dataclass
class DataTrainingArguments:
    """
    Arguments pertaining to what data we are going to input our model for training and eval.
    """
    dataset_name: Optional[str] = field(
        default=None, metadata={"help": "The name of the dataset to use (via the datasets library)."}
    )
    dataset_config_name: Optional[str] = field(
        default=None, metadata={"help": "The configuration name of the dataset to use (via the datasets library)."}
    )
    overwrite_cache: bool = field(
        default=False, metadata={"help": "Overwrite the cached training and evaluation sets"}
    )
    preprocessing_num_workers: Optional[int] = field(
        default=None,
        metadata={"help": "The number of processes to use for the preprocessing."},
    )
    max_source_length: Optional[int] = field(
        default=512,
        metadata={
            "help": (
                "The maximum total input sequence length after tokenization. Sequences longer "
                "than this will be truncated, sequences shorter will be padded."
            )
        },
    )
    max_target_length: Optional[int] = field(
        default=512,
        metadata={
            "help": (
                "The maximum total sequence length for target text after tokenization. Sequences longer "
                "than this will be truncated, sequences shorter will be padded."
            )
        },
    )
    pad_to_max_length: bool = field(
        default=False,
        metadata={
            "help": (
                "Whether to pad all samples to model maximum sentence length. "
                "If False, will pad the samples dynamically when batching to the maximum length in the batch. More "
                "efficient on GPU but very bad for TPU."
            )
        },
    )
    num_beams: Optional[int] = field(
        default=1,
        metadata={
            "help": (
                "Number of beams to use for evaluation. This argument will be passed to ``model.generate``, "
                "which is used during ``evaluate`` and ``predict``."
            )
        },
    )
    ignore_pad_token_for_loss: bool = field(
        default=True,
        metadata={
            "help": "Whether to ignore the tokens corresponding to padded labels in the loss computation or not."
        },
    )
    augmentation_type: str = field(
        default='monolingual',
        metadata={
            "help": "Mode for data augmentation (monolingual / translation / bilingual / random)."
        },
    )

def main():
    # See all possible arguments in src/transformers/training_args.py
    # or by passing the --help flag to this script.
    # We now keep distinct sets of args, for a cleaner separation of concerns.

    parser = HfArgumentParser((ModelArguments, DataTrainingArguments, TrainingArguments))
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        # If we pass only one argument to the script and it's the path to a json file,
        # let's parse it to get our arguments.
        model_args, data_args, training_args = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))
    else:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    if training_args.should_log:
        # The default of training_args.log_level is passive, so we set log level at info here to have that default.
        transformers.utils.logging.set_verbosity_info()

    log_level = training_args.get_process_log_level()
    logger.setLevel(log_level)
    datasets.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.enable_default_handler()
    transformers.utils.logging.enable_explicit_format()

    # Log on each process the small summary:
    logger.warning(
        f"Process rank: {training_args.local_rank}, device: {training_args.device}, n_gpu: {training_args.n_gpu}"
        + f"distributed training: {bool(training_args.local_rank != -1)}, 16-bits training: {training_args.fp16}"
    )
    logger.info(f"Training/evaluation parameters {training_args}")

    # Detecting last checkpoint.
    last_checkpoint = None
    if os.path.isdir(training_args.output_dir) and training_args.do_train and not training_args.overwrite_output_dir:
        last_checkpoint = get_last_checkpoint(training_args.output_dir)
        if last_checkpoint is None and len(os.listdir(training_args.output_dir)) > 0:
            raise ValueError(
                f"Output directory ({training_args.output_dir}) already exists and is not empty. "
                "Use --overwrite_output_dir to overcome."
            )
        elif last_checkpoint is not None and training_args.resume_from_checkpoint is None:
            logger.info(
                f"Checkpoint detected, resuming training at {last_checkpoint}. To avoid this behavior, change "
                "the `--output_dir` or add `--overwrite_output_dir` to train from scratch."
            )

    # Set seed before initializing model.
    set_seed(training_args.seed)

    # Load the datasets
    raw_datasets = load_flores_datasets(pivot_langs=['eng_Latn'])

    # See more about loading any type of standard or custom dataset (from files, python dict, pandas DataFrame, etc) at
    # https://huggingface.co/docs/datasets/loading_datasets.html.
    config = AutoConfig.from_pretrained(
        model_args.config_name if model_args.config_name else model_args.model_name_or_path,
        cache_dir=model_args.cache_dir,
        revision=model_args.model_revision,
        use_auth_token=True if model_args.use_auth_token else None,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
        cache_dir=model_args.cache_dir,
        use_fast=model_args.use_fast_tokenizer,
        revision=model_args.model_revision,
        use_auth_token=True if model_args.use_auth_token else None,
    )
    
    if config.is_encoder_decoder:
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_args.model_name_or_path,
            from_tf=bool(".ckpt" in model_args.model_name_or_path),
            config=config,
            cache_dir=model_args.cache_dir,
            revision=model_args.model_revision,
            use_auth_token=True if model_args.use_auth_token else None,
            # device_map='auto',
            # load_in_8bit=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_args.model_name_or_path,
            from_tf=bool(".ckpt" in model_args.model_name_or_path),
            config=config,
            cache_dir=model_args.cache_dir,
            revision=model_args.model_revision,
            use_auth_token=True if model_args.use_auth_token else None,
            # device_map='auto',
            # load_in_8bit=True
        )

    # Preprocessing the datasets.
    # We need to tokenize inputs and targets.
    column_names = raw_datasets["train"].column_names            
        
    def self_prompt(sent1, sent2, lang1, lang2, is_encoder_decoder, augmentation_type):
        # Random Choice
        if augmentation_type == 'random':
            augmentation_type = random.choice(['monolingual', 'translation', 'bilingual'])
        elif augmentation_type == 'pair':
            augmentation_type = random.choice(['translation', 'bilingual'])
            
        if augmentation_type == 'monolingual':
            rand_proba = random.random()            
            aug_list = None
            if rand_proba < 0.24:
                aug_list = ['infilling']
            elif rand_proba < 0.48:
                aug_list = ['deletion']
            elif rand_proba < 0.72:
                aug_list = ['deletion']
            elif rand_proba < 0.8:
                aug_list = ['infilling', 'deletion']
            elif rand_proba < 0.88:
                aug_list = ['infilling', 'permutation']
            elif rand_proba < 0.96:
                aug_list = ['deletion', 'permutation']
            else: # elif rand_proba < 1.0:            
                aug_list = ['infilling', 'deletion', 'permutation']
            
            # Apply monolingual perturbation
            src_text = sent1
            tgt_text = sent1
            for aug in aug_list:
                src_text = do_augment(src_text, aug)            
            
            # Apply monolingual prompting
            (input_text, output_text) = prompt_monolingual(src_text, tgt_text, lang1, is_encoder_decoder)

        elif augmentation_type == 'translation':
            # Apply translation prompting
            (input_text, output_text) = prompt_translation(sent1, sent2, lang1, lang2, is_encoder_decoder)
            
        elif augmentation_type == 'bilingual':
            rand_proba = random.random()
            aug_list = None
            if rand_proba < 0.24:
                aug_list = ['infilling']
            elif rand_proba < 0.48:
                aug_list = ['deletion']
            elif rand_proba < 0.72:
                aug_list = ['deletion']
            elif rand_proba < 0.8:
                aug_list = ['infilling', 'deletion']
            elif rand_proba < 0.88:
                aug_list = ['infilling', 'permutation']
            elif rand_proba < 0.96:
                aug_list = ['deletion', 'permutation']
            else: # elif rand_proba < 1.0:            
                aug_list = ['infilling', 'deletion', 'permutation']

            # Apply bilingual perturbation
            src_text = sent2
            tgt_text = sent2
            con_text = sent1
            for aug in aug_list:
                src_text = do_augment(src_text, aug)  
                
            # Apply bilingual noisy perturbation
            (input_text, output_text) = prompt_bilingual(src_text, con_text, tgt_text, lang1, lang2, is_encoder_decoder)

        # Return the (input, output) prompt tuple
        return (input_text, output_text)
        
    def preprocess_fn(examples):
        is_encoder_decoder = config.is_encoder_decoder
        augmentation_type = data_args.augmentation_type

        sent1 = [ex for ex in examples["sentence1"]]
        sent2 = [ex for ex in examples["sentence2"]]
        lang1 = [ex for ex in examples["lang1"]]
        lang2 = [ex for ex in examples["lang2"]]
                   
        # Build Prompt
        input_data = []
        for s1, s2, l1, l2 in zip(sent1, sent2, lang1, lang2):
            input_data.append(self_prompt(s1, s2, l1, l2, is_encoder_decoder, augmentation_type))
        
        model_inputs = None
        if is_encoder_decoder:
            inputs, labels = input_data
            model_inputs = tokenizer(inputs, max_length=data_args.max_source_length, padding=False, truncation=True)
            labels = tokenizer(labels, max_length=data_args.max_target_length, padding=False, truncation=True)
            labels["input_ids"] = [
                [(l if l != tokenizer.pad_token_id else -100) for l in label] for label in labels["input_ids"]
            ]
            model_inputs["labels"] = labels["input_ids"]
        else:
            inputs = input_data[0]
            model_inputs = tokenizer(inputs, max_length=data_args.max_source_length, padding=False, truncation=True)
        return model_inputs

    train_dataset = raw_datasets["train"] # .select([i for i in range(100)])
    eval_dataset = raw_datasets["test"] # .select([i for i in range(100)])
            
    train_dataset.set_transform(preprocess_fn)
    eval_dataset.set_transform(preprocess_fn)

    # Initialize our Trainer
    if config.is_encoder_decoder:
        collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model, padding='longest')
    else:
        collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args.remove_unused_columns = False
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset if training_args.do_train else None,
        eval_dataset=eval_dataset if training_args.do_eval else None,
        tokenizer=tokenizer,
        data_collator=collator
    )

    # Training
    if training_args.do_train:
        checkpoint = None
        if training_args.resume_from_checkpoint is not None:
            checkpoint = training_args.resume_from_checkpoint
        elif last_checkpoint is not None:
            checkpoint = last_checkpoint
        train_result = trainer.train(resume_from_checkpoint=checkpoint)
        trainer.save_model()  # Saves the tokenizer too for easy upload

        metrics = train_result.metrics
        metrics["train_samples"] = len(train_dataset)

        trainer.log_metrics("train", metrics)
        trainer.save_metrics("train", metrics)
        trainer.save_state()

    kwargs = {"finetuned_from": model_args.model_name_or_path, "tasks": "instruction-tuning"}
    if data_args.dataset_name is not None:
        kwargs["dataset_tags"] = data_args.dataset_name
        kwargs["dataset"] = data_args.dataset_name

    if training_args.push_to_hub:
        trainer.push_to_hub(**kwargs)
    else:
        trainer.create_model_card(**kwargs)

if __name__ == "__main__":
    main()