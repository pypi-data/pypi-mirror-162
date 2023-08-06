# this file is responsible for graph handling of mediapipe
from habana_frameworks.mediapipe.backend.cal import media_manager, pipe_manager
from habana_frameworks.mediapipe.backend.nodes import TensorNode
from habana_frameworks.mediapipe.backend.nodes import opnode_params
from habana_frameworks.mediapipe.operators.media_nodes import MediaConstantNode, MediaDummyNode
from habana_frameworks.mediapipe.operators.media_nodes import MediaReaderNode
from habana_frameworks.mediapipe.operators.media_nodes import MediaFuncDataNode
from habana_frameworks.mediapipe.operators.media_nodes import MediaDecoderNode
from habana_frameworks.mediapipe.operators.media_nodes import MediaHPUNode
from habana_frameworks.mediapipe.operators.media_nodes import MediaCPUNode
from habana_frameworks.mediapipe.operators.media_nodes import CPPNode


class graph_signature(object):
    """
    Class defining hpu graph nodes

    """

    def __init__(self, input_tensors, const_tensors, ops, output_tensors):
        """
        Constructor method.

        """
        self.input_tensors = input_tensors
        self.const_tensors = const_tensors
        self.output_tensors = output_tensors
        self.ops = ops


class graph_processor(object):
    """
    Class defining compile time processing of media nodes.

    """

    def __init__(self, device, output_tensors):
        """
        Constructor method.

        """
        self._device_ = device
        self._output_tensors_ = output_tensors
        self._mm_ = media_manager(self._device_)
        self._ops_ = []
        self._readers_ = []
        self._const_inputs_ = []
        self._func_inputs_ = []
        self._decoders_ = []
        self._hpu_ops_ = []
        self._cpu_ops_ = []
        self._dummy_ops_ = []
        self._cpp_nodes_ = []
        self._dma_ngop_tensors_ = None
        self._is_processed_ = False
        self._is_segmented_ = False
        self._hpu_graph_ = None

        tensors = output_tensors.copy()
        for t in tensors:
            t.dst_op.append(None)
        self._ops_ = []
        # extract list of nodes used in graph
        while tensors:
            tensor_node = tensors.pop(0)
            if(not isinstance(tensor_node, TensorNode)):
                raise ValueError("Got {} instead of TensorNode\n {}".format(
                    type(tensor_node), vars(tensor_node)))
            op_node = tensor_node.src_op
            # let's make it a graph that can be traversed in both ways
            for o in op_node.input_tensors:
                if op_node not in o.dst_op:
                    o.dst_op.append(op_node)
            if op_node is None:
                RuntimeError("node without source")
            if op_node not in self._ops_:
                self._ops_.append(op_node)
            else:
                self._ops_.remove(op_node)
                self._ops_.append(op_node)
            for n in op_node.get_input_tensors():
                tensors.append(n)
        # since graph was constructed bottom up reverse it
        self._ops_.reverse()

    def process_and_validate_graph(self, batch_size):
        """
        Method to process and validate graph node.

        """
        if(self._is_processed_ == True):
            return
        # update pipe specific params and generate output information
        ops = self._ops_
        params = opnode_params(batch_size)
        for op in ops:
            op.generate_node_info(params)
        # since we suppport only one decoder and reader check it here
        media_decoders = self._decoders_
        media_readers = self._readers_
        if(len(media_readers) > 1 or len(media_decoders) > 1):
            raise ValueError("Single decoder and reader supported")
        if(len(media_readers) == 0 or len(media_decoders) == 0):
            raise ValueError("min one decoder and reader supported")
        self._is_processed_ = True

    def segment_graph(self):
        """
        Method to segment graph.

        """
        if(self._is_segmented_ == True):
            return
        for o in self._ops_:
            if isinstance(o, MediaReaderNode):
                self._readers_.append(o)
            elif isinstance(o, MediaConstantNode):
                self._const_inputs_.append(o)
            elif isinstance(o, MediaFuncDataNode):
                self._func_inputs_.append(o)
            elif isinstance(o, MediaDecoderNode):
                self._decoders_.append(o)
            elif isinstance(o, MediaHPUNode):
                self._hpu_ops_.append(o)
            elif isinstance(o, MediaCPUNode):
                self._cpu_ops_.append(o)
                if isinstance(o, CPPNode):
                    self._cpp_nodes_.append(o)
            elif isinstance(o, MediaDummyNode):
                self._dummy_ops_.append(o)
            else:
                raise RuntimeError("invalid operator")
        self._media_graph_ = graph_signature(self._func_inputs_,
                                             self._const_inputs_,
                                             self._ops_,
                                             self._output_tensors_)

        # we currently support reader -> cpu -> hpu -> output only
        # lets check if graph contains same
        for op in self._cpu_ops_:
            out_tensors = op.output_tensors
            for o in out_tensors:
                for d in o.dst_op:
                    if (not ((d == None) or isinstance(d, MediaHPUNode)
                        or isinstance(d, MediaCPUNode)
                             or isinstance(d, MediaDecoderNode))):
                        raise ValueError(
                            "Detect CPU and {} mix up".format(d.__class__.__name__))
        for op in self._hpu_ops_:
            for o in op.output_tensors:
                for d in o.dst_op:
                    if (not ((d == None) or isinstance(d, MediaHPUNode))):
                        raise ValueError(
                            "Detect HPU and {} mix up".format(o.__class__.__name__))

        self._is_segmented_ = True

    def compile(self):
        """
        Method to compile graph.

        """
        hpu_graph = self.get_hpu_graph()
        decoder_op = self.get_decoder_ops()[0]
        self._mm_.compile(decoder_op, hpu_graph)
        return self._mm_.get_recipe()

    def get_cpp_nodes(self):
        """
        Getter method to get metadata processors.
        """
        return self._cpp_nodes_

    def get_recipe(self):
        """
        Getter method to get graph recipe.

        """
        return self._mm_.get_recipe()

    def get_media_graph(self):
        """
        Getter method to get full media graph.

        """
        return self._media_graph_

    def get_hpu_graph(self):
        """
        Getter method to get media graph to be run on hpu.

        """
        if (self._hpu_graph_ != None):
            return self._hpu_graph_
        input_tensors = []
        const_tensors = []
        output_tensors = []
        if(len(self._hpu_ops_) == 0):
            # INFO: no hpu ops present so register dec ouput as in/out
            decoder_op = self.get_decoder_ops()[0]
            input_tensors.append(decoder_op.output_tensors[0])
            output_tensors.append(decoder_op.output_tensors[0])
        else:
            for ho in self._hpu_ops_:
                # INFO: since we have assumned hpu graph to be last part of graph we can safely take this check to get outputs
                for o in ho.output_tensors:
                    for d in o.dst_op:
                        if (d == None):
                            output_tensors.append(o)
                for i in ho.input_tensors:
                    if (not isinstance(i.src_op, MediaHPUNode)):
                        if(isinstance(i.src_op, MediaConstantNode)):
                            const_tensors.append(i)
                        else:
                            input_tensors.append(i)

        self._hpu_graph_ = graph_signature(input_tensors,
                                           const_tensors,
                                           self._hpu_ops_,
                                           output_tensors)
        return self._hpu_graph_

    def get_ops(self):
        """
        Getter method to get list of media ops present in graph.

        """
        return self._ops_

    def get_output_tensors(self):
        """
        Getter method to get list of media output tensors.

        """
        return self._output_tensors_

    def get_reader_ops(self):
        """
        Getter method to get list of media reader nodes.

        """
        return self._readers_

    def get_const_ops(self):
        """
        Getter method to get list of constant nodes.

        """
        return self._const_inputs_

    def get_func_ops(self):
        """
        Getter method to get list of function nodes.

        """
        return self._func_inputs_

    def get_decoder_ops(self):
        """
        Getter method to get list of decoder nodes.

        """
        return self._decoders_

    def get_hpu_ops(self):
        """
        Getter method to get list of hpu nodes.

        """
        return self._hpu_ops_

    def get_cpu_ops(self):
        """
        Getter method to get list of cpu nodes.

        """
        return self._cpu_ops_


