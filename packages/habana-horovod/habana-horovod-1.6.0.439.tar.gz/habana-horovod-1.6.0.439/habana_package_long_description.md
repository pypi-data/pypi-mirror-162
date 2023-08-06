Horovod is a distributed training framework for TensorFlow, Keras, PyTorch, and Apache MXNet. The goal of Horovod is to
make distributed Deep Learning fast and easy to use.

This fork enables multi node training on Habana® Gaudi® accelerator with Habana®
TensorFlow bridge only (https://pypi.org/project/habana-tensorflow/).  For more details please refer to
https://docs.habana.ai/en/latest/Tensorflow_Scaling_Guide/TensorFlow_Gaudi_Scaling_Guide.html.

The same as original Horovod project, the package is sdist, containing all sources with Habana modifications for
in place building python Wheel package on customer environment.
