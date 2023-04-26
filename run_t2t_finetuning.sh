# TOKENIZERS_PARALLELISM=true CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m torch.distributed.launch --nproc_per_node 8 run_t2t_finetuning.py \
#     --model_name_or_path bigscience/bloomz-560m \
#     --do_train \
#     --max_steps 48700 \
#     --logging_strategy steps \
#     --logging_steps 10 \
#     --evaluation_strategy steps \
#     --eval_steps 974 \
#     --save_strategy steps \
#     --save_steps 9740 \
#     --save_total_limit 5 \
#     --output_dir ./save/monolingual/bloomz-560m \
#     --learning_rate 1e-5 \
#     --preprocessing_num_workers 8 \
#     --dataloader_num_workers 8 \
#     --per_device_train_batch_size 4 \
#     --per_device_eval_batch_size 4 \
#     --overwrite_output_dir \
#     --augmentation_type monolingual \
#     --fp16 \
#     --sharded_ddp zero_dp_3 \
#     --report_to tensorboard

# TOKENIZERS_PARALLELISM=true CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m torch.distributed.launch --nproc_per_node 8 run_t2t_finetuning.py \
#     --model_name_or_path bigscience/bloomz-560m \
#     --do_train \
#     --max_steps 48700 \
#     --logging_strategy steps \
#     --logging_steps 10 \
#     --evaluation_strategy steps \
#     --eval_steps 974 \
#     --save_strategy steps \
#     --save_steps 9740 \
#     --save_total_limit 5 \
#     --output_dir ./save/translation/bloomz-560m \
#     --learning_rate 1e-5 \
#     --preprocessing_num_workers 8 \
#     --dataloader_num_workers 8 \
#     --per_device_train_batch_size 4 \
#     --per_device_eval_batch_size 4 \
#     --overwrite_output_dir \
#     --augmentation_type translation \
#     --fp16 \
#     --sharded_ddp zero_dp_3 \
#     --report_to tensorboard

# TOKENIZERS_PARALLELISM=true CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m torch.distributed.launch --nproc_per_node 8 run_t2t_finetuning.py \
#     --model_name_or_path bigscience/bloomz-560m \
#     --do_train \
#     --max_steps 48700 \
#     --logging_strategy steps \
#     --logging_steps 10 \
#     --evaluation_strategy steps \
#     --eval_steps 974 \
#     --save_strategy steps \
#     --save_steps 9740 \
#     --save_total_limit 5 \
#     --output_dir ./save/bilingual/bloomz-560m \
#     --learning_rate 1e-5 \
#     --preprocessing_num_workers 8 \
#     --dataloader_num_workers 8 \
#     --per_device_train_batch_size 4 \
#     --per_device_eval_batch_size 4 \
#     --overwrite_output_dir \
#     --augmentation_type bilingual \
#     --fp16 \
#     --sharded_ddp zero_dp_3 \
#     --report_to tensorboard 

# TOKENIZERS_PARALLELISM=true CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m torch.distributed.launch --nproc_per_node 8 run_t2t_finetuning.py \
#     --model_name_or_path bigscience/bloomz-560m \
#     --do_train \
#     --max_steps 48700 \
#     --logging_strategy steps \
#     --logging_steps 10 \
#     --evaluation_strategy steps \
#     --eval_steps 974 \
#     --save_strategy steps \
#     --save_steps 9740 \
#     --save_total_limit 5 \
#     --output_dir ./save/pair/bloomz-560m \
#     --learning_rate 1e-5 \
#     --preprocessing_num_workers 8 \
#     --dataloader_num_workers 8 \
#     --per_device_train_batch_size 4 \
#     --per_device_eval_batch_size 4 \
#     --overwrite_output_dir \
#     --augmentation_type pair \
#     --fp16 \
#     --sharded_ddp zero_dp_3 \
#     --report_to tensorboard 

# TOKENIZERS_PARALLELISM=true CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m torch.distributed.launch --nproc_per_node 8 run_t2t_finetuning.py \
#     --model_name_or_path bigscience/bloomz-560m \
#     --do_train \
#     --max_steps 48700 \
#     --logging_strategy steps \
#     --logging_steps 10 \
#     --evaluation_strategy steps \
#     --eval_steps 974 \
#     --save_strategy steps \
#     --save_steps 9740 \
#     --save_total_limit 5 \
#     --output_dir ./save/random/bloomz-560m \
#     --learning_rate 1e-5 \
#     --preprocessing_num_workers 8 \
#     --dataloader_num_workers 8 \
#     --per_device_train_batch_size 4 \
#     --per_device_eval_batch_size 4 \
#     --overwrite_output_dir \
#     --augmentation_type random \
#     --fp16 \
#     --sharded_ddp zero_dp_3 \
#     --report_to tensorboard 

TOKENIZERS_PARALLELISM=true CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m torch.distributed.launch --nproc_per_node 8 run_t2t_finetuning.py \
    --model_name_or_path bigscience/bloomz-560m \
    --do_train \
    --max_steps 48700 \
    --logging_strategy steps \
    --logging_steps 10 \
    --evaluation_strategy steps \
    --eval_steps 974 \
    --save_strategy steps \
    --save_steps 9740 \
    --save_total_limit 5 \
    --output_dir ./save/pair/bloomz-560m_R-100 \
    --learning_rate 1e-5 \
    --preprocessing_num_workers 8 \
    --dataloader_num_workers 8 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 4 \
    --overwrite_output_dir \
    --augmentation_type pair \
    --continual_type rehearsal \
    --continual_size 100 \
    --fp16 \
    --sharded_ddp zero_dp_3 \
    --report_to tensorboard 

TOKENIZERS_PARALLELISM=true CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m torch.distributed.launch --nproc_per_node 8 run_t2t_finetuning.py \
    --model_name_or_path bigscience/bloomz-560m \
    --do_train \
    --max_steps 48700 \
    --logging_strategy steps \
    --logging_steps 10 \
    --evaluation_strategy steps \
    --eval_steps 974 \
    --save_strategy steps \
    --save_steps 9740 \
    --save_total_limit 5 \
    --output_dir ./save/pair/bloomz-560m_R-1000 \
    --learning_rate 1e-5 \
    --preprocessing_num_workers 8 \
    --dataloader_num_workers 8 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 4 \
    --overwrite_output_dir \
    --augmentation_type pair \
    --continual_type rehearsal \
    --continual_size 1000 \
    --fp16 \
    --sharded_ddp zero_dp_3 \
    --report_to tensorboard 

TOKENIZERS_PARALLELISM=true CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m torch.distributed.launch --nproc_per_node 8 run_t2t_finetuning.py \
    --model_name_or_path bigscience/bloomz-560m \
    --do_train \
    --max_steps 48700 \
    --logging_strategy steps \
    --logging_steps 10 \
    --evaluation_strategy steps \
    --eval_steps 974 \
    --save_strategy steps \
    --save_steps 9740 \
    --save_total_limit 5 \
    --output_dir ./save/pair/bloomz-560m_R-10000 \
    --learning_rate 1e-5 \
    --preprocessing_num_workers 8 \
    --dataloader_num_workers 8 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 4 \
    --overwrite_output_dir \
    --augmentation_type pair \
    --continual_type rehearsal \
    --continual_size 10000 \
    --fp16 \
    --sharded_ddp zero_dp_3 \
    --report_to tensorboard 