class graph_executor(object):
    """
    Class defining runtime time processing of media nodes.

    """

    def __init__(self,
                 graph_processor,
                 queue_depth,
                 img_cwhb,
                 fw_type,
                 proxy,
                 python_proxy):
        """
        Constructor method.

        """
        self._pm_ = pipe_manager(queue_depth,
                                 img_cwhb,
                                 fw_type,
                                 proxy,
                                 python_proxy,
                                 graph_processor.get_output_tensors())
        self._graph_processor_ = graph_processor
        self.hpu_input_tensors = None
        self.hpu_output_tensors = None
        self._exec_ = None
        self._const_exec_ = None
        self._decoder_op_ = self._graph_processor_.get_decoder_ops()[0]
        self._all_output_tensors_ = self._get_all_output_tensors_()
        self._iter_op_ = self._graph_processor_.get_reader_ops()[0]
        self._iter_ = None

        #Register all cpp nodes to cpp backend
        for p in graph_processor.get_cpp_nodes():
            p.add_to_pipeline(self._pm_)

    def start_worker(self):
        """
        Method to start backend worker.

        """
        self._pm_.start_worker()

    def stop_worker(self):
        """
        Method to stop backend worker.

        """
        self._pm_.stop_worker()

    def acquire_device(self, device):
        """
        Method to acquire device.

        """
        self._pm_.acquire_device(device)

    def release_device(self, ):
        """
        Method to release device.

        """
        self._pm_.release_device()

    def initialize_memory(self):
        """
        Method to initialize all backend memory.

        """
        self._pm_.decoder_init(self._graph_processor_.get_decoder_ops()[0])
        hpu_graph = self._graph_processor_.get_hpu_graph()

        self._pm_.media_init(self._graph_processor_.get_recipe(),
                             len(hpu_graph.output_tensors),
                             len(hpu_graph.input_tensors))

        # below api is used to extract data from receipe
        in_tensor_name, out_tensor_name = self._pm_.get_ordered_hpu_input_output_tensor_names()
        # reorder inputs and outputs
        self.hpu_input_tensors, self.hpu_output_tensors = self.get_hpu_graph_reordered_tensors(
            in_tensor_name, out_tensor_name)
        # generate the pipeline's for constants and cpu
        self._const_exec_ = self._generate_const_pipeline_()
        self._exec_ = self._generate_pipeline_()

        self._pm_.initialize_host_buffer()

    def free_memory(self):
        """
        Method to free all backend memory.

        """
        self._pm_.free_host_buffer()
        self._pm_.decoder_deinit()
        self._pm_.media_deinit()

    def get_hpu_graph_reordered_tensors(self, in_tensor_name, out_tensor_name):
        """
        Getter method to get ordered input output nodes as per recipe.

        """
        hpu_graph = self._graph_processor_.get_hpu_graph()
        if(len(in_tensor_name) != len(hpu_graph.input_tensors)):
            raise ValueError("recipe input count {} not matching hpu graph input count {}".format(
                len(in_tensor_name), len(hpu_graph.input_tensors)))

        if(len(out_tensor_name) != len(hpu_graph.output_tensors)):
            raise ValueError("recipe output count {} not matching hpu graph output count {}".format(
                len(in_tensor_name), len(hpu_graph.input_tensors)))

        if(len(out_tensor_name) != 1):
            raise ValueError("only 1 hpu output supported !!")

        hpu_input_tensor_idxs = []
        for in_name in in_tensor_name:
            for i in range(len(hpu_graph.input_tensors)):
                if(in_name == hpu_graph.input_tensors[i].name):
                    hpu_input_tensor_idxs.append(i)
                    break

        if(len(hpu_input_tensor_idxs) != len(in_tensor_name)):
            raise ValueError("recipe input names not matching!!!")
        hpu_input_tensors = []
        for i in range(len(hpu_input_tensor_idxs)):
            hpu_input_tensors.append(hpu_graph.input_tensors[i])
        return hpu_input_tensors, hpu_graph.output_tensors

    def flush_pipeline(self):
        """
        Method to flush pending command in pipe.

        """
        self._pm_.flush_pipeline()
        for t in self._all_output_tensors_:
            t.clear_data()

    def _generate_const_pipeline_(self):
        """
        Method to generate constant node pipeline.

        """
        const_exec = []
        for i in self.hpu_input_tensors:
            if (isinstance(i.src_op, MediaConstantNode)):
                const_exec.append(i.src_op)
        return const_exec

    def _generate_pipeline_(self):
        """
        Method to generate E2E pipeline.

        """
        exec = []
        ops = self._graph_processor_.get_ops()
        for op in ops:
            if (isinstance(op, MediaFuncDataNode)
                    or isinstance(op, MediaCPUNode)
                    or isinstance(op, MediaDummyNode)):
                exec.append(op)
            elif (isinstance(op, MediaConstantNode)):
                for o in op.output_tensors:
                    for d in o.dst_op:
                        if(isinstance(d, MediaFuncDataNode)
                                or isinstance(d, MediaCPUNode)):
                            exec.append(op)

        # INFO: last node is always hpu node running in c as of today
        c_hpu = c_hpu_node("c_hpu0",
                           self._graph_processor_.get_decoder_ops()[0],
                           self.hpu_input_tensors,
                           self._graph_processor_.get_output_tensors(),
                           self._pm_.run_hpu)
        exec.append(c_hpu)
        return exec

    def __generate_cpu_pipeline_(self):
        """
        Method to generate cpu alone pipeline.

        """
        cpu_exec = []
        cpu_ops = self._graph_processor_.get_cpu_ops()
        for op in cpu_ops:
            cpu_exec.append(op)
        return cpu_exec

    def _get_all_output_tensors_(self):
        """
        Method to get output tensors of the pipeline.

        """
        ops = self._graph_processor_.get_ops()
        tensors = []
        for op in ops:
            for o in op.output_tensors:
                tensors.append(o)
        return tensors

    # below are the executors to vall to get execution of nodes
    def initialize_iter_pipeline(self, repeat_count):
        """
        Method to initialize iterator of the pipe.

        """
        self._pm_.init_iterator()
        self._iter_ = iter(self._iter_op_)
        self._iter_repeat_idx_ = 0
        self._iter_repeat_count_ = repeat_count

    def execute_iter_pipeline(self):
        """
        Method to execute iterator.

        """
        try:
            outputs = next(self._iter_)
        except StopIteration:
            # because of queue depth we need to keep breaking here
            self._iter_repeat_idx_ = self._iter_repeat_idx_ + 1
            if(self._iter_repeat_count_ != -1 and self._iter_repeat_idx_ >= self._iter_repeat_count_):
                raise StopIteration
            self._iter_ = iter(self._iter_op_)
            outputs = next(self._iter_)
        self._iter_op_.push_output_buffers(outputs)

    def execute_const_pipeline(self):
        """
        Method to execute constant pipeline.

        """
        for e in self._const_exec_:
            outputs = e()
            e.push_output_buffers(outputs)

    def execute_pipeline(self):
        """
        Method to execute E2E pipeline.

        """
        for e in self._exec_:
            inputs = e.fetch_input_buffers()
            outputs = e(*inputs)
            e.push_output_buffers(outputs)

    def get_output(self):
        return self._pm_.get_output()


