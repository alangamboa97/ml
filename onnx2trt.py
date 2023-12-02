import tensorflow as tf
import tensorflow.contrib.tensorrt as trt

# Cargar el modelo TensorFlow en formato .h5
tf_model = tf.keras.models.load_model("modeloCNN1.h5")

# Crear el optimizador de TensorRT
trt_graph = trt.create_inference_graph(
   input_graph_def=tf.graph_util.convert_variables_to_constants(
       tf.compat.v1.Session().graph.as_graph_def(),
       ["output_tensor"]
   ),
   outputs=["output_tensor"],
   max_batch_size=1,
   max_workspace_size_bytes=1 << 25,
   precision_mode="FP16",  # Puedes ajustar la precisión según tus necesidades
   minimum_segment_size=50
)

# Guardar el grafo optimizado de TensorRT
with open("modelo_optimizado_tensorrt.pb", "wb") as f:
    f.write(trt_graph.SerializeToString())

