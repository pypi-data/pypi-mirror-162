# -*- coding: utf-8 -*-
import os
import paddle


# 基于Paddle-Inference封装的通用Paddle推理器
class PaddlePredict(object):

    def __init__(self, model_path, use_paddle_inference=True, gpu_memory_pool_init_size_mb=100, gpu_device_id=0, cpu_num_threads=1):
        self.use_paddle_inference = use_paddle_inference
        if self.use_paddle_inference:
            if os.path.exists(model_path + '.pdmodel') and os.path.exists(model_path + '.pdiparams'):
                config = paddle.inference.Config(model_path + '.pdmodel', model_path + '.pdiparams')
            elif os.path.exists(model_path + '/__model__'):
                config = paddle.inference.Config(model_path)
            else:
                raise Exception('未找到PaddlePaddle预训练模型数据！')

            if paddle.get_device().startswith('gpu'):
                config.enable_use_gpu(gpu_memory_pool_init_size_mb, gpu_device_id)
            else:
                config.disable_gpu()
                config.set_cpu_math_library_num_threads(cpu_num_threads)
            self.predictor = paddle.inference.create_predictor(config)
            input_names = self.predictor.get_input_names()
            self.input_handle = self.predictor.get_input_handle(input_names[0])
            output_names = self.predictor.get_output_names()
            self.output_handles = []
            for output_name in output_names:
                output_handle = self.predictor.get_output_handle(output_name)
                self.output_handles.append(output_handle)
        else:
            self.model = paddle.jit.load(model_path)
            self.model.eval()

    def predict(self, input_data):
        if self.use_paddle_inference:
            self.input_handle.copy_from_cpu(input_data)
            self.predictor.run()
            output_data = []
            for output_handle in self.output_handles:
                value = output_handle.copy_to_cpu()
                lod = output_handle.lod()
                output_data.append({'value': value, 'lod': lod})
            return output_data
        else:
            input_data = paddle.to_tensor(input_data)
            value = self.model(input_data)
            output_data = [{'value': value}]
            return output_data