# raw hpu node: non standard special op to handle c hpu runs
class c_hpu_node(MediaCPUNode):
    def __init__(self, name, decoder_op, inputs, outputs, run_hpu):
        super().__init__(
            name, "c_hpu0", "", [], {}, {}, None)
        self.populate_output_tensors([])
        self.run_hpu = run_hpu
        self.decoder_op = decoder_op
        self.get_ngops_buf_funcs = []
        for t in outputs[1:]:
            self.get_ngops_buf_funcs.append(t.data_read)

        self.var_buf_funcs = []
        for i in inputs:
            if(not isinstance(i.src_op, MediaDecoderNode)):
                self.var_buf_funcs.append(i.data_read)

    def set_params(self, params):
        pass

    def gen_output_info(self):
        pass

    def fetch_input_buffers(self):
        file_list = self.decoder_op.input_tensors[0].data_read()
        #start_time1 = time.perf_counter()
        if(len(self.decoder_op.input_tensors) > 1):
            rand_crp = self.decoder_op.input_tensors[1].data_read()
        else:
            rand_crp = None

        ngop_np_buf = []
        for f in self.get_ngops_buf_funcs:
            ngop_np_buf.append(f())

        var_np_buf = []
        for f in self.var_buf_funcs:
            var_np_buf.append(f())
        return file_list, rand_crp, var_np_buf, ngop_np_buf

    def push_output_buffers(self, outputs):
        pass

    def __call__(self, file_list, rand_crp, var_np_buf, ngop_np_buf):
        self.run_hpu(file_list, rand_crp, var_np_buf, ngop_np_buf)
        return []
