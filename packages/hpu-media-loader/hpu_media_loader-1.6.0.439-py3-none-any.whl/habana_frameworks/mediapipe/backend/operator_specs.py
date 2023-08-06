# File containing class of operator specification

class Operator(object):
    """
    Class defining the media nodes and its specifications.

    """

    def __init__(
            self,
            name,
            guid,
            min_inputs,
            max_inputs,
            num_outputs,
            params,
            cparams,
            op_class,
            dtype):
        """
        Constructor method.

        :params name: node name.
        :params guid: guid of the node.
        :params min_inputs: minimun inputs required by the node.
        :params max_inputs: maximum inputs required by the node.
        :params num_outputs: number of output produced by the node.
        :params params: params dictionary for this node.
        :params cparams: backend params for this node.
        :params op_class: class to which this node belongs to.
        """
        self.__name = name
        self.__min_inputs = min_inputs
        self.__max_inputs = max_inputs
        self.__num_outputs = num_outputs
        self.__params = params
        self.__cparams = cparams
        self.__guid = guid
        self.__op_class = op_class
        self.__dtype = dtype

    def updateparams(self, **kwargs):
        """
        Method to update defualts operator params.

        :params **kwargs: dictionary of params to be updated.
        :returns : updated dictionary of params.
        """
        params = self.__params.copy()
        for key, value in kwargs.items():
            if key in params.keys():
                params[key] = value
            else:
                raise RuntimeError(
                    'param {0} for operator {1} is invalid'.format(
                        key, self.__name))
        return params

    def getGuid(self):
        """
        Getter method to get guid.

        """
        return self.__guid

    def getNumInputs(self):
        """
        Getter method to get number of inputs.

        """
        return self.__min_inputs, self.__max_inputs

    def getMaxInputs(self):
        """
        Getter method to get max inputs.

        """
        return self.__max_inputs

    def getMinInputs(self):
        """
        Getter method to get min inputs.

        """
        return self.__min_inputs

    def getNumOutputs(self):
        """
        Getter method to get num outputs.

        """
        return self.__num_outputs

    def getOpClass(self):
        """
        Getter method to get opcode class.

        """
        return self.__op_class

    def getDtype(self):
        """
        Getter method to get default dtype.

        """
        return self.__dtype

    def getCParams(self):
        """
        Getter method to get cparams.

        """
        return self.__cparams


class operator_schema():
    """
    Call defining default schema for a operator.

    """

    def __init__(self):
        """
        Constructor method.

        """
        self.__ops_list = []
        self.__op_to_obj = {'None': None}

    def add_operator(
            self,
            name,
            guid,
            min_inputs,
            max_inputs,
            num_outputs,
            params,
            cparams,
            op_class,
            dtype):
        """
        Method to add operators

        :params name: operator name
        :params guid: guid of operator
        :params min_inputs: minimum inputs required by operator.
        :params max_inputs: maximum inpus reuired by operator.
        :params num_outputs: numbers of outputs of operator.
        :params params: parameter of the given operator.
        :params cparams: backend parameter of the given operator.
        :params op_class: class to which this oprator belongs to.
        :params dtype: defaults output dtypes of the operator.
        """
        op = Operator(name, guid, min_inputs, max_inputs,
                      num_outputs, params, cparams, op_class, dtype)
        self.__ops_list.append(name)
        if name in self.__op_to_obj.keys():
            raise RuntimeError(
                "{} node already register in operator schema", format(name))
        self.__op_to_obj[name] = op
        setattr(self, name, op)

    def get_operators_list(self):
        """
        Getter method to get operator listin schema.

        """
        return self.__ops_list

    def get_operator_schema(self, operator):
        """
        Getter method to get full schema.

        """
        return self.__op_to_obj[operator]


schema = operator_schema()
